import re
import os
import numpy as np
import catboost
import html2text as h2t
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics import f1_score, precision_score, recall_score
from catboost import CatBoostClassifier
from sklearn.neighbors import KNeighborsClassifier
import pickle


def htmlToText(html):
    h = h2t.HTML2Text()
    h.ignore_links = True
    text = h.handle(html)
    # text = re.sub(r'\*\s+.*|#+\s*.*', '', text)
    # text = re.sub(r'!\S+', '', text)
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


def nbTrain():
    train_htmls = []
    train_classes = []
    for file in os.scandir('train_pages/non_reg/'):
        filename = os.fsdecode(file)
        with open(filename) as file1:
            train_htmls.append(file1.read())
            train_classes.append(0)
    for file in os.scandir('train_pages/reg/'):
        filename = os.fsdecode(file)
        with open(filename) as file1:
            train_htmls.append(file1.read())
            train_classes.append(1)

    train_texts = []
    for html in train_htmls:
        train_texts.append(htmlToText(html))

    vectorizer = TfidfVectorizer()
    train_set = vectorizer.fit_transform(train_texts)

    # weights = 'distance' # algorithm{‘auto’, ‘ball_tree’, ‘kd_tree’, ‘brute’}
    clfNB = KNeighborsClassifier(n_neighbors=5, weights='uniform')
    clfNB.fit(X=train_set.toarray(), y=train_classes)
    saved_vect = open('./ml/nb/saved_vect', 'wb')
    pickle.dump(vectorizer, saved_vect)
    saved_vect.close()
    saved_model = open('./ml/nb/saved_clf', 'wb')
    pickle.dump(clfNB, saved_model)
    saved_model.close()


def cbTrain():
    train_htmls = []
    train_classes = []
    for file in os.scandir('train_pages/non_reg/'):
        filename = os.fsdecode(file)
        with open(filename) as file1:
            train_htmls.append(file1.read())
            train_classes.append(0)
    for file in os.scandir('train_pages/reg/'):
        filename = os.fsdecode(file)
        with open(filename) as file1:
            train_htmls.append(file1.read())
            train_classes.append(1)

    train_texts = []
    for html in train_htmls:
        train_texts.append(htmlToText(html))

    vectorizer = CountVectorizer()
    train_set = vectorizer.fit_transform(train_texts)

    clfCB = CatBoostClassifier(iterations=100, learning_rate=3, depth=7)
    clfCB.fit(X=train_set.toarray(), y=train_classes)
    saved_vect = open('./ml/cb/saved_vect', 'wb')
    pickle.dump(vectorizer, saved_vect)
    saved_vect.close()
    saved_model = open('./ml/cb/saved_clf', 'wb')
    pickle.dump(clfCB, saved_model)
    saved_model.close()
    '''
    predictMNB = clfMNB.predict(test_set)
    predictLSVC = clfLSVC.predict(test_set)
    predictCB = clfCB.predict(test_set.toarray())
    
    print('f1_scoreMNB:', f1_score(test_classes, predictMNB))
    print('precision_scoreMNB:', precision_score(test_classes, predictMNB))
    print('recall_scoreMNB:', recall_score(test_classes, predictMNB))
    print('f1_scoreLSVC:', f1_score(test_classes, predictLSVC))
    print('precision_scoreLSVC:', precision_score(test_classes, predictLSVC))
    print('recall_scoreLSVC:', recall_score(test_classes, predictLSVC))
    
    print('f1_scoreCB:', f1_score(test_classes, predictCB))
    print('precision_scoreCB:', precision_score(test_classes, predictCB))
    print('recall_scoreCB:', recall_score(test_classes, predictCB))
    '''


def CBclassifier(input_dir):
    saved_model = open('./ml/cb/saved_clf', 'rb')
    clfCB = pickle.load(saved_model)
    saved_vect = open('./ml/cb/saved_vect', 'rb')
    vectorizer = pickle.load(saved_vect)
    htmls = []
    filenames = []
    for file in os.scandir(input_dir):
        filename = os.fsdecode(file)
        filenames.append(filename)
        with open(file) as file1:
            htmls.append(file1.read())
    texts = []
    for html in htmls:
        texts.append(htmlToText(html))
    test_set = vectorizer.transform(texts)
    predict = clfCB.predict(test_set.toarray())
    # вывод
    for file, p in zip(filenames, predict):
        print(file)
        if p:
            print('Yes')
        else:
            print("No")
    return


def NBclassifier(input_dir):
    saved_model = open('./ml/nb/saved_clf', 'rb')
    clfNB = pickle.load(saved_model)
    saved_vect = open('./ml/nb/saved_vect', 'rb')
    vectorizer = pickle.load(saved_vect)
    htmls = []
    filenames = []
    for file in os.scandir(input_dir):
        filename = os.fsdecode(file)
        filenames.append(filename)
        with open(file) as file1:
            htmls.append(file1.read())
    texts = []
    for html in htmls:
        texts.append(htmlToText(html))
    test_set = vectorizer.transform(texts)
    predict = clfNB.predict(test_set.toarray())
    # вывод
    for file, p in zip(filenames, predict):
        print(file)
        if p:
            print('Yes')
        else:
            print("No")
    return
