import os
import html2text as h2t
import re
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import gensim.models
from statistics import mean
from sklearn.neighbors import KNeighborsClassifier
from sklearn import svm
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score


def htmlToWords(html):
    h = h2t.HTML2Text()
    h.ignore_links = True
    text = h.handle(html)
    text = re.sub(r'\S.jpeg|\S.jpg|\S.svg|\S.png', '', text)
    text = text.lower()
    text = text.replace("can't", 'can not')
    text = text.replace("n't", ' not')
    text = text.replace("'", ' ')
    text = re.sub(r'[^a-z\s]', '', text)
    text = re.sub(r'[a-z]{20,}', '', text)
    ps = PorterStemmer()
    text = ps.stem(text)
    stop_words = set(stopwords.words('english'))
    stop_words.difference_update({'should', 'no', 'not', 'we', 'your', 'you', 'to'})
    stop_words.update({'one', 'distribution', 'ace', 'rewards', 'cookies', 'create', 'online', 'music', 'youtube', 'english',
                       'video', 'privacy', 'terms', 'upload', 'new', 'love', 'espaol', 'portugus', 'streaming', 'log'})
    text = text.split()
    text = [word for word in text if word not in stop_words]
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
    train_texts = []
    test_texts = []
    for html in train_htmls:
        train_texts.append(htmlToWords(html))
    for html in test_htmls:
        test_texts.append(htmlToWords(html))
    print('train texts:', len(train_texts))
    print('test texts:', len(test_texts))

    words_number = 100
    model = gensim.models.Word2Vec(sentences=train_texts, min_count=1, size=words_number)
    train_texts_vectors = []
    test_texts_vectors = []
    for text in train_texts:
        tmp = []
        for word in text:
            try:
                word_vector = model.wv[word]
                tmp.append(word_vector)
            except:
                pass
        text_vector = []
        for i in range(words_number):
            values = []
            for vector in tmp:
                values.append(vector[i])
            text_vector.append(mean(values))
        train_texts_vectors.append(text_vector)
    for text in test_texts:
        tmp = []
        for word in text:
            try:
                word_vector = model.wv[word]
                tmp.append(word_vector)
            except:
                pass
        text_vector = []
        for i in range(words_number):
            values = []
            for vector in tmp:
                values.append(vector[i])
            text_vector.append(mean(values))
        test_texts_vectors.append(text_vector)

    clfKN = KNeighborsClassifier(n_neighbors=3, weights='distance')
    clfSVC = svm.SVC()
    clfLinearSVC = svm.LinearSVC()
    clfKN.fit(train_texts_vectors, train_classes)
    clfSVC.fit(train_texts_vectors, train_classes)
    clfLinearSVC.fit(train_texts_vectors, train_classes)
    predictKN = clfKN.predict(test_texts_vectors)
    train_predictKN = clfKN.predict(train_texts_vectors)
    print('accuracy_test:', accuracy_score(test_classes, predictKN))
    print('accuracy_train:', accuracy_score(train_classes, train_predictKN))
    print('f1_scoreKN:', f1_score(test_classes, predictKN))
    print('precision_scoreKN:', precision_score(test_classes, predictKN))
    print('recall_scoreKN:', recall_score(test_classes, predictKN))
    predictSVC = clfSVC.predict(test_texts_vectors)
    train_predictSVC = clfSVC.predict(train_texts_vectors)
    print('accuracy_test:', accuracy_score(test_classes, predictSVC))
    print('accuracy_train:', accuracy_score(train_classes, train_predictSVC))
    print('f1_scoreSVC:', f1_score(test_classes, predictSVC))
    print('precision_scoreSVC:', precision_score(test_classes, predictSVC))
    print('recall_scoreSVC:', recall_score(test_classes, predictSVC))
    predictLinearSVC = clfLinearSVC.predict(test_texts_vectors)
    train_predictLinearSVC = clfLinearSVC.predict(train_texts_vectors)
    print('accuracy_test:', accuracy_score(test_classes, predictLinearSVC))
    print('accuracy_train:', accuracy_score(train_classes, train_predictLinearSVC))
    print('f1_scoreLinearSVC:', f1_score(test_classes, predictLinearSVC))
    print('precision_scoreLinearSVC:', precision_score(test_classes, predictLinearSVC))
    print('recall_scoreLinearSVC:', recall_score(test_classes, predictLinearSVC))


if __name__ == '__main__':
    trainAndTest()
