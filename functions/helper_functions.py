'''Helper functions for MCP tools.'''

import logging
import feedparser
from findfeed import search


def get_feed(website_url: str) -> str:
    '''Finds the RSS feed URI for a website given the website's url.
    
    Args:
        website_url: The url for the website to find the RSS feed for
        
    Returns:
        The website's RSS feed URI as a string
    '''

    logger = logging.getLogger(__name__ + '.get_content')

    feeds = search(website_url)

    if len(feeds) > 0:
        return str(feeds[0].url)

    else:
        return f'No feed found for {website_url}'


def parse_feed(feed_uri: str) -> list:
    '''Gets content from a remote RSS feed URI.
    
    Args:
        feed_uri: The RSS feed to get content from

    Returns:
        List of titles for the 10 most recent entries in the RSS feed.
    '''

    logger = logging.getLogger(__name__ + '.parse_feed')

    feed = feedparser.parse(feed_uri)
    logger.info('%s yieled %s entries', feed_uri, len(feed.entries))

    titles = []

    for entry in feed.entries:

        logger.debug('Entry attributes: %s', list(entry.keys()))

        if 'title' in entry:
            titles.append(entry.title)

        if len(titles) >= 10:
            break

    return titles
