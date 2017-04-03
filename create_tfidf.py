from nltk.corpus import stopwords
from nltk.stem.snowball import PorterStemmer
from nltk.tokenize.casual import TweetTokenizer

from collections import defaultdict
import sys
import string

from sqlalchemy.orm import sessionmaker
from settings import Datasets, engine
from models import Tweet
from typing import List

from load_dataset import load
from settings import engine, Datasets
import logging
from tqdm import tqdm
import nlp_utils
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse.csr import csr_matrix
from pandas.core.frame import DataFrame
from pathlib import Path
import pickle

logger = logging.getLogger(__name__)

def create_matrix(tweets: List, name: str = 'oscar pistorius') -> csr_matrix:
    matrix_loc = Path('data', name, 'tf_idf_matrix.pickle')

    if matrix_loc.exists():
        logger.info("Matrix exists! loading...")
        with matrix_loc.open('rb') as f:
            matrix = pickle.loads(f.read())
            return matrix

    stemmer = PorterStemmer()
    tokenizer = TweetTokenizer(preserve_case=False, strip_handles=True)

    texts = []
    for tweet in tqdm(tweets, desc="(create_matrix) iterating over tweets..."):
        text = tweet.text

        tokens = tokenizer.tokenize(text)
        text_proc = []
        for token in tokens:
            token = token.strip()
            if len(token) < 3:
                continue
            elif token in stopwords.words('english'):
                continue
            elif nlp_utils.match_url(token):
                continue
            elif token in string.punctuation:
                continue
            # elif token.startswith(("#", "$")):
            #     continue

            token = token.translate({ord(k): "" for k in string.punctuation})
            token = stemmer.stem(token)

            token = token.strip()
            if token == "":
                continue

            text_proc.append(token)

        texts.append(text_proc)

    vectorizer = TfidfVectorizer(analyzer="word", tokenizer=lambda x: x, lowercase=False)
    m = vectorizer.fit_transform(texts)

    logger.info("Saving computed matrix...")
    with matrix_loc.open('wb') as f:
        f.write(pickle.dumps(m))

    return m


def info_for_distance(name: str, dataset: List[int]):
    Session = sessionmaker(bind=engine, autocommit=True, expire_on_commit=False)
    session = Session()

    tweets = session.query(Tweet).filter(Tweet.event_id_id.in_(dataset)).all()
    m = create_matrix(tweets, name)

    doc = {}
    tweets_of_doc = defaultdict(list)
    for idx, tweet in enumerate(tweets):
        doc[idx] = tweet.document_id
        tweets_of_doc[tweet.document_id].append(idx)

    return m, doc, tweets_of_doc



if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s | %(levelname)s : %(message)s', level=logging.INFO, stream=sys.stdout)
    m = create_matrix()
