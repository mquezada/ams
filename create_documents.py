from pandas.core.frame import DataFrame
from tqdm import trange
from collections import defaultdict

import logging
import nlp_utils


logger = logging.getLogger(__name__)


def create_documents(tweets_df: DataFrame, urls_df: DataFrame):
    urls_dict = dict()
    for i in trange(len(urls_df), desc="Creating URLs dict"):
        row = urls_df.loc[i]
        urls_dict[row['tweet_url']] = row['expanded_url']

    texts = tweets_df['text']
    documents = defaultdict(list)

    for i in trange(len(texts), desc="Creating docs"):
        text = texts[i]
        matches = nlp_utils.match_url(text)
        for match in matches:
            expanded_url = urls_dict.get(match, match)
            documents[expanded_url].append(text)

    return documents
