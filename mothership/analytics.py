
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer
from sklearn.linear_model import SGDClassifier
from sklearn.pipeline import Pipeline

from workers.basic_worker import BasicUserParseWorker
from settings import LABEL_SHILL, LABEL_NOTSHILL


class DataAnalyzer(object):

    data_queue = None
    stop_words = None
    categories = ['shill', 'not shill']

    classifier = None

    def __init__(self, shill_filepath, notshill_filepath):
        self.init_training(shill_filepath, notshill_filepath)

    def init_training(self, shill_filepath, notshill_filepath):

        content = []
        with open(shill_filepath, 'r') as f:
            content = f.readlines()
        shill_targets = [x.strip() for x in content]

        notshill_targets = []
        if notshill_filepath:
            with open(shill_filepath, 'r') as f:
                content = f.readlines()

            notshill_targets = [x.strip() for x in content]

        corpus = []
        for shill in shill_targets:
            worker = BasicUserParseWorker(shill)
            result, root = worker.run(training_label=LABEL_SHILL, local=True)
            corpus += result

        for notshill in notshill_targets:
            worker = BasicUserParseWorker(notshill)
            result, root = worker.run(training_label=LABEL_NOTSHILL, local=True)
            corpus += result

        self.train_classifier({'data': corpus})

    def train_classifier(self, data):

        posts = data.get('data', [])
        corpus = []
        training_labels = []

        for post in posts:
            title, subreddit, post_text, post_link, post_author, training_label = post
            post_text = str(post_text).lower()
            corpus.append(post_text)
            training_labels.append(training_label)

        count_vect = CountVectorizer(stop_words='english')
        X_train_counts = count_vect.fit_transform(raw_documents=corpus)

        tfidf_transformer = TfidfTransformer(use_idf=False)
        X_train_tfidf = tfidf_transformer.fit_transform(X_train_counts)
        print(X_train_tfidf.shape)

        docs_train = corpus

        self.classifier = Pipeline([
            ('vect', CountVectorizer(stop_words='english')),
            ('tfidf', TfidfTransformer(use_idf=True)),
            ('clf', SGDClassifier(loss='hinge', penalty='l2', alpha=1e-3, random_state=42, verbose=1)),
        ])

        self.classifier.fit(docs_train, training_labels)

    def classify_data(self, data):
        """
        Assumes given data is testing and not training the classification model.
        Assumes that the classifier is already trained and instantiated -- returns None otherwise
        :param data:
        :return:
        """

        if not self.classifier:
            print('Cannot classify data -- classifier not trained.')
            return

        posts = data.get('data', [])
        corpus = []

        for post in posts:

            title, subreddit, post_text, post_link, post_author, training_label = post
            post_text = str(post_text).lower()
            corpus.append(post_text)

        predictions = self.classifier.predict(corpus)

        print(predictions)







