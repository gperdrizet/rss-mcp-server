'''Main script to run gradio interface and MCP server.'''

import gradio as gr


def letter_counter(word, letter):
    """
    Count the number of occurrences of a letter in a word or text.

    Args:
        word (str): The input text to search through
        letter (str): The letter to search for

    Returns:
        str: A message indicating how many times the letter appears
    """
    word = word.lower()
    letter = letter.lower()
    count = word.count(letter)
    return count

# demo = gr.Interface(
#     fn=letter_counter,
#     inputs=[gr.Textbox("strawberry"), gr.Textbox("r")],
#     outputs=[gr.Number()],
#     title="Letter Counter",
#     description="Enter text and a letter to count how many times the letter appears in the text."
# )

title=(
    """
        <center> 
            <h1>Letter counter</h1>
        </center>
    """
)



with gr.Blocks() as demo:

    with gr.Row():
        gr.HTML(title)

    gr.Markdown("Enter text and a letter to count how many times the letter appears in the text.")
    word = gr.Textbox("strawberry", label="Text")
    letter = gr.Textbox("r", label='Word')
    output = gr.Number(label='Letter count')
    count_button = gr.Button('Count')

    count_button.click(
        fn=letter_counter,
        inputs=[word, letter],
        outputs=output,
        api_name='letter count'
    )

demo.launch(mcp_server=True)
