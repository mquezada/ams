import operator
from collections import defaultdict

import pickle
from pathlib import Path

import requests
from sqlalchemy.orm import sessionmaker

import settings
from models import Document, Tweet

Session = sessionmaker(bind=settings.engine, expire_on_commit=False)
session = Session()

def get_representative(path_clusters, path_docs, event_name, type):
    dict_docs = defaultdict(list)

    with path_clusters.open() as clusters, path_docs.open() as docs:
        for cluster, doc in zip(clusters, docs):
            dict_docs[int(cluster.rstrip())].append(doc.split('\t'))
        clusters.close()
        docs.close()

    dict_path = Path('data', event_name, 'clusters', type, 'dict_topic_' + str(len(dict_docs.keys())) + '.pickle')
    with dict_path.open('wb') as f:
        f.write(pickle.dumps(dict_docs))

    return dict_docs


def get_tweets(sorted_doc):
    url = 'https://publish.twitter.com/oembed?url=https://twitter.com/Interior/status/'
    tweet_dict = defaultdict(list)

    for doc in sorted_doc:
        id = doc[1]
        response = requests.get(url + id + '?maxwidth=300')
        try:
            json = response.json()
            if 'error' not in json:
                tweet_dict[id] = json['html']
        except ValueError as e:
            tweet_dict[id] = "Tweet no encontrado"
            print("Tweet no encontrado")
            continue
    return tweet_dict


def list_files(path):
    return [x.name for x in path.iterdir() if x.is_file() and x.suffix != '.txt']


def list_files_event(event_name):
    path_event = Path('data', event_name, 'clusters')
    dict_files = defaultdict(list)
    clusterings = [x.name for x in path_event.iterdir()]
    for clustering in clusterings:
        path_clustering = Path('data', event_name, 'clusters', clustering)
        dict_files[clustering] = [x.name for x in path_clustering.iterdir() if
                                  x.is_file() and x.suffix != '.txt' and x.suffix != '.pickle']

    return dict_files


def get_html(id):
    url = 'https://publish.twitter.com/oembed?url=https://twitter.com/Interior/status/' + str(id) + '?maxwidth=300'
    response = requests.get(url)
    try:
        json = response.json()
        if 'error' not in json:
            return json['html']
    except ValueError as e:
        return "Tweet no encontrado"


def get_tweets_db(sorted_docs):
    tweets_ids = [x.tweet_id for x in sorted_docs]
    docs = session.query(Document).filter(Document.tweet_id.in_(tweets_ids)).all()
    for doc in docs:
        if doc.embebed_html == 'Tweet no encontrado':
            continue
        if doc.embebed_html is None:
            doc.embebed_html = get_html(doc.tweet_id)
    session.commit()
    return docs

def sort_by_topics(sorted_dic):
    for label, docs in sorted_dic.items():
        tweet = docs[0].tweet_id
        date = session.query(Tweet.created_at).filter(Tweet.tweet_id == tweet).first()
        sorted_dic[label] = (date, docs)

    items = sorted(sorted_dic.items(), key=operator.itemgetter(1))
    return items
