'''HTML elements for Gradio interface.'''

TITLE = ('''
    <center> 
        <h1>RASS (retrieval augmented simple syndication) MCP server</h1>
        <h2>RSS feed tools for agents</h2>
    </center>
''')

DESCRIPTION = ('''
    **Problem**: I love RSS feeds, but need help keeping up with all of the content from my subscriptions. 
    
    **Solution**: Build a tool to allow LLMs to find and interact with RSS feeds on behalf of the user.
    
    ## Introduction
    
    This space is a MCP server which exposes custom tools to find and interact with
    RSS feed. See 
    [Agentic RSS reader](https://huggingface.co/spaces/gperdrizet/rss-mcp-client) 
    for a demonstration of its use by an agent. Also, check out the 
    [main project repo on GitHub](https://github.com/gperdrizet/MCP-hackathon/tree/main).
    Both Spaces by [George Perdrizet](https://www.linkedin.com/in/gperdrizet)
               
    I love RSS feeds - they remind me of a time when the internet was a weird and
    wonderful place, filled with interesting content hiding behind every link. The tools
    to produce and navigate that content have improved by leaps and bounds. However, 
    the improvement has not come without some losses. Content often feels homogeneous and
    it is too often painfully apparent that your favorite platform has a large degree of
    control over what content you see and what content you don't.

    This tool give the user back some of that control. It let's them decide what content
    and sources they are interested in. I built it because I want access to diverse,
    unfiltered publishing by many sources, paired modern AI to help me navigate it. 
    I want the model to help me ingest my feed, not create it for me!
               
    **Note**: This space is not meant to be used directly. But, for testing and demonstration,
    you can try the tools directly below.

    ## Features

    1. Feeds are found using a combination of [findfeed](https://pypi.org/project/findfeed) and/or Google search with [googlesearch-python](https://pypi.org/project/googlesearch-python/) as needed.
    2. Recent posts from the feed are extracted using [feedparser](https://pypi.org/project/feedparser).
    3. Article content is either taken from the feed if avalible, or pulled from the linked article using [boilerpy3](https://pypi.org/project/boilerpy3/) and good old RegEx, if possible.        
    4. The article content is summarized using [Meta-Llama-3.1-8B-Instruct](https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct) on [Modal](https://modal.com).
    5. Article content is embedded into a vector database on [Upstash](https://upstash.com/) for RAG.
    6. Results are cached to a Redis database on [Upstash](https://upstash.com/) to minimize unnecessary calls to the web crawler/scraper or summarizer.
    
    ## Tools

    1. `get_feed()`: Given a website name or URL, find its RSS feed and
        return recent article titles, links and a generated summary of content if
        avalible. Caches results for fast retrieval by other tools. Embeds content
        to vector database for subsequent RAG.
    2. `context_search()`: Vector search on article content for RAG context.
    3. `find_article()`: Uses vector search on article content to find title of article
        that user is referring to.
    4. `get_summary()`: Gets article summary from Redis cache using article title.
    5. `get_link()`: Gets article link from Redis cache using article title.
''')
