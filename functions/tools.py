'''Tool functions for MCP server'''

import json
import logging
import functions.helper_functions as helper_funcs


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

    feed_uri = helper_funcs.find_feed_uri(website)
    logger.info('find_feed_uri() returned %s', feed_uri)

    if 'No feed found' in feed_uri:
        return 'No feed found'

    content = helper_funcs.parse_feed(feed_uri)
    logger.info('parse_feed() returned %s entries', len(list(content.keys())))

    return json.dumps(content)
