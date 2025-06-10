'''Tool functions for MCP server'''

import os
import threading
import time
import json
import logging
import queue
from typing import Tuple
from upstash_vector import Index

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
    n items in feed. This function is slow a resource heavy, only call it when
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
    '''Searches for context relevant to query in article vector store. 
    Use this Function to search for additional information before 
    answering the user's question about an article. If article_title is
    provided the search will only return results from that article. If
    article_title is omitted, the search will include all articles
    currently in the cache. 
    
    Ags:
        query: user query to find context for
        article_title: optional, use this argument to search only for 
        context from a specific context, defaults to None
            
    Returns:
        List of tuples with the following format: [(relevance score, 'context string')]
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

    contexts = []

    for result in results:
        contexts.append((result.score, result.data))

    return contexts


def find_article(query: str) -> list[Tuple[float, str]]:
    '''Uses vector search to find the most likely title of the article 
    referred to by query. Use this function if the user is asking about
    and article, but it is unclear which article.
    
    Args:
        query: query to to find source article for
        
    Returns:
        List of tuples of most likely context article titles in the following format:
        [(relevance score, 'article title')]
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

    contexts = []

    for result in results:
        contexts.append((result.score, result.metadata['namespace']))

    return contexts
