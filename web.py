import logging
import pickle
import sys
from collections import defaultdict
from pathlib import Path
from urllib import parse

from flask import Flask, render_template
from sqlalchemy.orm import sessionmaker
from create_tfidf import info_for_distance, load_cluster
from distance import tweet_distance
from sklearn import metrics
import os
from tqdm import tqdm
import random
import numpy as np
import models
from settings import Datasets

import set_db
import settings
from models import *
from settings import engine

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s | %(levelname)s : %(message)s', level=logging.INFO, stream=sys.stderr)

app = Flask(__name__)


# @app.route("/test/")
# def test():
#     Session = sessionmaker(bind=settings.engine, autocommit=True, expire_on_commit=False)
#     session = Session()
#     docs = session.query(models.Document).all()
#     docs_info = {d.id: d.url for d in docs}
#     tweets, url_tweet, set_info = set_db.get_tweets(1, session)
#     return render_template('test.html', docs_info=docs_info)
#
#
# @app.route("/")
# def main():
#     return render_template('index.html')
#
#
# @app.route("/event/")
# def show_info():
#     return render_template('index.html',
#                            tweets=tweets,
#                            index=tweet_index,
#                            urls=urls,
#                            set_info=set_info,
#                            event_name=event_name.capitalize())
#
#
# @app.route('/document/<int:doc_id>')
# def document(doc_id):
#     tweets, url_tweet, set_info = set_db.get_tweets(doc_id, session)
#     if url_tweet:
#         _, exp, title = list(url_tweet.values())[0]
#     else:
#         exp = ""
#         title = "No URL"
#
#     return render_template('document.html',
#                            doc_id=doc_id,
#                            index=tweet_index,
#                            set_info=set_info,
#                            url=exp,
#                            url_title=title,
#                            tweets=tweets,
#                            urls=url_tweet)
#
#
# @app.route('/clusters/<string:distance>/<string:linkage>/<int:n_cluster>/<int:cluster>')
# def see_cluster(distance, linkage, n_cluster, cluster):
#     cluster_labels = load_cluster(distance, linkage, n_cluster, 'oscar_pistorius')
#     cluster_elements = [i for i in range(len(cluster_labels)) if cluster_labels[i] == cluster]
#     tweet_clust_dict = {}
#     url_clust_dict = {}
#     n_elements = len(cluster_elements)
#     for cluster_element in cluster_elements:
#         tweets = set_db.get_onlytweets(cluster_element, session)
#         tweet_clust_dict[cluster_element] = tweets
#
#     return render_template('see_cluster.html', tweet_dict=tweet_clust_dict, cluster=cluster, n_elements=n_elements)
#
#
# @app.route('/clusters/<string:distance>/<string:linkage>/<int:n_cluster>')
# def index_cluster(distance, linkage, n_cluster):
#     cluster_labels = load_cluster(distance, linkage, n_cluster, 'oscar pistorius')
#     m, doc, tweets_of_doc = info_for_distance('oscar pistorius', Datasets.oscar_pistorius)
#     silhouette = metrics.silhouette_score(m, cluster_labels, metric='cosine')
#     unique, counts = np.unique(cluster_labels, return_counts=True)
#     n_elements = dict(zip(unique, counts))
#     return render_template("cluster_index.html", distance=distance, linkage=linkage, n_cluster=n_cluster,
#                            silhouette=silhouette, n_elements=n_elements)
#
#
# @app.route('/clusters')
# def clusters():
#     files_distance={}
#     for file in os.listdir("data/oscar pistorius"):
#         if file.endswith(".pickle") and file.startswith("labels_clusters"):
#             file = file[16:-7]
#             tokens=file.split('-')
#             distance=tokens[0]
#             if distance in files_distance:
#                 elements=files_distance[distance]
#                 elements.append(tokens)
#                 files_distance[distance]=elements
#             else:
#                 files_distance[distance]=[tokens]
#
#     print(files_distance)
#     return render_template('clusters.html', files=files_distance)
#
#
# @app.route('/distances')
# def distances():
#     m_tf_idf, doc_dict, tweet_dict = info_for_distance('oscar pistorius',
#                                                        Datasets.oscar_pistorius)
#
#     Session = sessionmaker(bind=settings.engine, autocommit=True, expire_on_commit=False)
#     session = Session()
#
#     docs = session.query(models.Document).all()
#     docs_info = {d.id: d.url for d in docs}
#
#     lens = list(map(len, tweet_dict.values()))
#     max_scale = max(lens) / min(lens)
#
#     sample_size = 10
#     docs_to_sample = [k for k in tweet_dict if len(tweet_dict[k]) > 100]
#
#     docs = random.sample(docs_to_sample, sample_size)
#     all_dists = []
#
#     for i in range(len(docs)):
#         doc1 = docs[i]
#         for j in range(i + 1, len(docs)):
#             doc2 = docs[j]
#             distances = []
#             for t1 in tqdm(tweet_dict[doc1], desc=str((doc1, doc2))):
#                 for t2 in tweet_dict[doc2]:
#                     d = tweet_distance(t1,
#                                        t2,
#                                        doc_dict,
#                                        tweet_dict,
#                                        m_tf_idf,
#                                        max_scale=max_scale)
#                     distances.append(d)
#
#             all_dists.append((doc1,
#                               len(tweet_dict[doc1]),
#                               doc2,
#                               len(tweet_dict[doc2]),
#                               np.min(distances),
#                               np.mean(distances),
#                               np.max(distances)))
#
#     return render_template('distances.html', distances=all_dists, info=docs_info)



