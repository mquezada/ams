from collections import defaultdict
from os import listdir
from os.path import isfile, join
from operator import itemgetter

number_topics = 8
event_name = 'nepal_earthquake'
path_to_docs = '/home/luism/Universidad/ams/By_Day/'+event_name+'/TextWithLabel/'
path_to_attr = 'data/'+event_name+'/attr/'

docs = [f for f in listdir(path_to_docs) if isfile(join(path_to_docs, f))]
attr = [f for f in listdir(path_to_docs) if isfile(join(path_to_attr, f))]

def count_topic_words(text, k):
    count = 0
    count_topic = [0]*number_topics
    tokens = text.strip().split(' ')
    for token in tokens:
        t = token[token.index('/') + 1:]
        if not t.isdigit() and t != 'false':
            continue
        if t != 'false' and int(t) == k:
            count += 1
            count_topic[t] +=1
        else:
            count -=0
    return count

dic_topic = defaultdict(list)
for doc in docs:
    file_doc = open(path_to_docs+doc,'r')
    file_attr = open(path_to_attr+doc[:-4]+'_attr.txt')
    for line, attrs in zip(file_doc, file_attr):
        attr = attrs.split('\t')
        tweet = line.split('  ')[1]
        topic = line.split('\t')[1][2]
        attr.append(tweet)
        if len(attr) < 8:
            continue
        dic_topic[topic].append(attr)

print('total_rt','total_favs','total_replies','total_tweets')
for key, value in dic_topic.items():
    scores = dic_topic[key]
    scores.sort(key=lambda x: int(x[1]), reverse=True)
    for selected in scores[:5]:
        print(key,selected[1:6])
    print('------------------------')