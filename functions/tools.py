'''Tool functions for MCP server'''

import time
import json
import logging
import functions.feed_extraction as extraction_funcs
import functions.summarization as summarization_funcs

LOCAL_CACHE = {
    'get_feed': {}
}

def get_feed(website: str, use_cache: bool = True) -> list:
    '''Gets RSS feed content from a given website. Can take a website or RSS
    feed URL directly, or the name of a website. Will attempt to find RSS
    feed and return title, summary and link to full article for most recent
    items in feed
    
    Args:
        website: URL or name of website to extract RSS feed content from
        use_cache: check local cache for content from RSS feed first before
            downloading data from the website's RSS feed 

    Returns:
        JSON string containing the feed content or 'No feed found' if a RSS
        feed for the requested website could not be found
    '''

    start_time = time.time()

    logger = logging.getLogger(__name__ + '.get_feed()')
    logger.info('Getting feed content for: %s', website)

    # Check to see if we have this feed cached, if desired
    if use_cache is True and website in LOCAL_CACHE['get_feed']:
        content = LOCAL_CACHE['get_feed'][website]
        logger.info('Got feed content from local cache')

    else:

        # Find the feed's URI from the website name/URL
        feed_uri = extraction_funcs.find_feed_uri(website)
        logger.info('find_feed_uri() returned %s', feed_uri)

        if 'No feed found' in feed_uri:
            logger.info('Completed in %s seconds', round(time.time()-start_time, 2))
            return 'No feed found'

        # Parse and extract content from the feed
        content = extraction_funcs.parse_feed(feed_uri)
        logger.info('parse_feed() returned %s entries', len(list(content.keys())))

        # Summarize each post in the feed
        for i, item in content.items():

            if item['content'] is not None:
                summary = summarization_funcs.summarize_content(item['content'])
                content[i]['summary'] = summary

            content[i].pop('content', None)

        LOCAL_CACHE['get_feed'][website] = content

    logger.info('Completed in %s seconds', round(time.time()-start_time, 2))

    return json.dumps(content)
