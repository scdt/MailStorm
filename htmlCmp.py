import os
import html2text as h2t
import re
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer


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


def trainAndTest():
    train_htmls = []
    train_htmls_new1 = []
    train_htmls_new2 = []
    train_htmls_new3 = []
    test_htmls = []
    test_htmls_new1 = []
    test_htmls_new2 = []
    for file in os.scandir('train_pages_cmp'):
        filename = os.fsdecode(file)
        if filename.endswith('.html'):
            if filename.find('NoReg.') != -1:
                with open(filename) as file1:
                    train_htmls.append(file1.read())
                with open(filename[:-5] + '1.html') as file2:
                    train_htmls_new1.append(file2.read())
                with open(filename[:-5] + '2.html') as file3:
                    train_htmls_new2.append(file3.read())
                with open(filename[:-5] + '3.html') as file4:
                    train_htmls_new3.append(file4.read())

    for file in os.scandir('test_pages_cmp'):
        filename = os.fsdecode(file)
        if filename.endswith('.html'):
            if filename.find('NoReg.') != -1:
                with open(filename) as file1:
                    test_htmls.append(file1.read())
                with open(filename[:-5] + '1.html') as file2:
                    test_htmls_new1.append(file2.read())
                with open(filename[:-5] + '2.html') as file3:
                    test_htmls_new2.append(file3.read())

    print("train text cmp new1 and new2")
    for html, html_new in zip(train_htmls_new1, train_htmls_new2):
        text = htmlToText(html)
        text_new = htmlToText(html_new)
        if(text == text_new):
            print('same text')
    print("train text cmp new2 and new3")
    for html, html_new in zip(train_htmls_new2, train_htmls_new3):
        text = htmlToText(html)
        text_new = htmlToText(html_new)
        if(text == text_new):
            print('same text')
    print("train text cmp new1 and new3")
    for html, html_new in zip(train_htmls_new1, train_htmls_new3):
        text = htmlToText(html)
        text_new = htmlToText(html_new)
        if(text == text_new):
            print('same text')

    print("test text cmp new1 and new2")
    for html, html_new in zip(test_htmls_new1, test_htmls_new2):
        text = htmlToText(html)
        text_new = htmlToText(html_new)
        if(text == text_new):
            print('same text')


if __name__ == '__main__':
    trainAndTest()
