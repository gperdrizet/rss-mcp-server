'''Main script to run gradio interface and MCP server.'''

import gradio as gr
import assets.html as html
from functions import tools as tool_funcs


with gr.Blocks() as demo:

    with gr.Row():
        gr.HTML(html.TITLE)

    gr.Markdown(html.DESCRIPTION)
    input_word = gr.Textbox('strawberry', label='Text')
    target_letter = gr.Textbox('r', label='Word')
    output = gr.Number(label='Letter count')
    count_button = gr.Button('Count')

    count_button.click( # pylint: disable=no-member
        fn=tool_funcs.letter_counter,
        inputs=[input_word, target_letter],
        outputs=output,
        api_name='letter count'
    )


if __name__ == '__main__':

    demo.launch(mcp_server=True)
