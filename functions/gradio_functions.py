'''Collection of helper functions for Gradio UI and interface.'''

import os
import re


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
