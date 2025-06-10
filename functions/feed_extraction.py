'''Helper functions for MCP tools.'''

import os
import re
import logging
import urllib.request
from urllib.error import HTTPError, URLError

import feedparser
from boilerpy3 import extractors
from boilerpy3.exceptions import HTMLExtractionError
from findfeed import search as feed_search
from googlesearch import search as google_search
from upstash_redis import Redis

FEED_URIS = {}
RSS_EXTENSIONS = ['xml', 'rss', 'atom']
COMMON_EXTENSIONS = ['com', 'net', 'org', 'edu', 'gov', 'co', 'us']
REDIS = Redis(
    url='https://sensible-midge-19304.upstash.io',
    token=os.environ['UPSTASH_REDIS_KEY']
)

def find_feed_uri(website: str) -> str:
    '''Attempts to find URI for RSS feed. First checks if string provided in
    website is a feed URI, it it's not, checks if website is a URL, if so,
    uses that to find the RSS feed URI. If the provided string is neither,
    defaults to Google search to find website URL and then uses that to try
    and find the Feed.

    Args:
        website: target resource to find RSS feed URI for, can be website URL or
        name of website

    Returns:
        RSS feed URI for website
    '''

    logger = logging.getLogger(__name__ + '.find_feed_uri')
    logger.info('Finding feed URI for %s', website)

    # Find the feed URI
    feed_uri = None

    # If the website contains xml, rss or atom, assume it's an RSS URI
    if any(extension in website.lower() for extension in RSS_EXTENSIONS):
        feed_uri = website
        logger.info('%s looks like a feed URI already - using it directly', website)

    # Next, check the cache to see if we already have this feed's URI locally
    elif website in FEED_URIS:
        feed_uri = FEED_URIS[website]
        logger.info('%s feed URI in local cache: %s', website, feed_uri)

    # If we still haven't found it, check to see if the URI is in the Redis cache
    cache_key = f'{website} feed uri'
    cache_hit = False

    if feed_uri is None:
        cached_uri = REDIS.get(cache_key)

        if cached_uri:
            cache_hit = True
            feed_uri = cached_uri
            logger.info('%s feed URI in Redis cache: %s', website, feed_uri)

    # If still none of those methods get it - try feedparse if it looks like a url
    # or else just google it
    if feed_uri is None:
        if website.split('.')[-1] in COMMON_EXTENSIONS:
            website_url = website
            logger.info('%s looks like a website URL', website)

        else:
            website_url = _get_url(website)
            logger.info('Google result for %s: %s', website, website_url)

        feed_uri = _get_feed(website_url)
        logger.info('get_feed() returned %s', feed_uri)

        # Add to local cache
        FEED_URIS[website] = feed_uri

    # Add the feed URI to the redis cache if it wasn't already there
    if cache_hit is False:
        REDIS.set(cache_key, feed_uri)

    return feed_uri


def parse_feed(feed_uri: str, n: int) -> list:
    '''Gets content from a remote RSS feed URI.
    
    Args:
        feed_uri: The RSS feed to get content from
        n: the number of feed entries to parse

    Returns:
        List of dictionaries for the n most recent entries in the RSS feed.
        Each dictionary contains 'title', 'link' and 'content' keys.
    '''

    logger = logging.getLogger(__name__ + '.parse_feed')

    feed = feedparser.parse(feed_uri)
    logger.info('%s yielded %s entries', feed_uri, len(feed.entries))

    entries = {}

    for i, entry in enumerate(feed.entries):

        entry_content = {}

        if 'title' in entry and 'link' in entry:

            title = entry.title
            entry_content['title'] = title

            # Check the Redis cache
            cached_link = REDIS.get(f'{title} link')

            if cached_link:
                logger.info('Entry in Redis cache: "%s"', title)
                entry_content['link'] = cached_link
                entry_content['content'] = REDIS.get(f'{title} content')

            # If its not in the Redis cache, parse it from the feed data
            else:
                entry_content['title'] = entry.title
                entry_content['link'] = entry.link
                entry_content['content'] = None

                # Grab the article content from the feed, if provided
                if 'content' in entry:
                    entry_content['content'] = entry.content

                # If not, try to get the article content from the link
                elif entry_content['content'] is None:

                    html = _get_html(entry_content['link'])
                    content = _get_text(html)
                    entry_content['content'] = content

                # Add everything to the cache
                REDIS.set(f'{title} link', entry_content['link'])
                REDIS.set(f'{title} content', entry_content['content'])

                logger.info('Parsed entry: "%s"', title)

        entries[i] = entry_content

        if i == n-1:
            break

    logger.info('Entries contains %s elements', len(list(entries.keys())))

    return entries


