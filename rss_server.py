'''Main script to run gradio interface and MCP server.'''

import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

import gradio as gr
import assets.html as html
from functions import tools as tool_funcs

# Make sure log directory exists
Path('logs').mkdir(parents=True, exist_ok=True)

# Set-up logger
logger = logging.getLogger()

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

logger = logging.getLogger(__name__)


with gr.Blocks() as demo:

    with gr.Row():
        gr.HTML(html.TITLE)

    gr.Markdown(html.DESCRIPTION)
    website_url = gr.Textbox('hackernews.com', label='Website')
    output = gr.Textbox(label='RSS entry titles', lines=10)
    submit_button = gr.Button('Submit')

    submit_button.click( # pylint: disable=no-member
        fn=tool_funcs.get_feed,
        inputs=website_url,
        outputs=output,
        api_name='Get RSS feed content'
    )


if __name__ == '__main__':

    demo.launch(mcp_server=True)
