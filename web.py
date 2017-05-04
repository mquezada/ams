from pathlib import Path

import set_db
import settings
from sqlalchemy.orm import sessionmaker
from sklearn import metrics
from flask import Flask, render_template
from distance import tweet_distance
from settings import Datasets
import random
from create_tfidf import info_for_distance, load_cluster
from tqdm import tqdm
import numpy as np
import logging
import sys
import os
import models
import pickle

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s | %(levelname)s : %(message)s', level=logging.INFO, stream=sys.stderr)

app = Flask(__name__)


@app.route("/test/")
def test():
    Session = sessionmaker(bind=settings.engine, autocommit=True, expire_on_commit=False)
    session = Session()
    docs = session.query(models.Document).all()
    docs_info = {d.id: d.url for d in docs}
    tweets, url_tweet, set_info = set_db.get_tweets(1, session)
    return render_template('test.html', docs_info=docs_info)


@app.route("/")
def main():
    return render_template('index.html')


@app.route("/event/")
def show_info():
    return render_template('index.html',
                           tweets=tweets,
                           index=tweet_index,
                           urls=urls,
                           set_info=set_info,
                           event_name=event_name.capitalize())


@app.route('/document/<int:doc_id>')
def document(doc_id):
    tweets, url_tweet, set_info = set_db.get_tweets(doc_id, session)
    if url_tweet:
        _, exp, title = list(url_tweet.values())[0]
    else:
        exp = ""
        title = "No URL"

    return render_template('document.html',
                           doc_id=doc_id,
                           index=tweet_index,
                           set_info=set_info,
                           url=exp,
                           url_title=title,
                           tweets=tweets,
                           urls=url_tweet)


@app.route('/clusters/<string:distance>/<string:linkage>/<int:n_cluster>/<int:cluster>')
def see_cluster(distance, linkage, n_cluster, cluster):
    cluster_labels = load_cluster(distance, linkage, n_cluster, 'oscar pistorius')
    cluster_elements = [i for i in range(len(cluster_labels)) if cluster_labels[i] == cluster]
    tweet_clust_dict = {}
    url_clust_dict = {}
    n_elements = len(cluster_elements)
    for cluster_element in cluster_elements:
        tweets = set_db.get_onlytweets(cluster_element, session)
        tweet_clust_dict[cluster_element] = tweets

    return render_template('see_cluster.html', tweet_dict=tweet_clust_dict, cluster=cluster, n_elements=n_elements)


@app.route('/clusters/<string:distance>/<string:linkage>/<int:n_cluster>')
def index_cluster(distance, linkage, n_cluster):
    cluster_labels = load_cluster(distance, linkage, n_cluster, 'oscar pistorius')
    m, doc, tweets_of_doc = info_for_distance('oscar pistorius', Datasets.oscar_pistorius)
    silhouette = metrics.silhouette_score(m, cluster_labels, metric='cosine')
    unique, counts = np.unique(cluster_labels, return_counts=True)
    n_elements = dict(zip(unique, counts))
    return render_template("cluster_index.html", distance=distance, linkage=linkage, n_cluster=n_cluster,
                           silhouette=silhouette, n_elements=n_elements)


@app.route('/clusters')
def clusters():
    files_distance={}
    for file in os.listdir("data/oscar pistorius"):
        if file.endswith(".pickle") and file.startswith("labels_clusters"):
            file = file[16:-7]
            tokens=file.split('-')
            distance=tokens[0]
            if distance in files_distance:
                elements=files_distance[distance]
                elements.append(tokens)
                files_distance[distance]=elements
            else:
                files_distance[distance]=[tokens]

    return render_template('clusters.html', files=files_distance)


@app.route('/distances')
def distances():
    m_tf_idf, doc_dict, tweet_dict = info_for_distance('oscar pistorius',
                                                       Datasets.oscar_pistorius)

    Session = sessionmaker(bind=settings.engine, autocommit=True, expire_on_commit=False)
    session = Session()

    docs = session.query(models.Document).all()
    docs_info = {d.id: d.url for d in docs}

    lens = list(map(len, tweet_dict.values()))
    max_scale = max(lens) / min(lens)

    sample_size = 10
    docs_to_sample = [k for k in tweet_dict if len(tweet_dict[k]) > 100]

    docs = random.sample(docs_to_sample, sample_size)
    all_dists = []

    for i in range(len(docs)):
        doc1 = docs[i]
        for j in range(i + 1, len(docs)):
            doc2 = docs[j]
            distances = []
            for t1 in tqdm(tweet_dict[doc1], desc=str((doc1, doc2))):
                for t2 in tweet_dict[doc2]:
                    d = tweet_distance(t1,
                                       t2,
                                       doc_dict,
                                       tweet_dict,
                                       m_tf_idf,
                                       max_scale=max_scale)
                    distances.append(d)

            all_dists.append((doc1,
                              len(tweet_dict[doc1]),
                              doc2,
                              len(tweet_dict[doc2]),
                              np.min(distances),
                              np.mean(distances),
                              np.max(distances)))

    return render_template('distances.html', distances=all_dists, info=docs_info)

@app.route('/topics/')
def topics():
    return  render_template('topics.html')

@app.route('/topics/<int:n_topics>')
def list_topics(n_topics):
    dic_loc = Path('data','dict_docs_T'+str(n_topics)+'.pickle')
    with dic_loc.open('rb') as f:
        dic = pickle.loads(f.read())
    topics_lenght = {k: len(v) for k, v in dic.items()}
    return render_template('list_topics.html',n_topics = n_topics, topics = topics_lenght)

@app.route('/topics/<int:n_topics>/<int:topic>')
def see_topic(n_topics, topic):
    dic_loc = Path('data', 'dict_docs_T' + str(n_topics) + '.pickle')
    with dic_loc.open('rb') as f:
        dic = pickle.loads(f.read())

    tweets_ids = dic[str(topic)]
    tweets = set_db.get_tweets_topic(session,tweets_ids)
    return render_template('see_topic.html', tweets = tweets, topic = topic)

if __name__ == "__main__":
    Session = sessionmaker(bind=settings.engine, autocommit=True, expire_on_commit=False)
    session = Session()

    event_name = 'oscar pistorius'

    tweets, urls, set_info = set_db.get_info(event_name, session, limit=5000)
    tweet_index = {t.tweet_id: i for (i, t) in enumerate(tweets)}
    app.run(debug=True)

