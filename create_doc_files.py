import collections
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

from models import Tweet
from settings import Datasets, engine
import re



Session = sessionmaker(bind=engine, autocommit=True, expire_on_commit=False)
session = Session()
tweets = session.query(Tweet).filter(Tweet.event_id_id.in_(Datasets.oscar_pistorius)).all()

text_doc = {}
for tweet in tqdm(tweets, desc="Concateing Documents..."):
    text = re.sub(r"http\S+", "", tweet.text)
    doc_id = tweet.document_id
    value = text_doc.get(doc_id)
    if value == None:
        text_doc[doc_id] = text
    else:
        text_doc[doc_id] = text_doc[doc_id] +"\n" +text

#text_doc=[text_doc[i] for i in range(len(text_doc)) if len(text_doc[i])>1260]
text_doc_filter = {k: v for k, v in text_doc.items() if len(v) > 1120}
od_text_doc = collections.OrderedDict(sorted(text_doc_filter.items()))
file_list = open('data/docs/filelist_docs.txt','w')
for key, text in od_text_doc.items():
    name = 'doc_'+str(key)+'.txt\n'
    file = open('data/docs/doc_'+str(key)+'.txt','w')
    file.write(text)
    file_list.write(name)
    file.close()