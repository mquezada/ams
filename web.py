import set_db
import settings
from sqlalchemy.orm import sessionmaker
from flask import Flask, render_template
from distance import tweet_distance
from settings import Datasets
import random
from create_tfidf import info_for_distance
from tqdm import tqdm
import numpy as np
import logging
import sys
import models


logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s | %(levelname)s : %(message)s', level=logging.INFO, stream=sys.stderr)

app = Flask(__name__)


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


if __name__ == "__main__":
    Session = sessionmaker(bind=settings.engine, autocommit=True, expire_on_commit=False)
    session = Session()

    event_name = 'oscar pistorius'

    tweets, urls, set_info = set_db.get_info(event_name, session, limit=5000)
    tweet_index = {t.tweet_id: i for (i, t) in enumerate(tweets)}
    app.run()