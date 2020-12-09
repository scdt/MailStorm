import re
import os
import numpy as np
import html2text as h2t
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score
from sklearn.svm import LinearSVC


def htmlToText(html):
    h = h2t.HTML2Text()
    h.ignore_links = True
    text = h.handle(html)
    # text = re.sub(r'\*\s+.*|#+\s*.*', '', text)
    #text = re.sub(r'!\S+', '', text)
    text = re.sub(r'\S.jpeg|\S.jpg|\S.svg|\S.png', '', text)
    text = text.lower()
    text = text.replace("'", ' ')
    text = re.sub(r'[^a-z\s]', '', text)
    text = re.sub(r'\n{2,}', '\n', text)
    ps = PorterStemmer()
    text = ps.stem(text)
    stop_words = set(stopwords.words('english'))
    stop_words.difference_update({'should', 'no', 'not'})
    stop_words.update({'one', 'distribution', 'ace', 'rewards', 'cookies', 'create', 'online', 'music', 'youtube', 'english',
                       'video', 'privacy', 'terms', 'upload', 'new', 'love', 'espaol', 'portugus', 'streaming', 'log'})
    for word in text.split():
        if(word in stop_words):
            text = re.sub(rf'\b{word}\b', '', text)
    text = re.sub(r'\s{2,}', ' ', text)
    return text


def trainAndTest():
    train_htmls = []
    test_htmls = []
    train_classes = []
    test_classes = []
    for file in os.scandir('train_pages'):
        filename = os.fsdecode(file)
        if filename.endswith('.html'):
            with open(filename) as file1:
                train_htmls.append(file1.read())
                if(filename.find('NoReg') == -1):
                    train_classes.append(1)
                else:
                    train_classes.append(0)
    for file in os.scandir('test_pages'):
        filename = os.fsdecode(file)
        if filename.endswith('.html'):
            with open(filename) as file1:
                test_htmls.append(file1.read())
                if(filename.find('NoReg') == -1):
                    test_classes.append(1)
                else:
                    test_classes.append(0)
    print('train files:', len(train_htmls))
    print('test files:', len(test_htmls))
    train_texts = []
    test_texts = []
    for html in train_htmls:
        train_texts.append(htmlToText(html))
    for html in test_htmls:
        test_texts.append(htmlToText(html))
    vectorizer = TfidfVectorizer(max_features=200)
    train_set = vectorizer.fit_transform(train_texts)
    test_set = vectorizer.transform(test_texts)
    clf = LinearSVC('l2', 'hinge', dual=True, fit_intercept=True)
    clf.fit(X=train_set, y=train_classes)
    predict_train = clf.predict(train_set)
    predict = clf.predict(test_set)
    print('accuracy_train:', accuracy_score(train_classes, predict_train))
    print('accuracy_test:', accuracy_score(test_classes, predict))


if __name__ == '__main__':
    trainAndTest()
