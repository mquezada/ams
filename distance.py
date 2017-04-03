import numpy as np
from create_tfidf import info_for_distance
from tqdm import tqdm, trange
from tabulate import tabulate


def size_bucket(bucket_1, bucket_2, max_scale):
    size_bucket1 = len(bucket_1)
    size_bucket2 = len(bucket_2)
    delta = abs(size_bucket1 - size_bucket2)
    k = 1 / max_scale  # cte de proporcionalidad
    return k * delta / min(size_bucket1, size_bucket2)


def bucket_distance(bucket_1, bucket_2, m_tf_idf):

    tf_idf_bucket1 = m_tf_idf[bucket_1]
    tf_idf_bucket2 = m_tf_idf[bucket_2]

    distances = content_distance(tf_idf_bucket1, tf_idf_bucket2)
    return np.amax(distances)


def content_distance(tf_idf_tweet1, tf_idf_tweet2):
    dot_prod = np.dot(tf_idf_tweet1, tf_idf_tweet2.T)
    return np.ones(shape=dot_prod.shape) - dot_prod


def tweet_distance(tweet_1,
                   tweet_2,
                   doc_dict,
                   tweet_dict,
                   m_tf_idf,
                   size_p = 0.5,
                   bucket_p = 0.3,
                   content_p = 0.2,
                   max_scale=1000):
    doc1 = doc_dict[tweet_1]
    doc2 = doc_dict[tweet_2]

    bucket_1 = tweet_dict[doc1]
    bucket_2 = tweet_dict[doc2]

    if doc1 == doc2:
        return 0
    else:
        tf_idf_tweet1 = m_tf_idf[tweet_1]
        tf_idf_tweet2 = m_tf_idf[tweet_2]
        return size_p * size_bucket(bucket_1, bucket_2, max_scale) + \
               bucket_p * bucket_distance(bucket_1, bucket_2, m_tf_idf) + \
               content_p * content_distance(tf_idf_tweet1, tf_idf_tweet2)


if __name__ == '__main__':
    m_tf_idf, doc_dict, tweet_dict = info_for_distance()

    lens = list(map(len, tweet_dict.values()))
    max_scale = max(lens) / min(lens)

    docs = [1, 5, 20, 4, 360, 302, 283, 270]
    all_dists = []

    for i in range(len(docs)):
        doc1 = docs[i]
        for j in range(i + 1, len(docs)):
            doc2 = docs[j]
            distances = []
            for t1 in tqdm(tweet_dict[doc1], desc=str((doc1, doc2))):
                for t2 in tweet_dict[doc2]:
                    # todo
                    d = tweet_distance(t1, t2)
                    distances.append(d)

            all_dists.append(((doc1, doc2),
                              np.min(distances),
                              np.mean(distances),
                              np.max(distances)))

    print(tabulate(all_dists, headers=["min", "avg", "max"]))

