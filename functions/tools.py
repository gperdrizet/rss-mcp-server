'''Tool functions for MCP server'''

import logging
from urllib.parse import urlparse
import functions.helper_functions as helper_funcs

FEED_URIS = {}
RSS_EXTENSIONS = ['xml', 'rss', 'atom']
COMMON_EXTENSIONS = ['com', 'net', 'org', 'edu', 'gov', 'co', 'us']


def get_content(website: str) -> list:
    '''Gets RSS feed content from a given website.
    
    Args:
        website_url: URL or nam of website to extract RSS feed content from

    Returns:
        List of titles for the 10 most recent entries in the RSS feed from the
        requested website.
    '''

    logger = logging.getLogger(__name__ + '.get_content')
    logger.info('Getting feed content for: %s', website)

    # Find the feed URI
    feed_uri = None

    # If the website contains xml, rss or atom, assume it's an RSS URI
    if any(extension in website.lower() for extension in RSS_EXTENSIONS):
        feed_uri = website
        logger.info('%s looks like a feed URI already - using it directly', website)

    # Next, check the cache to see if we alreay have this feed's URI
    elif website in FEED_URIS.keys():
        feed_uri = FEED_URIS[website]
        logger.info('%s feed URI in cache: %s', website, feed_uri)

    # If neither of those get it - try feedparse if it looks like a url
    # or else just google it
    else:
        if website.split('.')[-1] in COMMON_EXTENSIONS:
            website_url = website
            logger.info('%s looks like a website URL', website)

        else:
            website_url = helper_funcs.get_url(website)
            logger.info('Google result for %s: %s', website, website_url)

        feed_uri = helper_funcs.get_feed(website_url)
        logger.info('get_feed() returned %s', feed_uri)

        FEED_URIS[website] = feed_uri

    content = helper_funcs.parse_feed(feed_uri)
    logger.info('parse_feed() returned %s', content)

    return '\n'.join(content)
