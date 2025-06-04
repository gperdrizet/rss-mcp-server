'''Tool functions for MCP server'''

import logging
import functions.helper_functions as helper_funcs


def get_content(website_url: str) -> list:
    '''Gets RSS feed content from a given website.
    
    Args:
        website_url: URL of website to extract RSS feed content from

    Returns:
        List of titles for the 10 most recent entries in the RSS feed.
    '''

    logger = logging.getLogger(__name__ + '.get_content')
    logger.info('Getting feed content for: %s', website_url)

    feed_uri = helper_funcs.get_feed(website_url)
    logger.info('get_feed() returned %s', feed_uri)

    content = helper_funcs.parse_feed(feed_uri)
    logger.info('parse_feed() returned %s', content)

    return '\n'.join(content)
