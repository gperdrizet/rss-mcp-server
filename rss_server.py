'''Main script to run gradio interface and MCP server.'''

import gradio as gr
import assets.html as html
from functions import tools as tool_funcs


with gr.Blocks() as demo:

    with gr.Row():
        gr.HTML(html.TITLE)

    gr.Markdown(html.DESCRIPTION)
    website_url = gr.Textbox('hackernews.com', label='Website URL')
    output = gr.Textbox(label='RSS feed URI')
    submit_button = gr.Button('Submit')

    submit_button.click( # pylint: disable=no-member
        fn=tool_funcs.get_feed,
        inputs=website_url,
        outputs=output,
        api_name='get_feed'
    )


if __name__ == '__main__':

    demo.launch(mcp_server=True)
