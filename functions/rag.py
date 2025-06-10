'''Collection of function for RAG on article texts.'''

import os
import logging
import queue
from semantic_text_splitter import TextSplitter
from tokenizers import Tokenizer
from upstash_vector import Index


def ingest(rag_ingest_queue: queue.Queue) -> None:
    '''Semantically chunks article and upsert to Upstash vector db
    using article title as namespace.'''

    logger = logging.getLogger(__name__ + '.ingest()')

    index = Index(
        url='https://living-whale-89944-us1-vector.upstash.io',
        token=os.environ['UPSTASH_VECTOR_KEY']
    )

    while True:

        namespaces = index.list_namespaces()

        item = rag_ingest_queue.get()
        logger.info('Upserting "%s": %s', item['title'], item)
        title = item['title']

        if title not in namespaces:
            text = item['content']
            logger.info('Got "%s" from RAG ingest queue', title)

            tokenizer=Tokenizer.from_pretrained('bert-base-uncased')
            splitter=TextSplitter.from_huggingface_tokenizer(tokenizer, 256)
            chunks=splitter.chunks(text)

            for i, chunk in enumerate(chunks):

                index.upsert(
                    [
                        (
                            hash(f'{title}-{i}'),
                            chunk,
                            {'namespace': title}
                        )
                    ],
                )
            logger.info('Ingested %s chunks into vector DB', i + 1)

        else:
            logger.info('%s already in RAG namespace', title)
