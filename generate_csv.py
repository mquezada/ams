from clustering import process_texts
import csv

event_name = 'libya_hotel'
path = 'data/'+event_name+'/'
texts, documents = process_texts(event_name)
with open(path+event_name+'.csv', 'w') as myfile:
    wr = csv.writer(myfile, delimiter = '\t', quoting=csv.QUOTE_ALL)
    for doc in documents:
        l = [doc.tweet_id, doc.url, doc]
        wr.writerow(l)