def _get_url(company_name: str) -> str:
    '''Finds the website associated with the name of a company or
    publication.

    Args:
        company_name: the name of the company, publication or site to find
        the URL for

    Returns:
        The URL for the company, publication or website.
    '''

    logger = logging.getLogger(__name__ + '.get_url')
    logger.info('Getting website URL for %s', company_name)

    query = f'{company_name} official website'

    for url in google_search(query, num_results=5):
        if 'facebook' not in url and 'linkedin' not in url:
            return url

    return None


def _get_feed(website_url: str) -> str:
    '''Finds the RSS feed URI for a website given the website's url.
    
    Args:
        website_url: The url for the website to find the RSS feed for
        
    Returns:
        The website's RSS feed URI as a string
    '''

    logger = logging.getLogger(__name__ + '.get_content')
    logger.info('Getting feed URI for: %s', website_url)

    feeds = feed_search(website_url)

    if len(feeds) > 0:
        return str(feeds[0].url)

    else:
        return f'No feed found for {website_url}'


def _get_html(url: str) -> str:
    '''Gets HTML string content from url
    
    Args:
        url: the webpage to extract content from

    Returns:
        Webpage HTML source as string
    '''

    header={
        "Accept": ("text/html,application/xhtml+xml,application/xml;q=0.9,image/avif," +
                   "image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"),
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive",
        "Sec-Fetch-Site": "cross-site",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" +
                       "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
    }

    # Create the request with header
    request_params = urllib.request.Request(
        url=url,
        headers=header
    )

    # Get the html string
    try:
        with urllib.request.urlopen(request_params) as response:
            status_code = response.getcode()

            if status_code == 200:
                content = response.read()
                encoding = response.headers.get_content_charset()

                if encoding is None:
                    encoding = "utf-8"

                content = content.decode(encoding)

            else:
                content = None

    except HTTPError:
        content = None

    except URLError:
        content = None

    return content


def _get_text(html: str) -> str:
    '''Uses boilerpy3 extractor and regex cribbed from old NLTK clean_html
    function to try and extract text from HTML as cleanly as possible.
    
    Args:
        html: the HTML string to be cleaned
        
    Returns:
        Cleaned text string'''

    if html is None:
        return None

    extractor = extractors.ArticleExtractor()

    try:
        html = extractor.get_content(html)

    except HTMLExtractionError:
        pass

    except AttributeError:
        pass

    except TypeError:
        pass

    return _clean_html(html)


def _clean_html(html: str) -> str:
    '''
    Remove HTML markup from the given string. 

    Args:
        html: the HTML string to be cleaned

    Returns:
        Cleaned string
    '''

    if html is None:
        return None

    # First we remove inline JavaScript/CSS:
    cleaned = re.sub(r"(?is)<(script|style).*?>.*?(</\1>)", "", html.strip())

    # Then we remove html comments. This has to be done before removing regular
    # tags since comments can contain '>' characters.
    cleaned = re.sub(r"(?s)<!--(.*?)-->[\n]?", "", cleaned)

    # Next we can remove the remaining tags:
    cleaned = re.sub(r"(?s)<.*?>", " ", cleaned)


    # Finally, we deal with whitespace
    cleaned = re.sub(r"&nbsp;", " ", cleaned)
    cleaned = re.sub(r"  ", " ", cleaned)
    cleaned = re.sub(r"  ", " ", cleaned)

    return cleaned.strip()
