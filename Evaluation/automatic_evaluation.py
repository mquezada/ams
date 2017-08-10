'''
Do the automatic evaluation of the summaries.
Compare the selected tweets with a timeline extracted from internet.+
The summaries are in data/event_name/summaries/system, and the reference(gold standard) are
in data/event_name/summaries/reference
Calculate ROUGE, Jaccard and Jensen-Shannon
'''
import collections
import subprocess
from pathlib import Path

import dit
import jprops
from dit.divergences import jensen_shannon_divergence
from nltk import FreqDist
from nltk.corpus import stopwords
from nltk.stem.porter import *
from nltk.tokenize import TweetTokenizer

from tqdm import tqdm

from settings import LOCAL_DATA_DIR_2

stemmer = PorterStemmer()
tknzr = TweetTokenizer()


#from gensim.models import KeyedVectors

path = '/home/luism/PycharmProjects/ams/Embeddings/model.vec'
#w2v = KeyedVectors.load_word2vec_format(path)
w2v = object()

def calculate_most_popular(text, n_populars):
    fdist = calculate_fdist(text, True)
    term = []
    for key, value in fdist.items():
        term.append((key, value))
    term.sort(key=lambda x: int(x[1]), reverse=True)
    return term[:n_populars]


def compress_similar(text, treshold):
    populars = calculate_most_popular(text, 200)
    fdist_all = calculate_fdist(text)
    topn = 10
    fdist_similars = fdist_all.copy()
    count = 0
    for key, value in tqdm(fdist_all.items()):
        if (key, value) in populars:
            try:
                similars = [similar[0] for similar in w2v.most_similar(key, topn=topn) if similar[1] >= treshold]
                for similar in similars:
                    item_similar = fdist_similars.pop(similar)
                    if similar in fdist_all.keys() and similar not in fdist_similars.keys():
                        fdist_similars.update({key: item_similar + fdist_similars.get(key)})
                        count += 1
            except:
                continue
    print(count)
    return fdist_similars

def replace_similar(text, treshold):
    populars = calculate_most_popular(text, 200)
    topn = 10
    replaced = []
    for (word, count) in populars:
        try:
            if word not in replaced:
                similars = [similar[0] for similar in w2v.most_similar(word, topn=topn) if similar[1] >= treshold]
                for similar in similars:
                    text = text.replace(similar, word)
                    replaced.append(similar)
        except:
            continue
    return text


def calculate_fdist(text, steam=False):
    list_of_words = remove_and_stem(text, steam)
    fdist_all = FreqDist(list_of_words)
    return fdist_all


def remove_and_stem(text, steam=False):
    stop_words = set(stopwords.words('english'))
    stop_words.update(
        ['~', '.', ':', ',', ';', '?', '¿', '!', '¡', '...', '/', '\'', '\\', '\"', '-', 'amp', '&', 'rt', '[', ']',
         '":', '--&',
         '(', ')', '|', '*', '+', '%', '$', '_', '@', 's', 'ap', '=', '}', '{', '**', '--', '()', '!!', '::', '||',
         '.:', ':.', '".', '))', '((', '’'])
    if steam:
        list_of_words = [stemmer.stem(i.lower()) for i in tknzr.tokenize(text) if i.lower() not in stop_words]
    else:
        list_of_words = [i.lower() for i in tknzr.tokenize(text) if i.lower() not in stop_words]
    return list_of_words


'''Calculate the probability distribution of a text'''


def calculate_vocab_distribution(text):
    #fdist = compress_similar(text, 0.9)
    fdist = calculate_fdist(text, True)
    #text = replace_similar(text, 0.9)
    fdist = calculate_fdist(text, True)
    fdist = {k: v for k,v in fdist.items() if v > 1}
    len_vocab = sum(fdist.values())
    pairs = [(key, value/len_vocab) for key,value in fdist.items()]
    pairs.sort(key=lambda x: int(x[1]), reverse=True)
    return [x[0] for x in pairs], [x[1] for x in pairs], pairs


def create_distribution(event, reference_name, summary_name):
    path_reference = Path(LOCAL_DATA_DIR_2, 'data', event, 'summaries', 'reference', reference_name)
    path_summary = Path(LOCAL_DATA_DIR_2, 'data', event, 'summaries', 'system', summary_name)
    with path_reference.open('r') as reference, path_summary.open('r') as summary:
        reference_text = reference.read()
        summary_text = summary.read()
        summary_words, summary_probs, _ = calculate_vocab_distribution(summary_text)
        reference_words, reference_probs, _ = calculate_vocab_distribution(reference_text)
        summary_dist = dit.ScalarDistribution(summary_words, summary_probs)
        reference_dist = dit.ScalarDistribution(reference_words, reference_probs)
    return reference_dist, summary_dist


'''Computes the rouge score for all the summaries of an event, it will asume that the summaries are in
 event_name/summaries'''


def compute_rouge(event):
    summaries_path = Path(LOCAL_DATA_DIR_2, 'data', event, 'summaries')

    with open('rouge.properties', 'r+') as fp:
        props = jprops.load_properties(fp, collections.OrderedDict)
        ngrams = props.get('ngram')
        result_path = Path(LOCAL_DATA_DIR_2, 'data', event, 'summaries', 'result_rouge_ngram' + str(ngrams) + '.csv')
        props.pop('project.dir')
        props.pop('outputFile')
        props.update({'project.dir': str(summaries_path.absolute()), 'outputFile': str(result_path.absolute())})
        fp.seek(0)
        fp.truncate()
        jprops.store_properties(fp, props)

    subprocess.call(['java', '-jar', 'rouge2.0_0.2.jar', '-Drouge.prop=', 'rouge.properties'])


'''Computes the jensen shannon divergence for a summary and his timeline'''


def compute_jensen_shannon(event, reference_name, summary_name):
    reference_dist, summary_dist = create_distribution(event, reference_name, summary_name)
    return jensen_shannon_divergence([summary_dist, reference_dist])


def dist_jaccard(str1, str2):
    str1 = set(remove_and_stem(str1, True))
    str2 = set(remove_and_stem(str2, True))
    return float(len(str1 & str2)) / len(str1 | str2)


def compute_jaccard(event, reference_name, summary_name):
    path_reference = Path(LOCAL_DATA_DIR_2, 'data', event, 'summaries', 'reference', reference_name)
    path_summary = Path(LOCAL_DATA_DIR_2, 'data', event, 'summaries', 'system', summary_name)
    with path_reference.open('r') as reference, path_summary.open('r') as summary:
        reference_text = reference.read()
        summary_text = summary.read()
    return dist_jaccard(summary_text, reference_text), dist_jaccard(reference_text, summary_text)


def evaluate_event(event_name):
    print('-------------' + event_name + '--------------')

    compute_rouge(event_name)
    event_path = Path(LOCAL_DATA_DIR_2, 'data', event_name, 'summaries')
    references_path = Path(event_path, 'reference')
    summaries_path = Path(event_path, 'system')
    references = [x for x in references_path.iterdir() if x.is_file()]
    summaries = [x for x in summaries_path.iterdir() if x.is_file()]

    for reference in references:
        for summary in summaries:
            print('Jensen-Shannon Divergence: ')
            print(compute_jensen_shannon(event_name, reference.name, summary.name))
            print('Jaccard Distance')
            print(compute_jaccard(event_name, reference.name, summary.name))


if __name__ == '__main__':
    evaluate_event('libya_hotel')
    evaluate_event('oscar_pistorius')
