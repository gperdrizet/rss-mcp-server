'''Functions to summarize article content.'''

import os
import logging

from openai import OpenAI
from upstash_redis import Redis

REDIS = Redis(
    url='https://sensible-midge-19304.upstash.io',
    token=os.environ['UPSTASH_REDIS_KEY']
)

def summarize_content(title: str, content: str) -> str:
    '''Generates summary of article content using Modal inference endpoint.
    
    Args:
        content: string containing the text content to be summarized
        
    Returns:
        Summarized text as string
    '''

    logger = logging.getLogger(__name__ + '.summarize_content')
    logger.info('Summarizing extracted content')

    # Check Redis cache for summary
    cache_key = f'{title} summary'
    cached_summary = REDIS.get(cache_key)

    if cached_summary:
        logger.info('Got summary from Redis cache: "%s"', title)
        return cached_summary

    # It the summary is not in the cache, generate it
    client = OpenAI(api_key=os.environ['MODAL_API_KEY'])

    client.base_url = (
        'https://gperdrizet--vllm-openai-compatible-summarization-serve.modal.run/v1'
    )

    # Default to first avalible model
    model = client.models.list().data[0]
    model_id = model.id

    messages = [
        {
            'role': 'system',
            'content': f'Summarize the following text in 50 words returning only the summary: {content}'
        }
    ]

    completion_args = {
        'model': model_id,
        'messages': messages,
        # "frequency_penalty": args.frequency_penalty,
        # "max_tokens": 128,
        # "n": args.n,
        # "presence_penalty": args.presence_penalty,
        # "seed": args.seed,
        # "stop": args.stop,
        # "stream": args.stream,
        # "temperature": args.temperature,
        # "top_p": args.top_p,
    }

    try:
        response = client.chat.completions.create(**completion_args)

    except Exception as e: # pylint: disable=broad-exception-caught
        response = None
        logger.error('Error during Modal API call: %s', e)

    if response is not None:
        summary = response.choices[0].message.content

    else:
        summary = None

    # Add the new summary to the cache
    REDIS.set(cache_key, summary)
    logger.info('Summarized: "%s"', title)

    return summary
