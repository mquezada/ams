import logging
from pathlib import Path
from queue import Queue
from threading import Thread, Lock
from typing import List
import time

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


if __name__ == '__main__':
    import sys

    logging.basicConfig(format='%(asctime)s | %(levelname)s : %(message)s', level=logging.INFO, stream=sys.stdout)

    def resolve_url(url):
        global curr

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


    event_ids = [13472, 15641, 15724, 15749, 15753, 15764, 15778, 15846, 15866, 15943, 15958, 15995, 15996, 16000,
                 16024, 16032, 16034, 16109, 16111, 16145, 16186, 16277, 16292, 16347, 16695, 16700, 16702, 16703,
                 16705, 16729, 16730, 16735, 17140, 17211, 17281, 17533, 17796, 17914, 18469, 18607, 18703, 19115,
                 19119, 19127, 20376, 20415, 20421, 20425, 20441, 20444, 20466, 20556, 20573, 20576, 20582, 20612,
                 20651, 20701, 20702, 20711, 20717, 20841, 20844, 20853, 20985, 20989, 21356, 21358, 21362, 21373,
                 21381, 21495, 21501, 21512, 21514, 21642, 21687, 21733, 21782, 24164, 24165, 24179, 24185, 24198,
                 24311, 24581, 24728, 25106, 25117, 25238, 25263, 25370, 25380, 25387, 25391, 26173, 26177, 26179,
                 27024, 27026, 31659, 31749, 31750, 31753, 31759, 31892, 32033, 32233, 32624, 32699, 36246, 36253,
                 36881, 36882, 36892, 36898, 36899, 36904, 36917, 37042, 37058]

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

    urls = list(set(urls))
    total = len(urls)

    n_threads = 32
    name = 'oscar pistorius'

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
    for _ in range(n_threads):
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
