#! /usr/bin/python3
import getopt
import sys
import colored
import random
import htmlClassifier
import htmlParser
import webSelenium

email2 = 'emailexample2@inbox.lv'
email3 = 'emailexample3@inbox.lv'


def main():
    motd = open('./motd', 'r')
    banner = motd.read()
    motd.close()
    style = colored.fg(random.choice(['red', 'blue', 'green']))
    print(colored.stylize(banner, style))
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hfdao:e:u:1:2:i:m:", ["help", "full", "download", "analyze", "output-dir=", "email=", "urls=", "input-dir-nr1=", "input-dir-nr2=", "input-dir=", "method="])
    except getopt.GetoptError as err:
        print(err)
        sys.exit(2)

    output_dir = None
    email = None
    nr_dir1 = None
    nr_dir2 = None
    input_dir = None
    method = None

    if not opts:
        print('Options required, try -h or --help for more information')
        return

    o, a = opts[0]
    if o in ("-h", "--help"):
        print("Usefull information")
    elif o in ("-f", "--full"):
        pass
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
        webSelenium.save_htmls(email, urls, output_dir)
    elif o in ("-a", "--analyze"):
        for o, a in opts[1:]:
            if o in ("-1", "--input-dir-nr1"):
                nr_dir1 = a
            elif o in ("-2", "--input-dir-nr2"):
                nr_dir2 = a
            elif o in ("-i", "--input-dir"):
                input_dir = a
            elif o in ("-m", "--method"):
                method = a
            else:
                assert False, "unhandled option for analyze"
        if method == "1":
            htmlParser.htmlCmp(nr_dir1, nr_dir2, input_dir)
        elif method == "cb":
            htmlClassifier.CBclassifier(input_dir)
        elif method == "nb":
            htmlClassifier.NBclassifier(input_dir)
        else:
            assert False, "method not specified"
    else:
        assert False, "unhandled option"


if __name__ == "__main__":
    main()
