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


def load(name: str) -> Tuple[DataFrame, DataFrame]:
    df = pd.read_sql_query("SELECT * from tweet", engine)
    logger.info(f"Loaded df '{name}' of dim {df.shape}")

    urls_dir = Path('data', name, 'urls.txt')
    urls_df = pd.read_table(urls_dir.as_posix(), sep=' ')
    logger.info(f"Loaded urls df '{name}' of dim {urls_df.shape}")

    return df, urls_df


def get_urls(name: str) -> List[str]:
    df = pd.read_sql_query("SELECT * from tweet", engine)
    logger.info(f"Loaded df '{name}' of dim {df.shape}")

    texts = df['text']
    urls = []
    for i in trange(len(texts)):
        urls.extend([url for url in match_url(texts[i])])
    return urls


def resolve_urls(urls: List[str], n_threads=10):
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
    return responses
