'''HTML elements for Gradio interface.'''

TITLE = (
    '''
        <center> 
            <h1>RSS feed finder/extractor</h1>
        </center>
    '''
)

DESCRIPTION = (
    '''
        Functions to find and extract RSS feeds are complete-ish. No AI 
        yet, plan for tomorrow is to build two tools:

        <ol>
            <li>Human readable summaries of requested RSS feed</li>
            <li>Simple RAG on requested RSS feed content</li>
        </ol>

        For now we just dump the extracted RSS content below. Try asking 
        for a feed by website name, website URL, or entering your favorite
        feed URI directly. Suggestions: http://openai.com/news/rss.xml, 
        hackernews.com, Hugging Face, etc
    '''
)
