# For a specific cluster calculate the distribution of time intervals beteween the tweets
# 54,25
from collections import defaultdict
from tqdm import tqdm

import db_utils
import numpy as np
from models import Tweet, DocumentTweet, Cluster

clustering = 54  # El id de clustering jerarquico


def return_intersection(hist_1, hist_2):
    minima = np.minimum(hist_1, hist_2)
    intersection = np.true_divide(np.sum(minima), np.sum(hist_2))
    return intersection


# Calculate the score of a histogram as the linear combination of the bins
def linear_combination(histogram):
    return 0.4 * histogram[0] + 0.3 * histogram[1] + 0.175 * histogram[2] + 0.125 * histogram[3]

#Calculate the histogram of time frecuency
def calculate_time_histogram(clustering, topic, n_clusters):
    docs = db_utils.get_documents_cluster(clustering, n_clusters)
    topic_dict = defaultdict(list)

    for doc in docs:
        topic_dict[doc[0]].append(doc[1])
    specific_topic = topic_dict[topic]
    docs_id = [doc.id for doc in specific_topic]
    tweets = db_utils.session.query(DocumentTweet.tweet_id).filter(DocumentTweet.document_id.in_(docs_id)).all()

    tweets = [x[0] for x in tweets]
    dates = db_utils.session.query(Tweet.created_at).filter(Tweet.tweet_id.in_(tweets)).all()

    differences = []
    dates.sort(key=lambda x: x[0], reverse=True)

    for i in range(len(dates) - 1):
        minutes_diff = dates[i][0] - dates[i + 1][0]
        differences.append(round(minutes_diff.total_seconds(), -1))
    differences.sort()
    histogram, bins = np.histogram(differences, bins=45, range=(0, 1080))

    return histogram

def rank(histograms, score = True):
    ranking = []
    for cluster, histogram in histograms.items():
        ranking.append((cluster, histogram[0]))

    ranking.sort(key=lambda x: x[1], reverse=True)
    ranking.append((-1,0))
    if score:
        ranking = [x[0] for x in ranking]
    return ranking

# n_cluster = db_utils.session.query(Cluster.n_clusters).filter(Cluster.id == clustering).first()
#
# histograms = {}
# for j in tqdm(range(n_cluster[0])):
#     histograms[j] = calculate_time_histogram(clustering, j)

#print(rank(histograms))