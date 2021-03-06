import models
from typing import List, Tuple, Dict, Any
from pathlib import Path
from tqdm import tqdm, trange
import logging
from pandas.core.frame import DataFrame
from collections import defaultdict
import numpy as np
from union_find import UnionFind
from load_dataset import load
from settings import engine, Datasets


logger = logging.getLogger(__name__)


def add_event(name: str, event: List[int], session):
    """agrega filas a Event dada la info de cada evento seleccionado"""
    with session.begin():
        for id in tqdm(event, desc="add_event"):
            e = models.Event(title=name, event_id=id)
            session.add(e)


def add_urls(name: str, session) -> Dict[str, models.URL]:
    """itera sobre archivo con urls resueltas y agrega filas a URL"""
    path = Path('data', name, 'resolved_urls.txt')
    urls = dict()
    with session.begin():
        with path.open('r') as f:
            lines = f.readlines()
            for line in tqdm(lines, desc="add_urls"):
                short, expanded, title = line.split('\t')
                url = models.URL(short_url=short,
                                 expanded_url=expanded,
                                 title=title)
                urls[short] = url
                session.add(url)
    return urls


def add_tweets_url(name: str, tweets_df: DataFrame, urls: Dict[str, models.URL], session):
    """itera sobre los tweets, saca las URLs y agrega las filas a TweetURL que correspondan."""

    tweet_urls = dict()

    with session.begin():
        for _, tweet in tqdm(tweets_df.iterrows(), total=tweets_df.shape[0], desc="add_tweets_url"):
            matches = match_url(tweet.text)

            for short_url in matches:
                url_obj = urls.get(short_url)
                if url_obj:
                    tweet_url = models.TweetURL(tweet_id=tweet.tweet_id, url_id=url_obj.id)
                    tweet_urls[tweet.tweet_id] = url_obj
                    session.add(tweet_url)
    return tweet_urls


def add_documents(name: str, event_ids: List[int], tweet_urls: Dict[int, models.URL], session):
    uf = UnionFind()

    tweets = session.query(models.Tweet).filter(models.Tweet.event_id_id.in_(event_ids)).all()
    for tweet in tqdm(tweets, desc="Iterating over tweets (create sets)"):
        uf.make_set(tweet.tweet_id)


        url_obj = tweet_urls.get(tweet.tweet_id)
        if url_obj:
            uf.make_set(url_obj.expanded_url)

    for tweet in tqdm(tweets, desc="Iterating over tweets (join sets)"):
        if tweet.in_reply_to_status_id:
            uf.union(tweet.tweet_id, int(tweet.in_reply_to_status_id))
        if tweet.retweet_of_id:
            uf.union(tweet.tweet_id, int(tweet.retweet_of_id))

        url_obj = tweet_urls.get(tweet.tweet_id)
        if url_obj:
            uf.union(tweet.tweet_id, url_obj.expanded_url)

    with session.begin():
        group_doc = dict()
        groups = map(lambda g: str(uf.find(g)), uf.groups)
        for rep in groups:
            document = models.Document(url=rep)
            group_doc[rep] = document

        for tweet in tqdm(tweets, desc="Iterating over tweets (set documents)"):
            id = str(uf.find(tweet.tweet_id))
            doc = group_doc[id]

            tweet.document = doc

    return uf


def get_info(name: str, session, dataset: List[int] = Datasets.oscar_pistorius, limit: int = None):
    with session.begin():
        if limit:
            tweets = session.query(models.Tweet).filter(models.Tweet.event_id_id.in_(dataset)).limit(limit).all()
        else:
            tweets = session.query(models.Tweet).filter(models.Tweet.event_id_id.in_(dataset)).all()

        tweet_ids = []
        replies = 0
        rts = 0

        for tweet in tweets:
            tweet_ids.append(tweet.tweet_id)
            if tweet.in_reply_to_status_id:
                replies += 1
            if tweet.retweet_of_id:
                rts += 1

        set_info = {'replies': replies, 'rts': rts}

        logger.info("get_info (URLs)")

        url_obj = session.query(models.URL, models.TweetURL).\
            filter(models.URL.id == models.TweetURL.url_id).all()
        url_info = dict()
        url_tweet = dict()
        for i in trange(len(url_obj), desc="get_info (url_obj)"):
            m_url, m_tweet_url = url_obj[i]
            url_info[m_tweet_url.tweet_id] = (m_url.short_url, m_url.expanded_url, m_url.title)
        for tweet_id in tqdm(tweet_ids, desc="get_info (join tweets)"):
            info = url_info.get(tweet_id)
            if info:
                url_tweet[tweet_id] = info

        return tweets, url_tweet, set_info


def get_tweets(document_id: int, session):
    with session.begin():
        tweets = session.query(models.Tweet).filter_by(document_id=document_id).all()

        tweet_ids = []
        replies = 0
        rts = 0
        for tweet in tweets:
            tweet_ids.append(tweet.tweet_id)
            if tweet.in_reply_to_status_id:
                replies += 1
            if tweet.retweet_of_id:
                rts += 1

        set_info = {'replies': replies, 'rts': rts}

        url_obj = session.query(models.URL, models.TweetURL). \
            filter(models.URL.id == models.TweetURL.url_id).all()

        url_info = dict()
        url_tweet = dict()

        for i in trange(len(url_obj), desc="get_info (url_obj)"):
            m_url, m_tweet_url = url_obj[i]
            url_info[m_tweet_url.tweet_id] = (m_url.short_url, m_url.expanded_url, m_url.title)

        for tweet_id in tqdm(tweet_ids, desc="get_info (join tweets)"):
            info = url_info.get(tweet_id)
            if info:
                url_tweet[tweet_id] = info

        return tweets, url_tweet, set_info


if __name__ == '__main__':
    from sqlalchemy.orm import sessionmaker
    from settings import engine, Datasets
    from load_dataset import load
    from nlp_utils import match_url
    import sys

    from docopt import docopt

    doc = """set_db
    Usage:
        set_db.py add <event_name>
    """

    args = docopt(doc)

    event_name = args['<event_name>']
    if event_name == 'oscar pistorius':
        dataset = Datasets.oscar_pistorius
    else:
        sys.exit(0)

    logging.basicConfig(format='%(asctime)s | %(levelname)s : %(message)s', level=logging.INFO, stream=sys.stderr)

    Session = sessionmaker(bind=engine, autocommit=True)
    session = Session()

    add_event(event_name, dataset, session)
    url_objs = add_urls(event_name, session)

    df, urls_df = load(event_name, dataset, engine)
    tweet_urls = add_tweets_url(event_name, df, url_objs, session)
    uf = add_documents(event_name, dataset, tweet_urls, session)


def main_info():
    from sqlalchemy.orm import sessionmaker
    import sys
    from settings import engine
    import time

    logging.basicConfig(format='%(asctime)s | %(levelname)s : %(message)s', level=logging.INFO, stream=sys.stderr)

    Session = sessionmaker(bind=engine, autocommit=True, expire_on_commit=False)
    session = Session()

    event_name = 'oscar pistorius'

    t0 = time.time()
    events, tweets, urls = get_info(event_name, session)
    print(time.time() - t0)

    return events, tweets, urls