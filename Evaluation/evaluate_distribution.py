import re
from pathlib import Path

import dit
from dit.divergences import jensen_shannon_divergence
from nltk import TweetTokenizer, FreqDist
from nltk.corpus import stopwords
from tqdm import tqdm

from Evaluation.automatic_evaluation import calculate_vocab_distribution, calculate_most_popular
from db_utils import get_tweets, get_event_ids
from settings import LOCAL_DATA_DIR_2


'''
Evaluate the distribution of words in a event, comparing the all the tweets of an event with the timeline.
'''

tknzr = TweetTokenizer()

path = '/home/luism/PycharmProjects/ams/Embeddings/model.vec'


def calculate_distribution_event(event_name):
    event_ids = get_event_ids(event_name)
    tweets = get_tweets(event_ids)
    text = '\n'
    for tweet in tweets:
        tweet_text = re.sub(r"@\w+", '', re.sub(r"http\S+", '', tweet.text.replace('#', '')))
        text += tweet_text + '\n'
    words, distribution, pairs = calculate_vocab_distribution(text)
    return words, distribution, pairs


def calculate_distribution_timeline(event_name, timeline):
    reference = Path(LOCAL_DATA_DIR_2, 'data', event_name, 'summaries', 'reference', timeline)
    with reference.open('r') as f:
        words, distribution, pairs = calculate_vocab_distribution(f.read())
        # print(pairs)
    return words, distribution, pairs


def global_distribution(references_list):
    total_reference = ''
    for reference in references_list:
        with reference.open() as f:
            total_reference = total_reference + f.read()
    words, probs, pairs = calculate_vocab_distribution(total_reference)
    total_distribution = dit.ScalarDistribution(words, probs)
    return total_distribution, words


def evaluate_coverage_tweets(event, n_words):
    print('-------- {} ------------'.format(event))
    summaries_path = Path(LOCAL_DATA_DIR_2, 'data', event,'summaries','system')
    summaries = [x for x in summaries_path.iterdir() if x.is_file()]
    words, distribution, pairs = calculate_distribution_event(event)
    print(words[:n_words])
    for summary in summaries:
        with open(summary, 'r') as summary_file:
            print(summary_file.name)
            text_summary = summary_file.read()
            popular_summary = calculate_most_popular(text_summary, n_words)
            popular_words = [x[0] for x in popular_summary]
            print(popular_words)
            print(float(len(set(words[:n_words]) & set(popular_words))) / len(set(words[:n_words]) | set(popular_words)))


def evaluate_distibution(event_name):
    print(event_name)
    words_event, distribution_event, pairs_event = calculate_distribution_event(event_name)
    path_references = Path(LOCAL_DATA_DIR_2, 'data', event_name, 'summaries', 'reference')
    references_list = [reference for reference in path_references.iterdir() if reference.is_file()]
    event_dist = dit.ScalarDistribution(words_event, distribution_event)
    words_set_event = set(words_event[:10])
    print('Most Common words in event: {}'.format(words_set_event))
    total_dist, all_words = global_distribution(references_list)
    all_words_set = set(all_words[:10])
    jaccard = len(words_set_event.intersection(all_words_set)) / len(words_set_event.union(all_words_set))
    print('Most Common words in all timelines: {}'.format(all_words_set))
    print('Jaccard Index with all timelines: {}'.format(jaccard))
    print('Jensen-Shannon with all timelines: {}'.format(jensen_shannon_divergence([total_dist, event_dist])))
    for reference in references_list:
        words_timeline, probs_timeline, pairs_timeline = calculate_distribution_timeline(event_name, reference)
        dist_timeline = dit.ScalarDistribution(words_timeline, probs_timeline)
        print('----------------------------')
        word_set_timeline = set(words_timeline[:10])
        print(reference.name)
        print('Most Common words in timeline: {}'.format(word_set_timeline))
        print('Jensen-Shannon: {}'.format(jensen_shannon_divergence([dist_timeline, event_dist])))
        jaccard = len(words_set_event.intersection(word_set_timeline)) / len(words_set_event.union(word_set_timeline))
        print('Jaccard Index: {}'.format(jaccard))


if __name__ == '__main__':
    n_words = [10, 15, 20, 25]
    for n_word in n_words:
        print('n_words: {}'.format(n_word))
        evaluate_coverage_tweets('oscar_pistorius', n_word)
        evaluate_coverage_tweets('libya_hotel', n_word)
        evaluate_coverage_tweets('nepal_earthquake', n_word)
    #evaluate_distibution('libya_hotel')
    #evaluate_distibution('oscar_pistorius')
    #evaluate_distibution('nepal_earthquake')