# <<<<<<< HEAD
# =======
# @app.route('/document/<int:doc_id>')
# def document(doc_id):
#     tweets, url_tweet, set_info = set_db.get_tweets(doc_id, session)
#     if url_tweet:
#         _, exp, title = list(url_tweet.values())[0]
#     else:
#         exp = ""
#         title = "No URL"
#
#     return render_template('document.html',
#                            doc_id=doc_id,
#                            index=tweet_index,
#                            set_info=set_info,
#                            url=exp,
#                            url_title=title,
#                            tweets=tweets,
#                            urls=url_tweet)
#
#


# @app.route('/clusters/<string:distance>/<string:linkage>/<int:n_cluster>/<int:cluster>')
# def see_cluster(distance, linkage, n_cluster, cluster):
#     cluster_labels = load_cluster(distance, linkage, n_cluster, 'oscar pistorius')
#     cluster_elements = [i for i in range(len(cluster_labels)) if cluster_labels[i] == cluster]
#     tweet_clust_dict = {}
#     url_clust_dict = {}
#     n_elements = len(cluster_elements)
#     for cluster_element in cluster_elements:
#         tweets = set_db.get_onlytweets(cluster_element, session)
#         tweet_clust_dict[cluster_element] = tweets
#
#     return render_template('see_cluster.html', tweet_dict=tweet_clust_dict, cluster=cluster, n_elements=n_elements)
#
#
# @app.route('/clusters/<string:distance>/<string:linkage>/<int:n_cluster>')
# def index_cluster(distance, linkage, n_cluster):
#     cluster_labels = load_cluster(distance, linkage, n_cluster, 'oscar pistorius')
#     m, doc, tweets_of_doc = info_for_distance('oscar pistorius', Datasets.oscar_pistorius)
#     silhouette = metrics.silhouette_score(m, cluster_labels, metric='cosine')
#     unique, counts = np.unique(cluster_labels, return_counts=True)
#     n_elements = dict(zip(unique, counts))
#     return render_template("cluster_index.html", distance=distance, linkage=linkage, n_cluster=n_cluster,
#                            silhouette=silhouette, n_elements=n_elements)
#
#
# @app.route('/clusters')
# def clusters():
#     files_distance = {}
#     for file in os.listdir("data/oscar_pistorius/clusters/"):
#         if file.endswith(".pickle") and file.startswith("labels_clusters"):
#             file = file[16:-7]
#             tokens = file.split('-')
#             distance = tokens[0]
#             if distance in files_distance:
#                 elements = files_distance[distance]
#                 elements.append(tokens)
#                 files_distance[distance] = elements
#             else:
#                 files_distance[distance] = [tokens]
#
#     return render_template('clusters.html', files=files_distance)
#
#
# @app.route('/distances')
# def distances():
#     m_tf_idf, doc_dict, tweet_dict = info_for_distance('oscar pistorius',
#                                                        Datasets.oscar_pistorius)
#
#     Session = sessionmaker(bind=settings.engine, autocommit=True, expire_on_commit=False)
#     session = Session()
#
#     docs = session.query(models.Document).all()
#     docs_info = {d.id: d.url for d in docs}
#
#     lens = list(map(len, tweet_dict.values()))
#     max_scale = max(lens) / min(lens)
#
#     sample_size = 10
#     docs_to_sample = [k for k in tweet_dict if len(tweet_dict[k]) > 100]
#
#     docs = random.sample(docs_to_sample, sample_size)
#     all_dists = []
#
#     for i in range(len(docs)):
#         doc1 = docs[i]
#         for j in range(i + 1, len(docs)):
#             doc2 = docs[j]
#             distances = []
#             for t1 in tqdm(tweet_dict[doc1], desc=str((doc1, doc2))):
#                 for t2 in tweet_dict[doc2]:
#                     d = tweet_distance(t1,
#                                        t2,
#                                        doc_dict,
#                                        tweet_dict,
#                                        m_tf_idf,
#                                        max_scale=max_scale)
#                     distances.append(d)
#
#             all_dists.append((doc1,
#                               len(tweet_dict[doc1]),
#                               doc2,
#                               len(tweet_dict[doc2]),
#                               np.min(distances),
#                               np.mean(distances),
#                               np.max(distances)))
#
#     return render_template('distances.html', distances=all_dists, info=docs_info)


