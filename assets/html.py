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
        <p>RSS feed reader MCP server. See 
        <a href="https://huggingface.co/spaces/Agents-MCP-Hackathon/rss-mcp-client">
        Agentic RSS reader</a>for a demonstration. Check out the 
        <a href="https://github.com/gperdrizet/MCP-hackathon/tree/main">
        main project repo on GitHub</a>. Both Spaces by 
        <a href="https://www.linkedin.com/in/gperdrizet">George Perdrizet</a>.</p>

        <p>This Space is not meant to be used directly, but you can try out the bare tool below.
        Enter a website name, website URL, or feed URI. The tool will do it's best
        to find the feed and return titles, links and summaries for the three most recent posts.
        Suggestions: http://openai.com/news/rss.xml, hackernews.com, slashdot, etc.</p>

        <h2>Tools</h2>

        <ol>
            <li><b>DONE</b> Given a website name or URL, find its RSS feed and return recent
                article titles, links and a generated summary of content if avalible</li>
            <li><b>TODO</b> Simple RAG on requested RSS feed content</li>
        </ol>
    '''
)
