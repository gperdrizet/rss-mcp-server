'''Main script to run gradio interface and MCP server.'''

import logging
from functools import partial
from pathlib import Path
from logging.handlers import RotatingFileHandler

import gradio as gr
import assets.html as html
import functions.tools as tool_funcs
import functions.gradio_functions as gradio_funcs


# Set-up logging
# Make sure log directory exists
Path('logs').mkdir(parents=True, exist_ok=True)

# Clear old logs if present
gradio_funcs.delete_old_logs('logs', 'rss_server')

# Set up the root logger so we catch logs from everything
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

# Get a logger
logger = logging.getLogger(__name__)

with gr.Blocks() as demo:

    # Page text
    gr.HTML(html.TITLE)
    gr.HTML(html.DESCRIPTION)

    # Log output
    dialog_output = gr.Textbox(label='Server logs', lines=10, max_lines=100)
    timer = gr.Timer(0.5, active=True)

    timer.tick( # pylint: disable=no-member
        lambda: gradio_funcs.update_log(), # pylint: disable=unnecessary-lambda
        outputs=dialog_output,
        show_api=False
    )

    # Get feed tool
    website_url = gr.Textbox('hackernews.com', label='Website')
    output = gr.Textbox(label='RSS entries', lines=10)
    submit_button = gr.Button('Submit')

    submit_button.click( # pylint: disable=no-member
        fn=tool_funcs.get_feed,
        inputs=website_url,
        outputs=output,
        api_name='Get RSS feed content'
    )


if __name__ == '__main__':

    demo.launch(mcp_server=True)
