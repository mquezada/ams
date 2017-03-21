import pandas as pd
from pandas.core.frame import DataFrame
from pathlib import Path
import logging
from typing import Tuple, List
from sqlalchemy import create_engine
from tqdm import trange
from nlp_utils import match_url


logger = logging.getLogger('Load')
engine = create_engine('mysql://root@127.0.0.1/ams')
engine_m3 = create_engine('mysql://mquezada:phoophoh7ahdaiJahphoh3aicooz7uka3ahJe9oi@127.0.0.1/mquezada_db')

DATA_DIR = Path('data')


def load(name: str, engine) -> Tuple[DataFrame, DataFrame]:
    df = pd.read_sql_query("SELECT * from tweet", engine)
    logger.info(f"Loaded df '{name}' of dim {df.shape}")

    urls_dir = Path('data', name, 'urls.txt')
    urls_df = pd.read_table(urls_dir.as_posix(), sep=' ')
    logger.info(f"Loaded urls df '{name}' of dim {urls_df.shape}")

    return df, urls_df


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


def resolve_urls(name: str, urls: List[str], n_threads=10):
    import grequests
    i = 1

    def task(url):
        nonlocal i
        prog = 100 * i / len(urls)
        logger.info(f"Processing url {i} of {len(urls)} ({prog:.2f}%): {url}")
        i += 1
        return grequests.head(url, allow_redirects=True)

    reqs = (task(u) for u in urls)
    responses = grequests.map(reqs, size=n_threads)

    path = DATA_DIR / Path(name) / Path('resolved_urls.txt')

    with open(path.as_posix(), 'w') as f:
        for url, response in zip(urls, responses):
            if response.ok:
                f.write(f'{url} {response.url}\n')

    return responses
