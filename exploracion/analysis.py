import string
from collections import Counter, defaultdict
from urllib import parse

from sqlalchemy.orm import sessionmaker
from tqdm import tqdm
from pprint import pprint

import settings
from models import *
from settings import Datasets, engine

Session = sessionmaker(bind=settings.engine, autocommit=True, expire_on_commit=False)
session = Session()

event = settings.Datasets.oscar_pistorius

tweets = session.query(Tweet).filter(Tweet.event_id_id.in_(Datasets.oscar_pistorius)).all()
url_obj = session.query(URL, TweetURL).filter(URL.id == TweetURL.url_id).all()

n_tweets = len(tweets)
tweets_urls = list()

# numero de URLs
n_urls = len(set([url for url, _ in url_obj]))

# tweets con N URLs, N = 1, 2, ...
tweets_with_url = Counter()
with engine.connect() as conn:
    query = conn.execute('select count(url_id) as urls, '
                         'tweet_id from tweet_url group by tweet_id')
    for urls, tweet_id in query:
        tweets_with_url[urls] += 1

tweets_with_url[0] = n_tweets - sum(tweets_with_url[i] for i in tweets_with_url)

# document sizes
documents = defaultdict(list)
for _, tweet_url in url_obj:
    documents[tweet_url.url_id].append(tweet_url.tweet_id)

document_sizes = Counter({k: len(v) for k, v in documents.items()})

# retweets, replies
retweets = 0
replies = 0
for t in tweets:
    if t.is_retweet:
        retweets += 1
    elif t.in_reply_to_status_id:
        replies += 1

# domains
urls = set([url for url, __ in url_obj])
domains = Counter()
for url in urls:
    domain = parse.urlparse(url.expanded_url).netloc
    domains[domain] += 1

# duplicates
id_text = {tweet.tweet_id: tweet.text for tweet in tweets}

document_dup = defaultdict(set)
for url_id, tweet_ids in documents.items():
    document_dup[url_id] = set([id_text[id] for id in tweet_ids])

document_dup_sizes = Counter({k: len(v) for k, v in document_dup.items()})

# duplicates using jaccard similarity between tweets as bag of words
table = str.maketrans({key: None for key in string.punctuation})
del id_text
id_tokens = {}
for tweet in tweets:
    text = tweet.text.lower()
    text = text.translate(table).split()
    id_tokens[tweet.tweet_id] = Counter(text)


def jacc(x, y):
    if len(x) > len(y):
        _x = y
        _y = x
    else:
        _x = y
        _y = x
    _min = 0
    _max = 0
    for word in sorted(_x):
        _min += min(_x[word], _y.get(word, 0))
        _max += max(_x[word], _y.get(word, 0))
    return _min / _max


document_dup_jacc = {
    0.7: defaultdict(set),
    0.6: defaultdict(set),
    0.5: defaultdict(set),
}

thresholds = document_dup_jacc.keys()
document_dup_jacc_sizes = dict()

for thres in tqdm(thresholds):
    for url_id, tweet_ids in tqdm(documents.items()):
        for i in range(len(tweet_ids)):
            ti = id_tokens[tweet_ids[i]]
            sim_i = []
            for j in range(i + 1, len(tweet_ids)):
                tj = id_tokens[tweet_ids[j]]
                sim = jacc(ti, tj)
                sim_i.append(sim)
            if all([sim < thres for sim in sim_i]):
                document_dup_jacc[thres][url_id].add(tweet_ids[i])

    document_dup_jacc_sizes[thres] = Counter({k: len(v)
                                              for k, v in document_dup_jacc[thres].items()})

for thres in thresholds:
    print(thres)
    pprint(document_dup_jacc_sizes[thres].most_common(10))