import os
from bs4 import BeautifulSoup
from requests_html import HTMLSession
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from urllib.parse import urljoin
from pyppeteer import errors
from requests import exceptions
from selenium.common.exceptions import ElementNotInteractableException
import html2text as h2t
import re
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import time

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36'}
email1 = 'emailexample1@inbox.lv'
email2 = 'emailexample2@inbox.lv'
urls = ['https://github.com/password_reset', 'https://trello.com/forgot', 'https://9gag.com/recover', 'https://www.allmusic.com/forgot-password',
        'https://kr.battle.net/account/recovery/en/identify-account.html?requestType=PASSWORD_RESET', 'https://new.edmodo.com/account_recovery',
        'https://gen.xyz/account/pwreset.php', 'https://www.netflix.com/ru-en/LoginHelp', 'https://ltv.tapjoy.com/s/l#session/forgot',
        'https://twitter.com/account/begin_password_reset', 'https://vimeo.com/forgot_password',
        'https://www.duolingo.com/forgot_password', 'https://nanowrimo.org/forgot-password']


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
    res = session.get(url, headers=headers)
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
                if re.search(r'[Rr]ecover|[Ff]orgot|[Ss]end|[Rr]eset|[Pp]assword', item, re.IGNORECASE) is not None:
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
                if re.search(r'mail', attr_value, re.IGNORECASE) is not None:
                    checks[0] = True
                if len(forms) > 1 and re.search(r'[Rr]ecover|[Ff]orgot|[Ss]end|[Rr]eset', attr_value, re.IGNORECASE) is not None:
                    checks[1] = True
        if len(forms) == 1 and checks[0]:
            return form
        if len(forms) > 1:
            if all(checks):
                return form
    return None


def find_input(inputs):
    if len(inputs) == 1:
        return inputs[0]
    input_tags1 = []
    for input_tag in inputs:
        type_attr = input_tag.attrs.get("type")
        if type_attr is not None and re.search(r'text|mail|account|user', type_attr, re.IGNORECASE) and (input_tag not in input_tags1):
            input_tags1.append(input_tag)
    if len(input_tags1) == 1:
        return input_tags1[0]
    input_tags2 = []
    for input_tag in inputs:
        name_attr = input_tag.attrs.get("name")
        if name_attr is not None and re.search(r'mail|account|user', name_attr, re.IGNORECASE) and (input_tag not in input_tags2):
            input_tags2.append(input_tag)
    if len(input_tags2) == 1:
        return input_tags2[0]
    input_tags3 = []
    for input_tag in inputs:
        placeholder_attr = input_tag.attrs.get("placeholder")
        if placeholder_attr is not None and re.search(r'@|mail|user|account|example', placeholder_attr, re.IGNORECASE) and (input_tag not in input_tags3):
            input_tags3.append(input_tag)
    if len(input_tags3) == 1:
        return input_tags3[0]
    return None


def find_email_input(elements):
    if len(elements) == 1:
        return elements[0]
    elements1 = []
    for element in elements:
        type_attr = element.get_attribute("type")
        if type_attr is not None and re.search(r'text|mail|account|user', type_attr, re.IGNORECASE) and (element not in elements1):
            elements1.append(element)
    if len(elements1) == 1:
        return elements1[0]
    elements2 = []
    for element in elements:
        name_attr = element.get_attribute("name")
        if name_attr is not None and re.search(r'mail|account|user', name_attr, re.IGNORECASE) and (element not in elements2):
            elements2.append(element)
    if len(elements2) == 1:
        return elements2[0]
    elements3 = []
    for element in elements:
        placeholder_attr = element.get_attribute("placeholder")
        if placeholder_attr is not None and re.search(r'@|mail|user|account|example', placeholder_attr, re.IGNORECASE) and (element not in elements3):
            elements3.append(element)
    if len(elements3) == 1:
        return elements3[0]
    return None


