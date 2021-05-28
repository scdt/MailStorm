import os
import pickle
from htmlParser import HtmlParser
from sklearn.feature_extraction.text import CountVectorizer
from catboost import CatBoostClassifier
from htmlClassifier import HtmlClassifier


class CatBoostHtmlClassifier(HtmlClassifier):

    def fit(input_dir_non_reg='train_pages/non_reg/', input_dir_reg='train_pages/reg', output_dir='ml/cb'):
        train_htmls = []
        train_classes = []
        for file in os.scandir(input_dir_non_reg):
            filename = os.fsdecode(file)
            with open(filename) as file1:
                train_htmls.append(file1.read())
                train_classes.append(0)
        for file in os.scandir(input_dir_reg):
            filename = os.fsdecode(file)
            with open(filename) as file1:
                train_htmls.append(file1.read())
                train_classes.append(1)

        train_texts = []
        for html in train_htmls:
            train_texts.append(HtmlParser.htmlToText(html))

        vectorizer = CountVectorizer()
        train_set = vectorizer.fit_transform(train_texts)

        clfCB = CatBoostClassifier(iterations=100, learning_rate=3, depth=7)
        clfCB.fit(X=train_set.toarray(), y=train_classes)
        saved_vect = open(output_dir + '/saved_vect_cb', 'wb')
        pickle.dump(vectorizer, saved_vect)
        saved_vect.close()
        saved_model = open(output_dir + '/saved_clf_cb', 'wb')
        pickle.dump(clfCB, saved_model)
        saved_model.close()

    def predict(input_dir, clf_dir="ml/cb"):
        saved_model = open(clf_dir + "/saved_clf_cb", 'rb')
        clfCB = pickle.load(saved_model)
        saved_vect = open(clf_dir + "/saved_vect_cb", 'rb')
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
            texts.append(HtmlParser.htmlToText(html))
        test_set = vectorizer.transform(texts)
        predict = clfCB.predict(test_set.toarray())
        for file, p in zip(filenames, predict):
            print(file)
            if p:
                print('Yes')
            else:
                print("No")
        return
