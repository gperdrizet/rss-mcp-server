'''HTML elements for Gradio interface.'''

TITLE = ('''
    <center> 
        <h1>RSS feed reader</h1>
    </center>
''')

DESCRIPTION = ('''
    RSS feed reader MCP server. See 
    [Agentic RSS reader](https://huggingface.co/spaces/Agents-MCP-Hackathon/rss-mcp-client) 
    for a demonstration. Check out the 
    [main project repo on GitHub](https://github.com/gperdrizet/MCP-hackathon/tree/main)
    . Both Spaces by 
    [George Perdrizet](https://www.linkedin.com/in/gperdrizet)

    This space is not meant to be used directly. It exposes a set of tools to
    interact with RSS feeds for use by agents. For testing and demonstration,
    you can try the tools directly below.

    ## Tools

    1. `get_feed()`: Given a website name or URL, find its RSS feed and
        return recent article titles, links and a generated summary of content if
        avalible. Caches results for fast retrieval by other tools. Embeds content
        to vector database for subsequent RAG.
    2. `context_search()`: Vector search on article content for RAG context.
    3. `find_article()`: Uses vector search on article content to find title of article
        that user is referring to.
    4. `get_summary()`: Gets article summary from Redis cache using article title.

''')
