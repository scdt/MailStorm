import os
import pickle
from htmlParser import HtmlParser
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import KNeighborsClassifier
from htmlClassifier import HtmlClassifier


class KNeighboursHtmlClassifier(HtmlClassifier):

    def fit(input_dir_non_reg='train_pages/non_reg/', input_dir_reg='train_pages/reg', output_dir='ml/nb'):
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

        vectorizer = TfidfVectorizer()
        train_set = vectorizer.fit_transform(train_texts)

        clfNB = KNeighborsClassifier(n_neighbors=5, weights='uniform')
        clfNB.fit(X=train_set.toarray(), y=train_classes)
        saved_vect = open(output_dir + '/saved_vect_nb', 'wb')
        pickle.dump(vectorizer, saved_vect)
        saved_vect.close()
        saved_model = open(output_dir + '/saved_clf_nb', 'wb')
        pickle.dump(clfNB, saved_model)
        saved_model.close()

    def predict(input_dir, clf_dir="ml/nb"):
        saved_model = open(clf_dir + "/saved_clf_nb", 'rb')
        clfNB = pickle.load(saved_model)
        saved_vect = open(clf_dir + "/saved_vect_nb", 'rb')
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
        predict = clfNB.predict(test_set.toarray())
        for file, p in zip(filenames, predict):
            print(file)
            if p:
                print('Yes')
            else:
                print("No")
        return