def find_button(driver):
    inputs = driver.find_elements_by_tag_name("input")
    buttons = driver.find_elements_by_tag_name("button")
    if buttons:
        buttons1 = []
        for element in buttons:
            element_html = element.get_attribute("outerHTML")
            soup = BeautifulSoup(element_html, "html.parser")
            type_attr = soup.find("button").attrs.get("type")
            if isinstance(type_attr, list):
                type_attr = " ".join(type_attr)
            # type_attr = element.get_attribute("type")
            if type_attr is not None and re.search(r'submit', type_attr, re.IGNORECASE) and (element not in buttons1):
                buttons1.append(element)
        if len(buttons1) == 1:
            return buttons1[0]
        buttons2 = []
        for element in buttons:
            element_html = element.get_attribute("outerHTML")
            soup = BeautifulSoup(element_html, "html.parser")
            class_attr = soup.find("button").attrs.get("class")
            if isinstance(class_attr, list):
                class_attr = " ".join(class_attr)
            # class_attr = element.get_attribute("class")
            if class_attr is not None and re.search(r'recover|next|forgot|pass', class_attr, re.IGNORECASE) and (element not in buttons2):
                buttons2.append(element)
        if len(buttons2) == 1:
            return buttons2[0]
    inputs1 = []
    for element in inputs:
        element_html = element.get_attribute("outerHTML")
        soup = BeautifulSoup(element_html, "html.parser")
        type_attr = soup.find("input").attrs.get("type")
        if isinstance(type_attr, list):
            type_attr = " ".join(type_attr)
        # type_attr = element.get_attribute("type")
        if type_attr is not None and re.search(r'submit|but|btn|', type_attr, re.IGNORECASE) and (element not in inputs1):
            inputs1.append(element)
    if len(inputs1) == 1:
        return inputs1[0]
    inputs2 = []
    for element in inputs:
        element_html = element.get_attribute("outerHTML")
        soup = BeautifulSoup(element_html, "html.parser")
        value_attr = soup.find("input").attrs.get("value")
        if isinstance(value_attr, list):
            value_attr = " ".join(value_attr)
        # value_attr = element.get_attribute("value")
        if value_attr is not None and re.search(r'submit|send|reset|continue|next|email|search|help', value_attr, re.IGNORECASE) and (element not in inputs2):
            inputs2.append(element)
    if len(inputs2) == 1:
        return inputs2[0]
    inputs3 = []
    for element in inputs:
        element_html = element.get_attribute("outerHTML")
        soup = BeautifulSoup(element_html, "html.parser")
        class_attr = soup.find("input").attrs.get("class")
        if isinstance(class_attr, list):
            class_attr = " ".join(class_attr)
        # class_attr = element.get_attribute("class")
        if class_attr is not None and re.search(r'btn|but', class_attr, re.IGNORECASE) and (element not in inputs3):
            inputs3.append(element)
    if len(inputs3) == 1:
        return inputs3[0]
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
        res = session.post(url, data=data, headers=headers)
    elif form_details["method"] == "get":
        res = session.get(url, params=data, headers=headers)
    return res


def main():
    files = ['github', 'music', 'battle', 'xyz', 'twitter', 'vimeo']
    reg_texts = []
    noreg_texts = []
    for file in files:
        with open('pages_cmp/' + file + 'Reg.html') as file1:
            reg_texts.append(htmlToText(file1.read()))
        with open('pages_cmp/' + file + 'NoReg.html') as file1:
            noreg_texts.append(htmlToText(file1.read()))
    for url, reg_text, noreg_text in zip(urls, reg_texts, noreg_texts):
        session = HTMLSession()
        print('*' * 10, url, '*' * 10)
        successful_conection = False
        connection_attempts = 0
        while not successful_conection:
            if connection_attempts > 4:
                print('Connection attempts exceeded')
                break
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
                        print(text1)
                        if text1 == reg_text:
                            print('reg = saved')
                        if text2 == noreg_text:
                            print('noreg = saved')
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
                connection_attempts += 1
                pass


def main_selenium():
    options = webdriver.ChromeOptions()
    options.headless = False
    driver = webdriver.Chrome(executable_path='./chromedriver', options=options)
    for url in urls:
        print('*' * 10, url, '*' * 10)
        try:
            while(1):
                try:
                    driver.get(url)
                    elements = driver.find_elements_by_tag_name("input")
                    element = find_email_input(elements)
                    if element is None:
                        print("Email input field not found")
                        raise NotImplementedError
                    element.send_keys(email1)
                    time.sleep(1)
                    element.send_keys(Keys.ENTER)
                    time.sleep(2)
                    html1 = driver.page_source
                    break
                except ElementNotInteractableException:
                    pass
        except NotImplementedError:
            continue

        try:
            while(1):
                try:
                    driver.get(url)
                    elements = driver.find_elements_by_tag_name("input")
                    element = find_email_input(elements)
                    if element is None:
                        print("Email input field not found")
                        raise NotImplementedError
                    element.send_keys(email2)
                    time.sleep(1)
                    element.send_keys(Keys.ENTER)
                    time.sleep(2)
                    html2 = driver.page_source
                    break
                except ElementNotInteractableException:
                    pass
        except NotImplementedError:
            continue

        text1 = htmlToText(html1)
        text2 = htmlToText(html2)
        if text1 == text2:
            print("No")
        else:
            print("Yes")


if __name__ == '__main__':
    main_selenium()
