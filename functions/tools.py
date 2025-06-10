'''Tool functions for MCP server'''

import os
import threading
import time
import json
import logging
import queue
from typing import Tuple
from upstash_vector import Index
from upstash_redis import Redis

import functions.feed_extraction as extraction_funcs
import functions.summarization as summarization_funcs
import functions.rag as rag_funcs

RAG_INGEST_QUEUE = queue.Queue()

rag_ingest_thread = threading.Thread(
    target=rag_funcs.ingest,
    args=(RAG_INGEST_QUEUE,)
)

rag_ingest_thread.start()


def get_feed(website: str, n: int = 3) -> list:
    '''Gets RSS feed content from a given website. Can take a website or RSS
    feed URL directly, or the name of a website. Will attempt to find RSS
    feed and return title, summary and link to full article for most recent
    n items in feed. This function is slow and resource heavy, only call it when
    the user wants to check a feed for new content, or asks for content from a
    feed that you have not retrieved yet.
    
    Args:
        website: URL or name of website to extract RSS feed content from
        n: (optional) number of articles to parse from feed, defaults to 3

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
    articles = extraction_funcs.parse_feed(feed_uri, n)
    logger.info('parse_feed() returned %s entries', len(list(articles.keys())))

    # Loop on the posts, sending them to RAG (nonblocking) and summarization (blocking)
    for i, item in articles.items():

        # Check if content is present
        if item['content'] is not None:
            logger.info('Summarizing/RAG ingesting: %s', item)

            # Send to RAG ingest
            RAG_INGEST_QUEUE.put(item.copy())
            logger.info('"%s" sent to RAG ingest', item['title'])

            # Generate summary and add to content
            summary = summarization_funcs.summarize_content(
                item['title'],
                item['content']
            )

            articles[i]['summary'] = summary
            logger.info('Summary of "%s" generated', item['title'])

        # Remove full-text content before returning
        articles[i].pop('content', None)

    logger.info('Completed in %s seconds', round(time.time()-start_time, 2))

    # Return content dictionary as string
    return json.dumps(articles)


def context_search(query: str, article_title: str = None) -> list[Tuple[float, str]]:
    '''Searches for context relevant to query. Use this Function to search 
    for additional general information if needed before answering the user's question 
    about an article. If article_title is provided the search will only return 
    results from that article. If article_title is omitted, the search will 
    include all articles currently in the cache. 
    
    Ags:
        query: user query to find context for
        article_title: optional, use this argument to search only for 
        context from a specific article, defaults to None
            
    Returns:
        Text relevant to the query
    '''

    logger = logging.getLogger(__name__ + 'context_search')

    index = Index(
        url='https://living-whale-89944-us1-vector.upstash.io',
        token=os.environ['UPSTASH_VECTOR_KEY']
    )

    results = None

    results = index.query(
        data=query,
        top_k=3,
        include_data=True,
        namespace=article_title
    )

    logger.info('Retrieved %s chunks for "%s"', len(results), query)

    return results[0].data


def find_article(query: str) -> list[Tuple[float, str]]:
    '''Uses vector search to find the most likely title of the article 
    referred to by query. Use this function if the user is asking about
    an article, but it is not clear what the exact title of the article is.
    
    Args:
        query: query to to find source article tile for
        
    Returns:
        Article title
    '''

    logger = logging.getLogger(__name__ + 'context_search')

    index = Index(
        url='https://living-whale-89944-us1-vector.upstash.io',
        token=os.environ['UPSTASH_VECTOR_KEY']
    )

    results = None

    results = index.query(
        data=query,
        top_k=3,
        include_metadata=True,
        include_data=True
    )

    logger.info('Retrieved %s chunks for "%s"', len(results), query)

    return results[0].metadata['namespace']


def get_summary(title: str) -> str:
    '''Uses article title to retrieve summary of article content.
    
    Args:
        title: exact title of article

    Returns:
        Short summary of article content.
    '''

    logger = logging.getLogger(__name__ + '.get_summary()')

    redis = Redis(
        url='https://sensible-midge-19304.upstash.io',
        token=os.environ['UPSTASH_REDIS_KEY']
    )

    cache_key = f'{title} summary'
    summary = redis.get(cache_key)

    if summary:

        logger.info('Got summary for "%s": %s', title, summary[:100])
        return summary

    logger.info('Could not find summary for: "%s"', title)
    return f'No article called "{title}". Make sure you have the correct title.'


def get_link(title: str) -> str:
    '''Uses article title to look up direct link to article content webpage.
    
    Args:
        title: exact title of article

    Returns:
        Article webpage URL.
    '''

    logger = logging.getLogger(__name__ + '.get_link()')

    redis = Redis(
        url='https://sensible-midge-19304.upstash.io',
        token=os.environ['UPSTASH_REDIS_KEY']
    )

    cache_key = f'{title} link'
    link = redis.get(cache_key)

    if link:

        logger.info('Got link for "%s": %s', title, link)
        return link

    logger.info('Could not find link for: "%s"', title)
    return f'No article called "{title}". Make sure you have the correct title.'
