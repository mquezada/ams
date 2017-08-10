from tqdm import tqdm

from clustering import process_texts
import csv

event_name = 'nepal_earthquake'
path = 'data/' + event_name + '/'
texts, documents = process_texts(event_name)
with open(path + event_name + '.csv', 'w') as myfile:
    wr = csv.writer(myfile, delimiter='\t', quoting=csv.QUOTE_MINIMAL)
    for doc in tqdm(documents):
        l = [doc.id, doc.tweet_id, doc.total_tweets, doc.total_rts, doc.total_replies, doc.total_favs,
             doc.url.replace('\t', ' ')]
        wr.writerow(l)
