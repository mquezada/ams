import logging
import sys
from pathlib import Path
from queue import Queue
from threading import Thread, Lock
from typing import List

import pandas as pd
import requests
from requests.exceptions import TooManyRedirects, ReadTimeout, ConnectTimeout, ConnectionError
from tqdm import trange

from nlp_utils import match_url
from settings import DATA_DIR


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


def unshorten_urls(name: str, dataset: List[int], n_urls=None, n_threads=32):
    logging.basicConfig(format='%(asctime)s | %(levelname)s : %(message)s', level=logging.INFO, stream=sys.stdout)

    def resolve_url(url):
        nonlocal curr

        with lock:
            logger.info(f"URL {curr} of {total}")
            curr += 1

        try:
            resp = requests.head(url, allow_redirects=True, timeout=5)
            if resp and resp.ok:
                return resp.url
        except TooManyRedirects:
            logger.error(f"URL {url} too many redirects")
        except ReadTimeout:
            logger.error(f"URL {url} read timeout")
        except ConnectTimeout:
            logger.error(f"URL {url} connect timeout")
        except ConnectionError:
            logger.error(f"URL {url} connect error")

    def resolve_urls(urls):
        while True:
            url = q.get()
            if url is None:
                q.task_done()
                break
            expanded = resolve_url(url)
            if expanded:
                expanded_urls[url] = expanded
            q.task_done()

    event_ids = dataset

    from settings import engine, engine_m3

    try:
        urls = get_urls(event_ids, engine)
    except:
        urls = get_urls(event_ids, engine_m3)

    q = Queue()
    threads = []
    expanded_urls = dict()
    curr = 1
    lock = Lock()

    if n_urls:
        urls = list(set(urls[:n_urls]))
    else:
        urls = list(set(urls))
    total = len(urls)

    logger.info(f'Spawning {n_threads} threads')
    for _ in range(n_threads):
        t = Thread(target=resolve_urls, args=(urls,))
        t.start()
        threads.append(t)

    logger.info(f"Adding {total} urls to queue")
    for url in urls:
        q.put(url)

    q.join()

    logger.info(f'Done')
    for __ in range(n_threads):
        q.put(None)

    logger.info('Joining threads')
    for t in threads:
        t.join()

    logger.info(f'Saving data...')
    data_path = DATA_DIR / Path(name) / Path('resolved_urls.txt')
    with open(data_path.as_posix(), 'w') as f:
        for short, expanded in expanded_urls.items():
            f.write(f'{short} {expanded}\n')

    logger.info("Exiting main thread")
