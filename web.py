import os
from bs4 import BeautifulSoup
from requests_html import HTMLSession
from selenium import webdriver
from urllib.parse import urljoin
from pyppeteer import errors
from requests import exceptions
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
    '''
    ps = PorterStemmer()
    text = ps.stem(text)
    stop_words = set(stopwords.words('english'))
    stop_words.difference_update({'should', 'no', 'not'})
    stop_words.update({'one', 'distribution', 'ace', 'rewards', 'cookies', 'create', 'online', 'music', 'youtube', 'english',
                       'video', 'privacy', 'terms', 'upload', 'new', 'love', 'espaol', 'portugus', 'streaming', 'log'})
    for word in text.split():
        if(word in stop_words):
            text = re.sub(rf'\b{word}\b', '', text)
    '''
    text = re.sub(r'\s{2,}', ' ', text)
    return text


'''
Возвращает все формы страницы
'''


def get_all_forms(session, url, timeout_to_render=5):
    """Returns all form tags found on a web page's `url` """
    # GET request
    res = session.get(url)
    # for javascript driven website
    '''
    try:
        res.html.render(timeout_to_render)
    except errors.TimeoutError:
        print("TimeoutError while rendering the page")
    '''
    soup = BeautifulSoup(res.html.html, "html.parser")
    return soup.find_all("form")


'''
В алгоритме не используется. Используется в print_forms
'''


def get_form_details(form):
    """Returns the HTML details of a form,
    including action, method and list of form controls (inputs, etc)"""
    details = {}
    # get the form action (requested URL)
    try:
        action = form.attrs.get("action").lower()
    except AttributeError:
        action = ""
        # get the form method (POST, GET, DELETE, etc)
        # if not specified, GET is the default in HTML
    method = form.attrs.get("method", "get").lower()
    # get all form inputs
    inputs = []
    for input_tag in form.find_all("input"):
        # get type of input form control
        input_type = input_tag.attrs.get("type", "text")
        # get name attribute
        input_name = input_tag.attrs.get("name")
        # get the default value of that input tag
        input_value = input_tag.attrs.get("value", "")
        # add everything to that list
        try:
            input_hidden = input_tag.attrs.get("hidden")
            if input_hidden is not None:
                inputs.append({"type": input_type, "name": input_name, "hidden": input_hidden})
                continue
        except KeyError:
            pass
        inputs.append({"type": input_type, "name": input_name, "value": input_value})
    # put everything to the resulting dictionary
    details["action"] = action
    details["method"] = method
    details["inputs"] = inputs
    return details


'''
В алгоритме не используется
Печатает детали формы (action, method, input tags)
'''


def print_forms(forms):
    for i, form in enumerate(forms, start=1):
        form_details = get_form_details(form)
        print("=" * 50, f"form #{i}", "=" * 50)
        print(form_details)


'''
Метод для поиска формы сброса пароля
На вход принимает лист с формами
(предположительно) возвращает форму со сбросом пароля (на данной выборке работает на кажой странице верно)
'''


def find_form(forms):
    attributes = ['name', 'type', 'id', 'class', 'placeholder', 'value', 'text', 'title', 'action']
    for form in forms:
        checks = [False, False]
        for value in form.attrs.values():
            if not isinstance(value, list):
                value = [value]
            for item in value:
                if re.search(r'[Rr]ecover|[Ff]orgot|[Ss]end|[Rr]eset|[Pp]assword', item) is not None:
                    checks = [True, True]
                    break
        input_tags = form.find_all("input")
        for input_tag in input_tags:
            for attribute in attributes:
                attr_value = input_tag.attrs.get(attribute)
                if attr_value is None:
                    continue
                if isinstance(attr_value, list):
                    attr_value = attr_value[0]
                if re.search(r'[Ee]mail', attr_value) is not None:
                    checks[0] = True
                if len(forms) > 1 and re.search(r'[Rr]ecover|[Ff]orgot|[Ss]end|[Rr]eset', attr_value) is not None:
                    checks[1] = True
        if len(forms) == 1 and checks[0]:
            return form
        if len(forms) > 1:
            if all(checks):
                return form
    return None


