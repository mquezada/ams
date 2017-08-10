import pickle
from collections import defaultdict

from flask import Flask, render_template, jsonify
from flask import request
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from collections import Counter

import db_utils
from Forms.forms import SelectionForm
from Ranking.ranking_cluster_timeimpact import calculate_time_histogram, rank
from get_representative_tweets import get_representative, get_tweets, list_files_event, get_tweets_db, sort_by_topics, \
    get_tweets_db_list

import logging

import settings
from models import Cluster
from utils.clean_documents import save_summary_text

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s | %(levelname)s : %(message)s', level=logging.INFO)

app = Flask(__name__)
app.url_map.strict_slashes = False


@app.route('/index')
def events():
    return render_template('events.html')

@app.route('/<event_name>')
def see_clusters(event_name):
    path = Path('data',event_name,'clusters')
    clusterings = [x.name for x in path.iterdir() if x.is_dir()]
    return render_template('clusterings.html', clusterings = clusterings, event_name = event_name)

@app.route('/<event_name>/<type>')
def select_cluster(event_name, type):
    path = Path('data',event_name,'clusters',type)
    clusters = [x.name for x in path.iterdir() if x.is_file() and x.suffix != '.txt']
    return render_template('select_clusters.html',clusters = clusters, event_name = event_name, type = type)


@app.route('/<event_name>/<type>/<file>')
def list_cluster(event_name, file, type):
    path_clusters = Path('data', event_name, 'clusters', type, file)
    with path_clusters.open() as clusters:
        lines = clusters.readlines()
        count = Counter(lines)
        total = len(lines)
        clusters.close()
    return render_template('see_topics.html', count=count, event_name=event_name, type=type, file=file, total=total)

@app.route('/explorer',methods = ['POST','GET'])
def explorer():
    form = SelectionForm(request.form)

    if request.method == 'POST':
        event_id = form.event.data
        event_name = db_utils.get_event_name(event_id).title
        clustering = form.clustering.data
        n_clusters = form.n_clusters.data
        n_tweets = form.n_tweets.data
        order = form.order.data
        sort = form.sort.data
        docs = db_utils.get_documents_cluster(clustering, int(n_clusters))
        topic_dict = defaultdict(list)
        for doc in docs:
            topic_dict[doc[0]].append(doc[1])

        for label, doc in topic_dict.items():
            doc.sort(key=lambda x: getattr(x,order), reverse=True)

        docs_sorted = defaultdict(list)
        len_event = len(docs)

        for label, doc in topic_dict.items():
            docs_sorted[label] = doc[:int(n_tweets)]
            save_summary_text(event_name, doc[:n_tweets], clustering, n_tweets=n_tweets)
            docs_sorted[label] = get_tweets_db(docs_sorted[label])

        sorted_topic = docs_sorted
        if sort:
            histograms = defaultdict(list)
            for j in range(int(n_clusters)):
                histograms[j] = calculate_time_histogram(clustering, j, n_clusters)

            ranking = rank(histograms)
            sorted_topic = [x for x in sorted_topic.items()]
            sorted_topic.sort(key=lambda x: ranking.index(x[0]))

        return render_template('see_representative.html', topics = sorted_topic, form = form, sort = sort, len_event = len_event)

    return render_template('see_representative.html',form = form)


@app.route('/<event_name>/<type>/<file>/<int:topic>')
@app.route('/<event_name>/<type>/<file>/<int:topic>/<int:criteria>')
def see_cluster(event_name, file, type, topic, criteria=2):
    n_topics = file.split('.')[3]
    dict_path = Path('data', event_name, 'clusters', type, 'dict_topic_' + n_topics + '.pickle')
    tweets = {}

    if dict_path.exists():
        with dict_path.open('rb') as f:
            tweets = pickle.loads(f.read())
    else:
        path_clusters = Path('data', event_name, 'clusters', type, file)
        path_docs = Path('data', event_name, 'clusters', type, event_name + '_docs.txt')
        tweets = get_representative(path_clusters, path_docs, event_name, type)

    docs = tweets[topic]
    len_topic = len(docs)
    docs.sort(key=lambda x: int(x[criteria]), reverse=True)
    docs_sorted = docs[:12]
    tweet_dict = get_tweets_db_list(docs_sorted)
    return render_template('tweets_selected.html', tweets=tweet_dict, event_name=event_name, file=file, type=type,
                           topic=topic, len_topic = len_topic)

@app.route('/get_clusters')
def get_clusters_options():
    val = request.args.get('select_val', 0)
    clusters = db_utils.get_clusters_event(int(val))
    dict_clust = defaultdict(set)
    for cluster in clusters:
        dict_clust[cluster.method] = cluster.id
    return jsonify(result=dict_clust)

@app.route('/get_number')
def get_number_options():
    val = request.args.get('select_val', 0)
    event = request.args.get('event',0)
    clusters = db_utils.get_clusters_event(int(event))
    dict_clust = defaultdict(list)
    for cluster in clusters:
        if cluster.method == val:
            dict_clust[cluster.n_clusters] = cluster.n_clusters
    return jsonify(result=dict_clust)

if __name__ == "__main__":
    Session = sessionmaker(bind=settings.engine, autocommit=True, expire_on_commit=False)
    session = Session()
    # event_name = 'oscar pistorius'

    # tweets, urls, set_info = set_db.get_info(event_name, session, limit=5000)
    # tweet_index = {t.tweet_id: i for (i, t) in enumerate(tweets)}
    app.url_map.strict_slashes = False
    app.run()
