from nltk.corpus import stopwords
from nltk.stem.snowball import PorterStemmer
from nltk.tokenize.casual import TweetTokenizer

import sys
import string

from load_dataset import load
from settings import engine, Datasets
import logging
from tqdm import tqdm
import nlp_utils
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse.csr import csr_matrix
from pandas.core.frame import DataFrame

logger = logging.getLogger(__name__)

def create_matrix(tweets_df: DataFrame) -> csr_matrix:
    stemmer = PorterStemmer()
    tokenizer = TweetTokenizer(preserve_case=False, strip_handles=True)

    texts = []
    for _, tweet in tqdm(tweets_df.iterrows(), total=tweets_df.shape[0], desc="Iterating over tweets"):
        text = tweet.text

        tokens = tokenizer.tokenize(text)
        text_proc = []
        for token in tokens:
            token = token.strip()
            if len(token) < 3:
                continue
            elif token in stopwords.words('english'):
                continue
            elif nlp_utils.match_url(token):
                continue
            elif token in string.punctuation:
                continue
            # elif token.startswith(("#", "$")):
            #     continue

            token = token.translate({ord(k): "" for k in string.punctuation})
            token = stemmer.stem(token)

            token = token.strip()
            if token == "":
                continue

            text_proc.append(token)

        texts.append(text_proc)

    vectorizer = TfidfVectorizer(analyzer="word", tokenizer=lambda x: x, lowercase=False)
    m = vectorizer.fit_transform(texts)
    return m


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s | %(levelname)s : %(message)s', level=logging.INFO, stream=sys.stdout)
    m = create_matrix()
