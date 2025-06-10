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

# Set-up logging - make sure log directory exists
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
    website_url = gr.Textbox('slashdot', label='Website')
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

    context_search_query = gr.Textbox(
        'How is the air traffic control system being updated?',
        label='Context search query'
    )
    context_search_output = gr.Textbox(
        label='Context search results',
        lines=7,
        max_lines=7
    )

    with gr.Row():
        context_search_submit_button = gr.Button('Submit query')
        context_search_clear_button = gr.ClearButton(
            components=[context_search_query, context_search_output]
        )

    context_search_submit_button.click( # pylint: disable=no-member
        fn=tool_funcs.context_search,
        inputs=context_search_query,
        outputs=context_search_output,
        api_name='Context vector search'
    )


    # Find article tool
    gr.Markdown('### 3. `find_article()`')

    article_search_query = gr.Textbox(
        'How is the air traffic control system being updated?',
        label='Article search query'
    )
    article_search_output = gr.Textbox(
        label='Article search results',
        lines=3,
        max_lines=3
    )

    with gr.Row():
        article_search_submit_button = gr.Button('Submit query')
        article_search_clear_button = gr.ClearButton(
            components=[article_search_query, article_search_output]
        )

    article_search_submit_button.click( # pylint: disable=no-member
        fn=tool_funcs.find_article,
        inputs=article_search_query,
        outputs=article_search_output,
        api_name='Article vector search'
    )


    # Get summary tool
    gr.Markdown('### 4. `get_summary()`')

    article_title = gr.Textbox(
        'FAA To Eliminate Floppy Disks Used In Air Traffic Control Systems',
        label='Article title'
    )
    article_summary = gr.Textbox(
        label='Article summary',
        lines=3,
        max_lines=3
    )

    with gr.Row():
        article_title_submit_button = gr.Button('Submit title')
        article_title_clear_button = gr.ClearButton(
            components=[article_title, article_summary]
        )

    article_title_submit_button.click( # pylint: disable=no-member
        fn=tool_funcs.get_summary,
        inputs=article_title,
        outputs=article_summary,
        api_name='Article summary search'
    )


    # Get link tool
    gr.Markdown('### 5. `get_link()`')

    article_title_link = gr.Textbox(
        'FAA To Eliminate Floppy Disks Used In Air Traffic Control Systems',
        label='Article title'
    )
    article_link = gr.Textbox(
        label='Article link',
        lines=3,
        max_lines=3
    )

    with gr.Row():
        article_link_submit_button = gr.Button('Submit title')
        article_link_clear_button = gr.ClearButton(
            components=[article_title_link, article_link]
        )

    article_link_submit_button.click( # pylint: disable=no-member
        fn=tool_funcs.get_link,
        inputs=article_title_link,
        outputs=article_link,
        api_name='Article link search'
    )


if __name__ == '__main__':

    demo.launch(mcp_server=True)
