import logging
import string

from nltk.corpus import stopwords
from nltk.stem.snowball import PorterStemmer
from nltk.tokenize.casual import TweetTokenizer
from scipy.sparse.csr import csr_matrix
from sklearn.cluster import AgglomerativeClustering
from sklearn.cluster import MiniBatchKMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

from models import *
import numpy as np
import nlp_utils
import re
from models import Tweet
from settings import engine, Datasets
from db_utils import get_event_ids, get_documents

logger = logging.getLogger(__name__)

_session = sessionmaker(bind=engine, autocommit=True, expire_on_commit=False)
session = _session()


def process_texts(event_name, stem=False):
    event_ids = get_event_ids(event_name)
    documents = get_documents(event_ids)

    stemmer = PorterStemmer()
    tokenizer = TweetTokenizer(preserve_case=False, strip_handles=True)
    texts = []
    final_documents = []

    for doc in tqdm(documents, desc="cleaning documents"):
        text = ' '.join(doc.url.split())
        tokens = tokenizer.tokenize(text)
        text_proc = []

        n_hashtags = 0
        for token in tokens:
            token = token.strip()
            if token.startswith('#'):
                n_hashtags += 1
            if token.startswith('@'):
                continue
            if nlp_utils.match_url(token):
                continue
            if token in string.punctuation:
                continue
            if re.findall(r'^[^\w\s]+$', token):
                continue
            if token in stopwords.words('english'):
                continue

            token = token.translate({ord(k): "" for k in string.punctuation})

            if stem:
                token = stemmer.stem(token)

            token = token.strip()
            if len(token) < 2:
                continue

            text_proc.append(token)

        if n_hashtags > 3:
            continue

        if not text_proc:
            continue

        texts.append(text_proc)
        final_documents.append(doc)

    texts_one_per_line = []
    for text in texts:
        texts_one_per_line.append(' '.join(text))
    return texts_one_per_line, final_documents


def create_matrix(texts):
    v = TfidfVectorizer(analyzer="word", tokenizer=lambda x: x, lowercase=False)
    matrix = v.fit_transform(texts)
    return matrix


def kmeans(n_clusters, matrix):
    mbk = MiniBatchKMeans(n_clusters=n_clusters)
    mbk.fit_transform(matrix)

    return mbk


def inspect_clusters(labels, documents, limit=30):
    docs = np.array(documents)
    for i in range(max(labels) + 1):
        print(i)
        cluster = docs[labels == i]
        for doc in cluster[:limit]:
            print(doc.url)
        print()


def save_clusters(method, distance, n_clusters, labels, documents):
    cluster = session.query(Cluster).filter_by(method=method,
                                               distance=distance,
                                               n_clusters=n_clusters).first()
    docs = np.array(documents)
    with session.begin():
        for i in range(max(labels) + 1):
            doc_cluster = docs[labels == i]
            for doc in doc_cluster:
                dc = DocumentCluster(document_id=doc.id,
                                     cluster_id=cluster.id,
                                     label=i)
                session.add(dc)


if __name__ == '__main__':
    event_name = 'oscar_pistorius'
    texts, documents = process_texts(event_name)
    print(texts)

    # documents, matrix = create_matrix(event_name)
    # for n_clusters in range(3, 7):
    #     km = kmeans(n_clusters, matrix)
    #     save_clusters('minibatch_kmeans', 'euclidean', n_clusters, km.labels_, documents)