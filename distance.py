from sklearn.metrics.pairwise import cosine_similarity
from scipy import spatial
import numpy as np

doc_dict={}
tweet_dict={}
m_tf_idf=[]
size_p=0.1
bucket_p=0.1
content_p=0.1
def size_bucket(bucket_1,bucket_2):
	size_bucket1=len(bucket_1)
	size_bucket2=len(bucket_2)
	delta=abs(size_bucket1-size_bucket2)
	k=1 #cte de proporcionalidad
	return k*min(size_bucket1,size_bucket2)/delta

def bucket_distance(bucket_1,bucket_2):
	tweets_bucket1=tweet_dict[bucket_1]
	tweets_bucket2=tweet_dict[bucket_2]
	tf_idf_bucket1=[m_tf_idf[i] for i in tweets_bucket1]
	tf_idf_bucket2=[m_tf_idf[i] for i in tweets_bucket2]
	distances=content_distance(tf_idf_bucket1,tf_idf_bucket2)
	return np.amax(distances)

def content_distance(tf_idf_tweet1,tf_idf_tweet2):
	if len(tf_idf_tweet2.shape)==1:
		return spatial.distance.cosine(tf_idf_tweet1,tf_idf_tweet2)
	else:
		return cosine_similarity(tf_idf_tweet1,tf_idf_tweet2)

def tweet_distance(tweet_1,tweet_2):
	bucket_1=doc_dict[tweet_1]
	bucket_2=doc_dict[tweet_2]
	if bucket_1 == bucket_2:
		return 0
	else:
		tf_idf_tweet1=m_tf_idf[tweet_1]
		tf_idf_tweet1=m_tf_idf[tweet_2]
		return size_p*size_bucket(bucket_1,bucket_2)+bucket_p*bucket_distance(bucket_1,bucket_2)+content_p*content_distance(tf_idf_tweet1,tf_idf_tweet2)