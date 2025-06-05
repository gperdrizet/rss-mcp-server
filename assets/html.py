'''HTML elements for Gradio interface.'''

TITLE = (
    '''
        <center> 
            <h1>RSS feed reader</h1>
        </center>
    '''
)

DESCRIPTION = (
    '''
        Functions to find, extract and summarize RSS feeds are complete.

        <h2>Tools</h2>

        <ol>
            <li><b>DONE</b> Given a website name or URL, find its RSS feed and return recent
                article titles, links and a generated summary of content if avalible</li>
            <li><b>TODO</b> Simple RAG on requested RSS feed content</li>
        </ol>

        For now, we dump the extracted RSS title, link and summary below. Try asking for a 
        feed by website name, website URL, or entering your favorite feed URI directly.
        Suggestions: http://openai.com/news/rss.xml, hackernews.com, Hugging Face, etc
    '''
)
