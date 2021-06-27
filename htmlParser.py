import os
import html2text as h2t
import re
from nltk.corpus import stopwords


class HtmlParser():

    def htmlToText(html):
        h = h2t.HTML2Text()
        h.ignore_links = True
        text = h.handle(html)
        text = re.sub(r'\*\s+.*|#+\s*.*', '', text)
        text = re.sub(r'!\S+', '', text)
        text = re.sub(r'\S.jpeg|\S.jpg|\S.svg|\S.png', '', text)
        text = text.lower()
        text = text.replace("'", ' ')
        text = re.sub(r'[^a-z\s]', '', text)
        text = re.sub(r'\n{2,}', '\n', text)
        stop_words = set(stopwords.words('english'))
        stop_words.difference_update({'should', 'no', 'not'})
        stop_words.update({'one', 'distribution', 'ace', 'rewards', 'cookies', 'create', 'online', 'music', 'youtube', 'english',
                           'video', 'privacy', 'terms', 'upload', 'new', 'love', 'espaol', 'portugus', 'streaming', 'log'})
        for word in text.split():
            if(word in stop_words):
                text = re.sub(rf'\b{word}\b', '', text)
        text = re.sub(r'\s{2,}', ' ', text)
        text = re.sub(r'\n', ' ', text)
        return text

    def htmlCmp(nr_dir1, nr_dir2, a_dir):
        texts = []
        texts_nr1 = []
        texts_nr2 = []
        filenames = []
        for file in os.scandir(a_dir):
            filename = os.fsdecode(file)
            filenames.append(filename)
            with open(filename) as file1:
                texts.append(HtmlParser.htmlToText(file1.read()))
        for file in os.scandir(nr_dir1):
            filename = os.fsdecode(file)
            with open(filename) as file1:
                texts_nr1.append(HtmlParser.htmlToText(file1.read()))
        for file in os.scandir(nr_dir2):
            filename = os.fsdecode(file)
            with open(filename) as file1:
                texts_nr2.append(HtmlParser.htmlToText(file1.read()))
        for text, text1, text2, filename in zip(texts, texts_nr1, texts_nr2, filenames):
            print(filename)
            if text1 != text2:
                print("Even non registered are different")
            elif text != text1:
                print('Yes')
            else:
                print("Don't know")
