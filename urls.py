import pandas as pd
from tqdm import trange
from nlp_utils import match_url
from typing import List
import logging
from pathlib import Path
from settings import DATA_DIR
from threading import Thread, Lock
import requests
import time
from queue import Queue


logger = logging.getLogger(__name__)


def get_urls(event_ids: List[int], engine) -> List[str]:
    query = "SELECT * from tweet where event_id_id in ({})"
    query = query.format(','.join(map(str, event_ids)))

    df = pd.read_sql_query(query, engine)
    logger.info(f"Loaded df of dim {df.shape}")

    texts = df['text']
    urls = []
    for i in trange(len(texts)):
        urls.extend([url for url in match_url(texts[i])])
    return urls


def resolve_urls(urls: List[str], name: str, n_threads=10):
    class URLResolver(Thread):
        def __init__(self, queue, expanded_urls, lock, session):
            Thread.__init__(self)
            self.expanded_urls = expanded_urls
            self.lock = lock
            self.session = session
            self.queue = queue

        def run(self):
            nonlocal exitFlag
            nonlocal curr
            while not exitFlag:
                url = None
                with self.lock:
                    if not self.queue.empty():
                        url = self.queue.get()
                        logger.info(f'URL {curr} of {total}: {url}')
                        curr += 1
                if url:
                    resp = self.session.head(url, allow_redirects=True)
                    if resp and resp.ok:
                        self.expanded_urls[url] = resp.url

    exitFlag = False
    lock = Lock()
    q = Queue()
    session = requests.session()
    expanded_urls = dict()
    total = len(urls)
    curr = 1

    threads = []

    with lock:
        logger.info(f'Putting {total} urls into queue')
        for url in urls:
            q.put(url)

    logger.info(f'Spawning {n_threads} threads')
    for _ in range(n_threads):
        ur = URLResolver(q, expanded_urls, lock, session)
        ur.start()
        threads.append(ur)

    while not q.empty():
        time.sleep(5)

    logger.info(f'Done')
    exitFlag = True

    for t in threads:
        t.join()

    logger.info(f'Saving data...')
    data_path = DATA_DIR / Path(name) / Path('resolved_urls.txt')
    with open(data_path.as_posix(), 'w') as f:
        for short, expanded in expanded_urls.items():
            f.write(f'{short} {expanded}\n')

    logger.info("Exiting main thread")
    return expanded_urls
