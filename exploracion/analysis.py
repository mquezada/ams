import string
from collections import Counter, defaultdict
from urllib import parse

from sqlalchemy.orm import sessionmaker
from pprint import pprint

import settings
from models import *
from settings import Datasets, engine, LOCAL_DATA_DIR
from pathlib import Path
from operator import itemgetter


Session = sessionmaker(bind=settings.engine, autocommit=True, expire_on_commit=False)
session = Session()

#events = [(settings.Datasets.oscar_pistorius, 'oscar_pistorius'),
# events = [(settings.Datasets.microsoft_nokia, 'microsoft_nokia')]
events = [(settings.Datasets.nepal_earthquake, 'nepal_earthquake')]

for event, name in events:
    event_dir = LOCAL_DATA_DIR / Path(name)

    table_f = (event_dir / Path('stats.txt')).open('w')
    tweets_with_url_f = (event_dir / Path('tweets_with_url.txt')).open('w')
    document_sizes_f = (event_dir / Path('document_sizes.txt')).open('w')
    domains_f = (event_dir / Path('domains.txt')).open('w')
    document_sizes_dup_f = (event_dir / Path('document_sizes_dup.txt')).open('w')
    document_sizes_dup_jacc_f = (event_dir / Path('document_sizes_dup_jacc.txt')).open('w')

    files = [table_f, tweets_with_url_f, document_sizes_dup_f,
             document_sizes_dup_jacc_f, document_sizes_f, domains_f]

    tweets = session.query(Tweet).filter(Tweet.event_id_id.in_(event)).all()
    url_obj = session.query(URL, TweetURL, Tweet)\
        .filter(Tweet.tweet_id == TweetURL.tweet_id)\
        .filter(Tweet.event_id_id.in_(event))\
        .filter(URL.id == TweetURL.url_id).all()

    url_obj = list(map(itemgetter(0, 1), url_obj))

    n_tweets = len(tweets)
    tweets_urls = list()

    # numero de URLs
    n_urls = len(set([url for url, _ in url_obj]))

    print(f"Total tweets: {n_tweets}")
    print(f"Total unique URLs: {n_urls}")

    # tweets con N URLs, N = 1, 2, ...
    tweets_with_url = Counter()
    with engine.connect() as conn:
        query = conn.execute(f'select count(url_id) as urls, '
                             f'tweet_url.tweet_id from tweet_url join tweet on tweet_url.tweet_id = tweet.tweet_id '
                             f'where tweet.event_id_id in ({",".join(map(str, event))})'
                             f'group by tweet_id')

        for urls, tweet_id in query:
            tweets_with_url[urls] += 1

    tweets_with_url[0] = n_tweets - sum(tweets_with_url[i] for i in tweets_with_url)

    print(f"Tweets with URLs: {tweets_with_url}")
    tweets_with_url_f.write('n_urls\ttotal_tweets\n')
    for k, v in tweets_with_url.most_common():
        tweets_with_url_f.write('\t'.join(map(str, [k, v])) + '\n')

    # document sizes
    documents = defaultdict(list)
    for _, tweet_url in url_obj:
        documents[tweet_url.url_id].append(tweet_url.tweet_id)

    document_sizes = Counter({k: len(v) for k, v in documents.items()})

    document_sizes_f.write('url_id\tn_tweets\n')
    for k, v in document_sizes.most_common():
        document_sizes_f.write('\t'.join(map(str, [k, v])) + '\n')

    print(f"Document sizes: {document_sizes.most_common(10)}")

    # retweets, replies
    retweets = 0
    replies = 0
    for t in tweets:
        if t.is_retweet:
            retweets += 1
        elif t.in_reply_to_status_id:
            replies += 1

    print(f"Total retweets: {retweets}")
    print(f"Total replies: {replies}")

    # domains
    urls = set([url for url, __ in url_obj])
    domains = Counter()
    for url in urls:
        domain = parse.urlparse(url.expanded_url).netloc.strip()
        domains[domain] += 1

    print(f"Domain frequency: {domains.most_common(10)}")
    domains_f.write('netloc\tn_urls\n')
    for k, v in domains.most_common():
        domains_f.write('\t'.join(map(str, [k, v])) + '\n')

    # duplicates
    id_text = {tweet.tweet_id: tweet.text for tweet in tweets}

    document_dup = defaultdict(set)
    for url_id, tweet_ids in documents.items():
        document_dup[url_id] = set([id_text[id] for id in tweet_ids])

    document_dup_sizes = Counter({k: len(v) for k, v in document_dup.items()})

    print(f"Document sizes (after removing exact duplicates): {document_dup_sizes.most_common(10)}")

    document_sizes_dup_f.write('url_id\tn_tweets\n')
    for k, v in document_dup_sizes.most_common():
        document_sizes_dup_f.write('\t'.join(map(str, [k, v])) + '\n')


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

    for thres in thresholds:
        for url_id, tweet_ids in (documents.items()):
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

    print("Document sizes (after removing pseudo-duplicates): ")

    document_sizes_dup_jacc_f.write('threshold\turl_id\tn_tweets\n')

    for thres in thresholds:
        print(f"Threshold: {thres}")
        pprint(document_dup_jacc_sizes[thres].most_common(10))

        for k, v in document_dup_jacc_sizes[thres].most_common():
            document_sizes_dup_jacc_f.write('\t'.join(map(str, [thres, k, v])) + '\n')

    headers = ['total_tweets', 'total_urls', 'total_domains',
               'tweets_with_url', 'retweets', 'replies',
               'total_documents']
    data = list()
    data.append(n_tweets)
    data.append(n_urls)
    data.append(len(list(domains.keys())))
    data.append(sum(tweets_with_url[i] for i in range(1, len(tweets_with_url))))
    data.append(retweets)
    data.append(replies)
    data.append(len(list(documents.keys())))

    table_f.write('\t'.join(headers) + '\n')
    table_f.write('\t'.join(map(str, data)) + '\n')


    for f in files:
        f.close()
