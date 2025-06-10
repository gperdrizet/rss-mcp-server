'''Collection of helper functions for Gradio UI and interface.'''

import os
import re
import logging

from openai import OpenAI

def call_modal() -> None:
    '''Sends request to Modal to spin up container'''

    logger = logging.getLogger(__name__ + '.call_modal()')

    # Call the modal container so it spins up
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
            'content': ('Interpret the following proverb in 50 words or less: ' +
                'A poor craftsman blames the eye of the beholder')
        }
    ]

    logger.info('Prompt: %s', messages[0]['content'])

    completion_args = {
        'model': model_id,
        'messages': messages,
    }

    try:
        response = client.chat.completions.create(**completion_args)

    except Exception as e: # pylint: disable=broad-exception-caught
        response = None
        logger.error('Error during Modal API call: %s', e)

    if response is not None:
        reply = response.choices[0].message.content

    else:
        reply = None

    logger.info('Reply: %s', reply)


def update_log(n: int = 10):
    '''Gets updated logging output from disk to display to user.
    
    Args:
        n: number of most recent lines of log output to display

    Returns:
        Logging output as string
    '''

    with open('logs/rss_server.log', 'r', encoding='utf-8') as log_file:
        lines = log_file.readlines()

    return ''.join(lines[-n:])


def delete_old_logs(directory:str, basename:str) -> None:
    '''Deletes old log files from previous optimization sessions, if present.
    
    Args:
        directory: path to log file directory as string
        basename: log file base name as string
        
    Returns:
        None
    '''

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if re.search(basename, filename):
            os.remove(file_path)
