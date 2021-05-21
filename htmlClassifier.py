import os
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from catboost import CatBoostClassifier
from sklearn.neighbors import KNeighborsClassifier
import pickle
import htmlParser


class htmlClassifier():

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
            train_texts.append(htmlParser.htmlToText(html))

        vectorizer = TfidfVectorizer()
        train_set = vectorizer.fit_transform(train_texts)

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
            train_texts.append(htmlParser.htmlToText(html))

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
            texts.append(htmlParser.htmlToText(html))
        test_set = vectorizer.transform(texts)
        predict = clfCB.predict(test_set.toarray())
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
            texts.append(htmlParser.htmlToText(html))
        test_set = vectorizer.transform(texts)
        predict = clfNB.predict(test_set.toarray())
        for file, p in zip(filenames, predict):
            print(file)
            if p:
                print('Yes')
            else:
                print("No")
        return
