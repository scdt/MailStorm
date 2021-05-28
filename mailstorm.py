#! /usr/bin/python3
import getopt
import sys
import colored
import random
from catBoostHtmlClassifier import CatBoostHtmlClassifier
from kNeighboursHtmlClassifier import KNeighboursHtmlClassifier
from htmlParser import HtmlParser
from webSelenium import WebSelenium

email2 = 'emailexample2@inbox.lv'
email3 = 'emailexample3@inbox.lv'


def main():
    motd = open('./motd', 'r')
    banner = motd.read()
    motd.close()
    style = colored.fg(random.choice(['red', 'blue', 'green']))
    print(colored.stylize(banner, style))
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hfdao:e:u:1:2:i:m:c:", ["help", "full", "download", "analyze", "output-dir=", "email=", "urls=", "input-dir1=", "input-dir2=", "input-dir=", "method=", "clf_dir"])
    except getopt.GetoptError as err:
        print(err)
        sys.exit(2)

    output_dir = None
    email = None
    nr_dir1 = None
    nr_dir2 = None
    input_dir = None
    input_dir1 = None
    method = None
    clf_dir = None

    if not opts:
        print('Options required, try -h or --help for more information')
        return

    o, a = opts[0]
    if o in ("-h", "--help"):
        print("Usefull information")
    elif o in ("-f", "--fit"):
        for o, a in opts[1:]:
            if o in ("-1", "--input-dir1"):
                input_dir = a
            elif o in ("-2", "--input-dir2"):
                input_dir1 = a
            elif o in ("-o", "--output_dir"):
                output_dir = a
            elif o in ("-m", "--method"):
                method = a
            else:
                assert False, "unhandled option for fit"
        if method == "cb":
            CatBoostHtmlClassifier.fit(input_dir, input_dir1, output_dir)
        elif method == "nb":
            KNeighboursHtmlClassifier.fit(input_dir, input_dir1, output_dir)
        else:
            assert False, "method not specified"

    elif o in ("-d", "--download"):
        for o, a in opts[1:]:
            if o in ("-o", "--output-dir"):
                output_dir = a
            elif o in ("-e", "--email"):
                email = a
            elif o in ("-u", "--urls"):
                urls = a
            else:
                assert False, "unhandled option for download"
        WebSelenium.saveHtmls(email, urls, output_dir)
    elif o in ("-a", "--analyze"):
        for o, a in opts[1:]:
            if o in ("-1", "--input-dir1"):
                nr_dir1 = a
            elif o in ("-2", "--input-dir2"):
                nr_dir2 = a
            elif o in ("-i", "--input-dir"):
                input_dir = a
            elif o in ("-c", "--clf_dir"):
                clf_dir = a
            elif o in ("-m", "--method"):
                method = a
            else:
                assert False, "unhandled option for analyze"
        if method == "1":
            HtmlParser.htmlCmp(nr_dir1, nr_dir2, input_dir)
        elif method == "cb":
            CatBoostHtmlClassifier.predict(input_dir, clf_dir)
        elif method == "nb":
            KNeighboursHtmlClassifier.predict(input_dir, clf_dir)
        else:
            assert False, "method not specified"
    else:
        assert False, "unhandled option"


if __name__ == "__main__":
    main()