###########


def get_event_ids(event_name):
    events = session.query(Event).filter(Event.title == event_name).all()
    return [e.event_id for e in events]


@app.route('/')
def all_events():
    with engine.connect() as conn:
        query = 'select distinct title from event_id'
        events = conn.execute(query)

        events = [str(e[0]) for e in events]
        events_str = [' '.join(map(str.capitalize, e.split('_'))) for e in events]
        return render_template('all_events.html', events=list(zip(events_str, events)))


@app.route('/documents/<event_name>/', defaults={'filter': None})
@app.route('/documents/<event_name>/<filter>')
def documents(event_name, filter):
    ids = get_event_ids(event_name)
    tweets = session.query(Tweet) \
        .filter(Tweet.event_id_id.in_(ids)) \
        .all()

    docs = defaultdict(int)
    domains = dict()
    doc_ids = dict()
    for t in tweets:
        url_or_int = t.document.url
        parsed = parse.urlparse(url_or_int).netloc.strip()

        tokens = parsed.split('.')
        if tokens[0].startswith('www'):
            parsed = '.'.join(tokens[1:])

        docs[url_or_int] += 1
        domains[url_or_int] = parsed
        doc_ids[url_or_int] = t.document.id

    if filter:
        docs_ = {k: v for k, v in docs.items() if v > 1}
        docs = docs_

    return render_template('documents.html',
                           documents=docs,
                           domains=domains,
                           ids=doc_ids,
                           event_name=event_name)


@app.route('/document/<doc_id>/')
def document(doc_id):
    session_m = sessionmaker(bind=settings.engine, autocommit=True, expire_on_commit=False)
    session = session_m()

    tweets = session.query(Tweet, URL).filter(Tweet.document_id == doc_id) \
        .outerjoin(TweetURL, Tweet.tweet_id == TweetURL.tweet_id) \
        .outerjoin(URL, TweetURL.url_id == URL.id) \
        .all()

    return render_template('event.html',
                           event_name='',
                           tweets_urls=tweets)


