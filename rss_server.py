'''Main script to run gradio interface and MCP server.'''

import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

import gradio as gr
import assets.text as text
import functions.tools as tool_funcs
import functions.gradio_functions as gradio_funcs

# Call the modal container so it spins up before the rest of
# the app starts
gradio_funcs.call_modal()

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
    gr.HTML(text.TITLE)
    gr.Markdown(text.DESCRIPTION)

    # Log output
    with gr.Row():
        dialog_output = gr.Textbox(label='Server logs', lines=7, max_lines=5)

    timer = gr.Timer(0.5, active=True)

    timer.tick( # pylint: disable=no-member
        lambda: gradio_funcs.update_log(), # pylint: disable=unnecessary-lambda
        outputs=dialog_output,
        show_api=False
    )

    # Get feed tool
    gr.Markdown('### 1. `get_feed()`')
    website_url = gr.Textbox('hackernews.com', label='Website')
    feed_output = gr.Textbox(label='RSS entries', lines=7, max_lines=7)

    with gr.Row():
        website_submit_button = gr.Button('Submit website')
        website_clear_button = gr.ClearButton(components=[website_url, feed_output])

    website_submit_button.click( # pylint: disable=no-member
        fn=tool_funcs.get_feed,
        inputs=website_url,
        outputs=feed_output,
        api_name='Get RSS feed content'
    )

    # Vector search tool
    gr.Markdown('### 2. `context_search()`')
    search_query = gr.Textbox('Does apple offer parental controls?', label='Vector search query')
    search_output = gr.Textbox(label='Vector search results', lines=7, max_lines=7)

    with gr.Row():
        search_submit_button = gr.Button('Submit query')
        search_clear_button = gr.ClearButton(components=[search_query, search_output])

    search_submit_button.click( # pylint: disable=no-member
        fn=tool_funcs.context_search,
        inputs=search_query,
        outputs=search_output,
        api_name='Context vector search'
    )


if __name__ == '__main__':

    demo.launch(mcp_server=True)