'''
Метод для отправки запроса сброса пароля
Формирует тело или параметры запроса (post или get) на основе тегов формы
'''


def submit_form(url, session, form, email):
    form_details = get_form_details(form)
    data = {}
    for input_tag in form_details["inputs"]:
        try:
            if input_tag["hidden"]:
                data[input_tag["name"]] = ""
                continue
        except KeyError:
            pass
        if input_tag["type"] == "hidden":
            data[input_tag["name"]] = input_tag["value"]
        elif input_tag["type"] != "submit":
            # print(f"Non hidden input tag name='{input_tag['name']}' type='{input_tag['type']}'")
            data[input_tag["name"]] = email
    url = urljoin(url, form_details["action"])
    if form_details["method"] == "post":
        res = session.post(url, data=data)
    elif form_details["method"] == "get":
        res = session.get(url, params=data)
    return res


def main():
    files = ['github', 'music', 'battle', 'xyz', 'twitter', 'vimeo']
    email1 = 'emailexample1@inbox.lv'
    email2 = 'emailexample2@inbox.lv'
    '''
    urls = ['https://github.com/password_reset', 'https://trello.com/forgot', 'https://9gag.com/recover', 'https://www.allmusic.com/forgot-password',
            'https://kr.battle.net/account/recovery/en/identify-account.html?requestType=PASSWORD_RESET', 'https://new.edmodo.com/account_recovery',
            'https://gen.xyz/account/pwreset.php', 'https://www.netflix.com/ru-en/LoginHelp', 'https://ltv.tapjoy.com/s/l#session/forgot',
            'https://twitter.com/account/begin_password_reset', 'https://vimeo.com/forgot_password',
            'https://www.duolingo.com/forgot_password', 'https://nanowrimo.org/forgot-password']
    '''
    urls = ['https://github.com/password_reset', 'https://www.allmusic.com/forgot-password',
            'https://kr.battle.net/account/recovery/en/identify-account.html?requestType=PASSWORD_RESET', 'https://gen.xyz/account/pwreset.php',
            'https://twitter.com/account/begin_password_reset', 'https://vimeo.com/forgot_password']
    reg_texts = []
    noreg_texts = []
    for file in files:
        with open('pages_cmp/' + file + 'Reg.html') as file1:
            reg_texts.append(htmlToText(file1.read()))
        with open('pages_cmp/' + file + 'NoReg.html') as file1:
            noreg_texts.append(htmlToText(file1.read()))
    session = HTMLSession()
    for url, reg_text, noreg_text in zip(urls, reg_texts, noreg_texts):
        print('*' * 10, url, '*' * 10)
        successful_conection = False
        while not successful_conection:
            successful_conection = True
            try:
                forms = get_all_forms(session, url, timeout_to_render=12)   # получаем все формы со страницы
                if forms is not None:
                    form = find_form(forms)                                 # ищем форму сброса пароля
                    if form is not None:
                        # print(form)
                        res1 = submit_form(url, session, form, email1)      # выполняем запросы
                        res2 = submit_form(url, session, form, email2)
                        res3 = submit_form(url, session, form, email2)
                        print(res1.status_code)
                        text1 = htmlToText(res1.text)                       # получаем текст из htmlки
                        text2 = htmlToText(res2.text)
                        text3 = htmlToText(res3.text)
                        if text2 == text3:                                  # проверяем что 2 запроса с незареганным email содержат один и тот же текст
                            if text1 != text2:                              # сравниваем текст ответа зареганного и незарег.
                                print('Yes')
                            else:
                                print('No')
                        else:
                            print('Do not know')
                    else:
                        print('Forgot password form not found')
                else:
                    print('*' * 10, url, '*' * 10)
                    print('Forms not found')
            except exceptions.ConnectionError:
                successful_conection = False
                pass
    '''
    driver = webdriver.Chrome(executable_path='./chromedriver')
    driver.get('https://www.netflix.com/ru-en/LoginHelp')
    driver.find_element_by_class_name('ui-text-input').send_keys('emailexample2@inbox.lv')
    elements = driver.find_elements_by_tag_name('button')
    for elem in elements:
        print(elem.text)
    '''


if __name__ == '__main__':
    main()
