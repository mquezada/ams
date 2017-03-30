from pandas.core.frame import DataFrame
from tqdm import tqdm
from collections import defaultdict

import logging
import nlp_utils
from load_dataset import load
from settings import engine, Datasets
from create_tfidf import create_matrix
from set_db import


logger = logging.getLogger(__name__)


def create_documents(tweets_df: DataFrame,
                     urls_df: DataFrame,
                     ignore_unresolved: bool = False,
                     include_no_url_tweets: bool = False,
                     contents: str = "ids"):

    assert contents in ("ids", "texts")

    urls_dict = dict()
    for _, row in tqdm(urls_df.iterrows(), desc="Creating URLs dict", total=urls_df.shape[0]):
        urls_dict[row['tweet_url']] = row['expanded_url']

    documents = defaultdict(list)

    for _, row in tqdm(tweets_df.iterrows(), desc="Creating documents", total=tweets_df.shape[0]):
        text = row['text']

        if contents == "ids":
            t_id = row['tweet_id']
        else:
            t_id = row['text']

        matches = nlp_utils.match_url(text)
        for match in matches:
            expanded_url = urls_dict.get(match, None)

            if ignore_unresolved and expanded_url is None:
                continue

            documents[expanded_url].append(t_id)

        if include_no_url_tweets and not matches:
            documents[_].append(t_id)

    logger.info(f'Total {len(documents)} documents.')
    return documents


def info_for_distance():
    tweets_df, _ = load('oscar pistorius', Datasets.oscar_pistorius, engine)
    m = create_matrix(tweets_df)

    doc = {}
    tweets_of_doc = defaultdict(list)
    for idx, tweet in tweets_df.iterrows():
        doc[idx] = tweet.document_id
        tweets_of_doc[tweet.document_id].append(idx)

    return m, doc, tweets_of_doc
