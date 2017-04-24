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
from sklearn.cluster import AgglomerativeClustering
from scipy.sparse.csr import csr_matrix
from pandas.core.frame import DataFrame
from pathlib import Path
import pickle

logger = logging.getLogger(__name__)


def create_matrix(tweets: List, name: str = 'oscar pistorius') -> csr_matrix:
    # matrix_loc = Path('data', name, 'tf_idf_matrix.pickle')
    matrix_loc = Path('data', name, 'tf_idf_matrix_docs.pickle')

    if matrix_loc.exists():
        logger.info("Matrix exists! loading...")
        with matrix_loc.open('rb') as f:
            matrix = pickle.loads(f.read())
            return matrix

    stemmer = PorterStemmer()
    tokenizer = TweetTokenizer(preserve_case=False, strip_handles=True)

    text_doc = []
    for tweet in tqdm(tweets, desc="Concateing Documents..."):
        text = tweet.text
        doc_id = tweet.document_id
        if doc_id > len(text_doc):
            text_doc.append(text)
        else:
            text_doc[doc_id - 1] = text_doc[doc_id - 1] + " " + text

    text_doc = [text_doc[i] for i in range(len(text_doc)) if len(text_doc[i]) > 140]

    print(len(text_doc))

    texts = []

    for doc in tqdm(text_doc, desc="(create_matrix) iterating over docs..."):

        tokens = tokenizer.tokenize(doc)
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


def clustering_tfidf(tweets, name: str = 'oscar pistorius'):
    distances = ['cosine', 'manhattan', 'euclidean']
    linkages = ['average', 'complete']
    n_clusters = [2, 5, 10, 13, 15, 20]
    matrix = create_matrix(tweets, name).toarray()
    print(matrix.shape)

    for distance in tqdm(distances, desc='Clustering...'):
        logger.info("Distance: %s", distance)
        for linkage in linkages:
            logger.info("Linkage: %s", linkage)
            for n in n_clusters:
                logger.info("Number of Clusters: %s", n)
                id = distance + '-' + linkage + '-' + str(n)
                labels_clusters = Path('data', name, 'labels_clusters_' + id + '.pickle')

                model = AgglomerativeClustering(n_clusters=n,
                                                linkage=linkage, affinity=distance)

                model.fit(matrix)
                labels = model.labels_

                logger.info("Saving computed matrix...")
                with labels_clusters.open('wb') as f:
                    f.write(pickle.dumps(labels))


def load_cluster(distance, linkage, n_cluster, name):
    file_name = 'labels_clusters_' + distance + '-' + linkage + '-' + str(n_cluster) + '.pickle'
    cluster_loc = Path('data', name, 'clusters_pistorius', file_name)
    if cluster_loc.exists():
        logger.info("Cluster exists! loading...")
        with cluster_loc.open('rb') as f:
            labels = pickle.loads(f.read())
            return labels


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s | %(levelname)s : %(message)s', level=logging.INFO, stream=sys.stdout)
    Session = sessionmaker(bind=engine, autocommit=True, expire_on_commit=False)
    session = Session()
    tweets = session.query(Tweet).filter(Tweet.event_id_id.in_(Datasets.oscar_pistorius)).all()
    clustering_tfidf(tweets, 'oscar pistorius')
    # info_for_distance('oscar pistorius',Datasets.oscar_pistorius)
    # m = create_matrix('oscar pistorius',Datasets.oscar_pistorius)