@app.route('/event/<event_name>/', defaults={'limit': None})
@app.route('/event/<event_name>/<limit>/')
def event(event_name, limit):
    ids = get_event_ids(event_name)

    tweets = session.query(Tweet, URL) \
        .outerjoin(TweetURL, Tweet.tweet_id == TweetURL.tweet_id) \
        .outerjoin(URL, TweetURL.url_id == URL.id) \
        .filter(Tweet.event_id_id.in_(ids))

    if limit:
        tweets = tweets.limit(limit)

    tweets = tweets.all()

    return render_template('event.html',
                           event_name=event_name,
                           tweets_urls=tweets)


@app.route('/clusters/<event_name>/')
def clusters(event_name):
    clusters = session.query(Cluster).all()
    return render_template('all_clusters.html', clusters=clusters, event_name=event_name)


@app.route('/clusters/<event_name>/<method>/<distance>/<n_clusters>/<int:label>/')
def see_cluster(event_name, method, distance, n_clusters, label):
    cluster = session.query(Cluster).filter_by(method=method,
                                               distance=distance,
                                               n_clusters=n_clusters).first()

    ids = get_event_ids(event_name)

    tweets = session.query(Tweet, URL, TweetCluster)\
        .join(TweetCluster, Tweet.tweet_id == TweetCluster.tweet_id)\
        .outerjoin(TweetURL, Tweet.tweet_id == TweetURL.tweet_id)\
        .outerjoin(URL, TweetURL.url_id == URL.id)\
        .filter(TweetCluster.cluster_id == cluster.id)\
        .filter(Tweet.event_id_id.in_(ids))\
        .all()

    labels = dict()
    tweet_ids = dict()
    tweet_text = dict()
    urls = dict()

    labels_unique = defaultdict(list)

    for tweet, url, tc in tweets:
        id = tweet.tweet_id
        tweet_ids[id] = tweet
        urls[id] = url
        labels[id] = tc.label

        tweet_text[tweet.text] = id

    for text, id in tweet_text.items():
        labels_unique[labels[id]].append((tweet_ids[tweet_text[text]], urls[id]))

    return render_template('event.html',
                           event_name=event_name,
                           tweets_urls=labels_unique[label])


@app.route('/topics/<event_name>/')
def topics(event_name):
    return render_template('topics.html', event_name=event_name)


@app.route('/topics/<event_name>/<int:n_topics>/')
def list_topics(n_topics, event_name):
    dic_loc = Path('data', event_name, 'clusters', 'tm', 'dict_docs_T' + str(n_topics) + '.pickle')
    with dic_loc.open('rb') as f:
        dic = pickle.loads(f.read())
    topics_lenght = {k: len(v) for k, v in dic.items()}
    return render_template('list_topics.html', n_topics=n_topics, event_name=event_name, topics=topics_lenght)


@app.route('/topics/<event_name>/<int:n_topics>/<int:topic>/')
def see_topic(n_topics, event_name, topic):
    dic_loc = Path('data', event_name, 'clusters', 'tm', 'dict_docs_T' + str(n_topics) + '.pickle')
    with dic_loc.open('rb') as f:
        dic = pickle.loads(f.read())

    tweets_ids = dic[str(topic)]
    tweets = set_db.get_tweets_topic(session, tweets_ids)
    return render_template('see_topic.html', tweets=tweets, topic=topic)


if __name__ == "__main__":
    Session = sessionmaker(bind=settings.engine, autocommit=True, expire_on_commit=False)
    session = Session()

    # event_name = 'oscar pistorius'

    # tweets, urls, set_info = set_db.get_info(event_name, session, limit=5000)
    # tweet_index = {t.tweet_id: i for (i, t) in enumerate(tweets)}
    app.url_map.strict_slashes = False
    app.run()


# todo
# mostrar documentos con representantes y datos, por evento