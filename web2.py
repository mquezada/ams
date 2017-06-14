import pickle
from collections import defaultdict

from flask import Flask, render_template, jsonify
from flask import request
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from collections import Counter

from Forms.forms import SelectionForm
from get_representative_tweets import get_representative, get_tweets, list_files_event, get_tweets_db

import logging

import settings


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
        event_name = form.event.data
        clustering = form.clustering.data.split('/')[1]
        file = form.n_clusters.data.split('/')[2]
        order = form.order.data
        n_topics = [x for x in range(int(file.split('.')[3]))]
        return render_template('see_representative.html', form=form, event_name=event_name, clustering=clustering,
                               file=file, order=order, n_topics = n_topics)

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
    docs_sorted = docs[:7]
    tweet_dict = get_tweets_db(docs_sorted)

    return render_template('tweets_selected.html', tweets=tweet_dict, event_name=event_name, file=file, type=type,
                           topic=topic, len_topic = len_topic)

@app.route('/get_file')
def get_file():
    val = request.args.get('select_val', 0).split('/')
    path_file = Path('data', val[0], 'clusters')
    if len(val) > 1:
        path_file = Path('data',val[0],'clusters',val[1])

    files = [x.name for x in path_file.iterdir() if x.suffix != '.txt' and x.suffix != '.pickle']
    return jsonify(result=files)

if __name__ == "__main__":
    Session = sessionmaker(bind=settings.engine, autocommit=True, expire_on_commit=False)
    session = Session()

    # event_name = 'oscar pistorius'

    # tweets, urls, set_info = set_db.get_info(event_name, session, limit=5000)
    # tweet_index = {t.tweet_id: i for (i, t) in enumerate(tweets)}
    app.url_map.strict_slashes = False
    app.run()