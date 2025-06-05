'''Tool functions for MCP server'''

import json
import logging
import functions.feed_extraction as extraction_funcs


def get_feed(website: str) -> list:
    '''Gets RSS feed content from a given website. Can take a website or RSS
    feed URL directly, or the name of a website. Will attempt to find RSS
    feed and return title, summary and link to full article for most recent
    items in feed
    
    Args:
        website: URL or name of website to extract RSS feed content from

    Returns:
        JSON string containing the feed content or 'No feed found' if a RSS
        feed for the requested website could not be found
    '''

    logger = logging.getLogger(__name__ + '.get_content')
    logger.info('Getting feed content for: %s', website)

    feed_uri = extraction_funcs.find_feed_uri(website)
    logger.info('find_feed_uri() returned %s', feed_uri)

    if 'No feed found' in feed_uri:
        return 'No feed found'

    content = extraction_funcs.parse_feed(feed_uri)
    logger.info('parse_feed() returned %s entries', len(list(content.keys())))

    return json.dumps(content)
