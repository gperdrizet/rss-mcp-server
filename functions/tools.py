'''Tool functions for MCP server'''

from findfeed import search


def get_feed(url: str) -> str:
    '''Finds the RSS feed URI for a website given the website's url.
    
    Args:
        url: The url for the website to find the RSS feed for
        
    Returns:
        The website's RSS feed URI as a string
    '''

    feeds = search(url)

    if len(feeds) > 0:
        return str(feeds[0].url)

    else:
        return f'No feed found for {url}'
