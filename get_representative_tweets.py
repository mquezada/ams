from collections import defaultdict

import pickle
from pathlib import Path

import requests

def get_representative(path_clusters,path_docs,event_name, type):
    dict_docs = defaultdict(list)
    with path_clusters.open() as clusters, path_docs.open() as docs:
        for cluster, doc in zip(clusters,docs):
            dict_docs[int(cluster.rstrip())].append(doc.split('\t'))
        clusters.close()
        docs.close()

    dict_path = Path('data',event_name,'clusters',type,'dict_topic_'+str(len(dict_docs.keys()))+'.pickle')
    with dict_path.open('wb') as f:
        f.write(pickle.dumps(dict_docs))

    return dict_docs

def get_tweets(sorted_doc):
    url = 'https://publish.twitter.com/oembed?url=https://twitter.com/Interior/status/'
    tweet_dict = defaultdict(list)

    for doc in sorted_doc:
        id = doc[1]
        response = requests.get(url+id)
        try:
            json = response.json()
            if 'error' not in json:
                tweet_dict[id] = json['html']
        except ValueError as e:
            print("Tweet no encontrado")
            continue

    return tweet_dict