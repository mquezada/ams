import models
from typing import List, Tuple
from pathlib import Path


def add_event(name: str, event: List[int], session):
    with session.begin():
        for id in event:
            e = models.Event(title=name, event_id=id)
            session.add(e)


def add_urls(name: str, session):
    path = Path('data', name, 'resolved_urls.txt')
    with session.begin():
        with path.open('r') as f:
            for line in f:
                short, expanded, title = line.split()
                url = models.URL(short_url=short,
                                 expanded_url=expanded,
                                 title=title)
                session.add(url)


def add_tweets_url(name: str, tweet_urls: List[Tuple[int, str]], session):
    with session.begin():
        for tweet_id, url in tweet_urls:
            url_obj = session.query(models.URL).filter_by(short_url=url).first()
            tweet_url_obj = models.TweetURL(tweet_id=tweet_id,
                                            url_id=url_obj.id)
            session.add(tweet_url_obj)


def get_info(name: str, session):
    with session.begin():
        events = session.query(models.Event).filter_by(title=name).all()

        tweets = []
        for event in events:
            tmp = session.query(models.Tweet).filter_by(event_id_id=event.event_id).all()
            tweets.extend(list(tmp))

        url_ids = []
        for tweet in tweets:
            tweet_url = session.query(models.TweetURL).filter_by(tweet_id=tweet.tweet_id).all()
            for tmp in tweet_url:
                url_ids.append(tmp.url_id)

        urls = []
        for id in url_ids:
            url_obj = session.query(models.URL).filter_by(id=id)
            urls.append(url_obj)

        return events, tweets, url_ids, urls