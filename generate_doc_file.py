import datetime
import os

from collections import defaultdict
from sqlalchemy.orm import sessionmaker

import models
from clustering import process_texts

from settings import engine

event_name = 'oscar_pistorius'
texts, documents = process_texts(event_name)

Session = sessionmaker(bind=engine, autocommit=True)
session = Session()

docs_id = defaultdict(list)
for doc in documents:
    docs_id[doc.tweet_id] = [doc.tweet_id,doc.total_rts, doc.total_favs, doc.total_replies, doc.total_tweets]

tweets = session.query(models.Tweet).filter(models.Tweet.tweet_id.in_(docs_id.keys())).all()
tweets_day = defaultdict(list)
for tweet in tweets:
    day = tweet.created_at.day
    month = tweet.created_at.month
    year = tweet.created_at.year
    date = datetime.datetime(year,month,day)
    tweet_info = docs_id[tweet.tweet_id]
    tweet_info.append(tweet.text)
    tweets_day[str(date)].append(tweet_info)

directory = 'data/'+event_name+'/'+event_name
directory_attr = 'data/'+event_name+'/attr'
if not os.path.exists(directory):
    os.makedirs(directory)

if not os.path.exists(directory_attr):
    os.makedirs(directory_attr)

file_list = open(directory+'/filelist_'+event_name+'.txt','w')
for key,value in tweets_day.items():
    file = open(directory+'/' + event_name + '_' + key[0:10] + '.txt', 'w')
    file_doc_attr = open(directory_attr+'/'+event_name+ '_' + key[0:10] + '_attr.txt', 'w')
    file_list.write("%s\n" % file.name[len(directory)+1:])
    for text in value:
        for attr in text:
            file_doc_attr.write(str(attr)+'\t')
        file_doc_attr.write('\n')
        file.write("%s\n" % text[5])
    file.close()
    file_doc_attr.close()

file_list.close()
