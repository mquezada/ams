import set_db
import settings
from sqlalchemy.orm import sessionmaker
from flask import Flask, render_template
import logging
import sys


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
                           urls=urls,
                           event_name=event_name.capitalize())

@app.route('/document/<int:doc_id>')
def show_tweets(doc_id):
    tweets, url_tweet = set_db.get_tweets(doc_id, session)
    if url_tweet:
        _, exp, title = list(url_tweet.values())[0]
    else:
        exp = ""
        title = "No URL"

    return render_template('document.html',
                           doc_id=doc_id,
                           url=exp,
                           url_title=title,
                           tweets=tweets,
                           urls=url_tweet)


if __name__ == "__main__":
    Session = sessionmaker(bind=settings.engine, autocommit=True, expire_on_commit=False)
    session = Session()

    event_name = 'oscar pistorius'

    events, tweets, urls = set_db.get_info(event_name, session)
    tweets = tweets[:1000]

    app.run()