import logging
from collections import defaultdict
from pathlib import Path

from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

import models
from models import *
from nlp_utils import match_url, clean_url
from settings import engine, Datasets
from union_find import UnionFind

logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s | %(levelname)s : %(message)s', level=logging.INFO)

Session = sessionmaker(bind=engine, autocommit=True)
session = Session()

def get_event_name(event_id):
    return session.query(Event).filter(Event.event_id == event_id).first()

def get_event_ids(event_name):
    event = session.query(Event).filter(Event.title == event_name).all()
    return [e.event_id for e in event]


def get_tweets(event_ids, urls=False):
    if not urls:
        return session.query(Tweet).filter(Tweet.event_id_id.in_(event_ids)).all()
    return session.query(Tweet, URL)\
        .outerjoin(TweetURL, Tweet.tweet_id == TweetURL.tweet_id)\
        .outerjoin(URL, TweetURL.url_id == URL.id)\
        .filter(Tweet.event_id_id.in_(event_ids))\
        .all()

def get_clusters_event(event_id_id):
    #get all the clusters methods for a specific event.
   q_tweet = session.query(Tweet.tweet_id).filter(Tweet.event_id_id == event_id_id).first()
   q_doc = session.query(DocumentTweet.document_id).filter(DocumentTweet.tweet_id == q_tweet[0]).first()
   q_clusters = session.query(DocumentCluster.cluster_id).filter(DocumentCluster.document_id == q_doc[0]).all()
   clusters_ids = [x[0] for x in q_clusters]
   clusters = session.query(Cluster).filter(Cluster.id.in_(clusters_ids)).all()
   return clusters

def get_documents_cluster(cluster_id, n_clusters):
    #get all the documents of a specific cluster method
    #return tuṕle (label,document)
    q_docs = session.query(DocumentCluster.label, Document).\
        join(Document, DocumentCluster.document_id == Document.id).\
        join(Cluster, Cluster.id == DocumentCluster.cluster_id).\
        filter(DocumentCluster.cluster_id == cluster_id).\
        filter(Cluster.n_clusters == n_clusters).\
        all()

    return q_docs


def get_documents(event_ids):
    return session.query(Document).\
        join(DocumentTweet, DocumentTweet.document_id == Document.id).\
        join(Tweet, DocumentTweet.tweet_id == Tweet.tweet_id).\
        filter(Tweet.event_id_id.in_(event_ids)).\
        filter(Document.total_tweets > 1).\
        all()


def add_event_ids(event_name, event_ids):
    with session.begin():
        for id in tqdm(event_ids, desc=f"Adding event ids for {event_name}"):
            event = Event(title=event_name, event_id=id)
            session.add(event)


def add_urls(event_name):
    path = Path('data', event_name, 'data', 'resolved_urls.txt')
    urls = dict()
    with session.begin(), path.open('r') as f:
        for line in tqdm(f.readlines(), desc=f'Adding urls for {event_name}'):
            short, expanded, title = line.split('\t')
            url = models.URL(short_url=short,
                             expanded_url=expanded,
                             title=title,
                             expanded_clean=clean_url(expanded))
            session.add(url)
            urls[url.short_url] = url
    return urls


def add_tweet_urls(tweets, urls):
    for tweet in tweets:
        matches = match_url(tweet.text)
        for short_url in matches:
            url = urls.get(short_url)
            if url:
                tweet_url = TweetURL(tweet_id=tweet.tweet_id,
                                     url_id=url.id)
                session.add(tweet_url)


def create_documents(tweet_urls):
    uf = UnionFind()

    for tweet, url in tqdm(tweet_urls, desc="Creating sets of individual tweets"):
        uf.make_set(str(tweet.tweet_id))

        if tweet.retweet_of_id:
            uf.make_set(str(tweet.retweet_of_id))
        if tweet.in_reply_to_status_id:
            uf.make_set(str(tweet.in_reply_to_status_id))
        if url:
            uf.make_set(str(url.expanded_clean))

    logger.info(f"Created {uf.size()} sets")

    joint = set()
    for tweet, url in tqdm(tweet_urls, desc="Joining sets"):
        if tweet.retweet_of_id:
            uf.union(str(tweet.tweet_id), str(tweet.retweet_of_id))
        if tweet.in_reply_to_status_id:
            uf.union(str(tweet.tweet_id), str(tweet.in_reply_to_status_id))
        if url and tweet.tweet_id not in joint:
            uf.union(str(tweet.tweet_id), str(url.expanded_clean))
            joint.add(tweet.tweet_id)

    logger.info(f"Join resulted in {uf.size()} sets")

    documents = defaultdict(list)
    tweet_ids = dict()
    for tweet, _ in tqdm(tweet_urls, desc="Grouping tweets into sets"):
        rep = uf.find(str(tweet.tweet_id))
        documents[rep].append(tweet)
        tweet_ids[tweet.tweet_id] = tweet

    documents_objs = dict()
    with session.begin():
        for doc_rep, tweet_list in tqdm(documents.items(), desc="Saving documents"):
            rep = None
            rep_id = None
            total_rts = 0
            total_replies = 0
            total_favs = 0
            total_tweets = 0

            for tweet in tweet_list:
                total_rts += tweet.retweet_count
                total_favs += tweet.favorite_count
                total_replies += 1 if tweet.in_reply_to_status_id else 0
                total_tweets += 1

                if tweet.retweet_of_id:
                    rep = tweet_ids.get(tweet.retweet_of_id)
                    if not rep:
                        rep = tweet.text
                        rep_id = tweet.tweet_id
                    else:
                        rep = rep.text
                        rep_id = tweet_ids[tweet.retweet_of_id].tweet_id
                else:
                    rep = tweet.text
                    rep_id = tweet.tweet_id

            doc = Document(url=rep,
                           tweet_id=rep_id,
                           total_tweets=total_tweets,
                           total_rts=total_rts,
                           total_replies=total_replies,
                           total_favs=total_favs)

            documents_objs[doc_rep] = doc
            session.add(doc)

    with session.begin():
        for doc_rep, tweet_list in tqdm(documents.items(), desc="Saving document_tweets"):
            for tweet in tweet_list:
                dt = DocumentTweet(document_id=documents_objs[doc_rep].id, tweet_id=tweet.tweet_id)
                session.add(dt)

    return uf


if __name__ == '__main__':

   # events = [ #('libya_hotel', Datasets.libya_hotel), ]
              #('mumbai_rape', Datasets.mumbai_rape),
              #('microsoft_nokia', Datasets.microsoft_nokia),
              #('oscar_pistorius', Datasets.oscar_pistorius),]
              #('nepal_earthquake', Datasets.nepal_earthquake)]

    events = [('mumbai_rape',Datasets.mumbai_rape)]
    for name, dataset in events:
        logger.info(name)

        logger.info("adding event ids")
        add_event_ids(name, dataset)
        event_ids = get_event_ids(name)
        logger.info(f"{len(event_ids)} event ids")

        logger.info("adding urls")
        urls = add_urls(name)
        logger.info(f"{len(urls)} urls")

        logger.info("getting tweets")
        tweets = get_tweets(event_ids)
        logger.info(f"{len(tweets)} tweets")

        logger.info("adding tweet urls")
        add_tweet_urls(tweets, urls)

        logger.info("getting tweets with url")
        tweets_with_url = get_tweets(event_ids, True)

        logger.info("adding documents")
        create_documents(tweets_with_url)