'''Collection of helper functions for Gradio UI and interface.'''

import os
import re
import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler


def configure_root_logger() -> None:
    '''Configures root logger for project-wide logging.'''

    # Make sure log directory exists
    Path('logs').mkdir(parents=True, exist_ok=True)

    # Clear old logs if present
    delete_old_logs('logs', 'rss_server')

    # Set up the root logger so we catch logs from
    logging.basicConfig(
        handlers=[RotatingFileHandler(
            'logs/rss_server.log',
            maxBytes=100000,
            backupCount=10,
            mode='w'
        )],
        level=logging.INFO,
        format='%(levelname)s - %(name)s - %(message)s'
    )


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
