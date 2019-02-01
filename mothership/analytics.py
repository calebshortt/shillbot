
import re

from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline


class DataAnalyzer(object):

    data_queue = None
    stop_words = None
    categories = ['shill', 'not shill']

    def __init__(self):
        try:
            print('Checking if NLTK libraries are installed and installing if necessary...')
            import nltk
            nltk.download('stopwords')
            nltk.download('punkt')
            self.stop_words = set(stopwords.words('english'))
            print('Done.')
        except Exception:
            print('Could not import required NLTK files. Exiting.')
            exit(0)

    def parse_data(self, data):

        """
        Assumes given data is testing and not training the classification model
        :param data:
        :return:
        """

        posts = data.get('data', [])
        word_counts = {}

        corpus = []

        for post in posts:

            title, subreddit, post_text, post_link, post_author = post
            post_text = str(post_text).lower()
            corpus.append(post_text)
        #     words = re.findall(r'\w+', post_text)
        #     keywords = [w for w in words if w not in self.stop_words]
        #
        #     for keyword in keywords:
        #         count = word_counts.get(keyword, 0)
        #         count += 1
        #         word_counts[keyword] = count
        #
        # sorted_word_counts = sorted(word_counts, key=word_counts.__getitem__, reverse=True)

        count_vect = CountVectorizer(stop_words='english')
        X_test_counts = count_vect.fit_transform(corpus)

        tfidf_transformer = TfidfTransformer(use_idf=False)
        X_test_tfidf = tfidf_transformer.fit_transform(X_test_counts)



        test = "test"







