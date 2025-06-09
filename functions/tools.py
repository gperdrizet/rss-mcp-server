'''Tool functions for MCP server'''

import os
import threading
import time
import json
import logging
import queue
from upstash_vector import Index, Vector

import functions.feed_extraction as extraction_funcs
import functions.summarization as summarization_funcs
import functions.rag as rag_funcs

RAG_INGEST_QUEUE = queue.Queue()

rag_ingest_thread = threading.Thread(
    target=rag_funcs.ingest,
    args=(RAG_INGEST_QUEUE,)
)

rag_ingest_thread.start()


def get_feed(website: str) -> list:
    '''Gets RSS feed content from a given website. Can take a website or RSS
    feed URL directly, or the name of a website. Will attempt to find RSS
    feed and return title, summary and link to full article for most recent
    items in feed.
    
    Args:
        website: URL or name of website to extract RSS feed content from

    Returns:
        JSON string containing the feed content or 'No feed found' if a RSS
        feed for the requested website could not be found
    '''

    start_time = time.time()

    logger = logging.getLogger(__name__ + '.get_feed()')
    logger.info('Getting feed content for: %s', website)

    # Find the feed's URI from the website name/URL
    feed_uri = extraction_funcs.find_feed_uri(website)
    logger.info('find_feed_uri() returned %s', feed_uri)

    if 'No feed found' in feed_uri:
        logger.info('Completed in %s seconds', round(time.time()-start_time, 2))
        return 'No feed found'

    # Parse and extract content from the feed
    content = extraction_funcs.parse_feed(feed_uri)
    logger.info('parse_feed() returned %s entries', len(list(content.keys())))

    # Summarize each post in the feed and submit full text for RAG ingest
    for i, item in content.items():

        if item['content'] is not None:

            RAG_INGEST_QUEUE.put(item)
            logger.info('%s sent to RAG ingest', item['title'])

            summary = summarization_funcs.summarize_content(
                item['title'],
                item['content']
            )

            content[i]['summary'] = summary
            logger.info('Summary of %s generated', item['title'])

        content[i].pop('content', None)

    logger.info('Completed in %s seconds', round(time.time()-start_time, 2))

    return json.dumps(content)


def context_search(query: str, article_title: str = None) -> str:
    '''Searches for context relevant to query in article vector store.
    
    Ags:
        query: user query to find context for
        article_title: optional, use this argument to search only for context
            from a specific context
            
    Returns:
        Context which bests matches query as string.
    '''

    index = Index(
        url='https://living-whale-89944-us1-vector.upstash.io',
        token=os.environ['UPSTASH_VECTOR_KEY']
    )

    results = None

    results = index.query(
        [query],
        top_k=3,
        namespace=article_title
    )

    return results
