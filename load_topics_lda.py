from collections import defaultdict
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

from settings import engine

from os import listdir
from os.path import isfile, join

import models
import pickle
from pathlib import Path


def get_tweets(document_id: int, session):
    with session.begin():
        tweets = session.query(models.Tweet).filter_by(document_id=document_id).all()
    return tweets

paths = ['data/docs_T10/TextWithLabel/', 'data/docs_T25/TextWithLabel/', 'data/docs_T50/TextWithLabel/', 'data/docs_T75/TextWithLabel/', 'data/docs_T100/TextWithLabel/']

for path in tqdm(paths,'Agrupando Topicos'):
    tokens = path.split('/')
    files = [f for f in listdir(path) if isfile(join(path, f))]
    topic_doc = defaultdict(list)
    for file in tqdm(files,'Iterando archivos'):
        f = open(path+file,'r+')
        doc = file[file.index('_')+1:file.index('.')]
        topic_tweet = []
        for line in f:
            sub_line = line[13:]
            topic = sub_line[1:sub_line.index(':')]
            topic_tweet.append(topic)
        topic_doc[doc] = topic_tweet
        del topic_tweet

    Session = sessionmaker(bind=engine, autocommit=True, expire_on_commit=False)
    session = Session()

    topic_dic = defaultdict(list)
    for doc_id, tweet_topic in topic_doc.items():
        tweets = get_tweets(doc_id, session)
        for i in range(len(tweets)):
            topic_dic[tweet_topic[i]].append(tweets[i].tweet_id)

    dic_loc = Path('data','dict_'+tokens[1]+'.pickle')
    with dic_loc.open('wb') as f:
        f.write(pickle.dumps(topic_dic))