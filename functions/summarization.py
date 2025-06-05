'''Functions to summarize article content.'''

import os
import logging

from openai import OpenAI


def summarize_content(content: str) -> str:
    '''Generates summary of article content using Modal inference endpoint.
    
    Args:
        content: string containing the text content to be summarized
        
    Returns:
        Summarized text as string
    '''

    logger = logging.getLogger(__name__ + '.summarize_content')
    logger.info('Summarizing extracted content')

    client = OpenAI(api_key=os.environ['MODAL_API_KEY'])

    client.base_url = (
        'https://gperdrizet--vllm-openai-compatible-summarization-serve.modal.run/v1'
    )

    # Default to first avalible model
    model = client.models.list().data[0]
    model_id = model.id

    # messages = [
    #     {
    #         'role': 'system',
    #         'content': ('You are a research assistant, skilled in summarizing documents in just '+
    #             'a few sentences. Your document summaries should be a maximum of 2 to 4 sentences long.'),
    #         'role': 'user',
    #         'content': content
    #     }
    # ]

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
        return response.choices[0].message.content

    else:
        return None
