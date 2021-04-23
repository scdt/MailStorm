from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from nltk.corpus import stopwords
import html2text as h2t
import re
import time

nonreg_folder = 'htmlpages_nonreg'
email2 = 'emailexample2@inbox.lv'
email3 = 'emailexample3@inbox.lv'
urls = ['https://github.com/password_reset', 'https://trello.com/forgot', 'https://9gag.com/recover', 'https://www.allmusic.com/forgot-password',
        'https://kr.battle.net/account/recovery/en/identify-account.html?requestType=PASSWORD_RESET', 'https://new.edmodo.com/account_recovery',
        'https://gen.xyz/account/pwreset.php', 'https://www.netflix.com/ru-en/LoginHelp', 'https://ltv.tapjoy.com/s/l#session/forgot',
        'https://twitter.com/account/begin_password_reset', 'https://vimeo.com/forgot_password',
        'https://www.duolingo.com/forgot_password', 'https://nanowrimo.org/forgot-password']

# urls = ['https://new.edmodo.com/account_recovery']


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
    return text


def load_wait(driver):
    time.sleep(1)
    for _ in range(3):
        page_state = driver.execute_script("return document.readyState;")
        if page_state == "complete":
            break
        time.sleep(1)
    time.sleep(3)
    return


def find_email_input(elements):
    '''
    Метод для поиска поля ввода email
    Принимает лист из WebEelement, возрващает найденный WebElement или Non
    '''
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


'''
Метод для поиска кнопки сброса пароля
Возвращает WebElement или None
'''


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


def reset_pas(driver, url, email):
    try:
        driver.get(url)
    except TimeoutException:
        pass
    for count in range(3):
        # Найти все элементы с тэгом input
        elements = driver.find_elements_by_tag_name("input")
        # print("Input tags:", len(elements))
        # Найти среди них поле ввода email
        element = find_email_input(elements)
        if element is None:
            print("Email input field not found")
            return False
        # Ввести в поле данные
        try:
            element.send_keys(email)
        except ElementNotInteractableException:
            time.sleep(1)
            continue
        time.sleep(1)
        html_old = driver.page_source
        # Нажать Enter
        try:
            element.send_keys(Keys.ENTER)
        except Exception:
            print('Send_keys Enter exception')
        load_wait(driver)
        html_new = driver.page_source
        if html_old != html_new:
            return html_new
        else:
            button = find_button(driver)
            try:
                button.click()
                load_wait(driver)
                html_new = driver.page_source
                if html_old != html_new:
                    return html_new
                else:
                    return False
            except:
                print("Exception with button")
                return False
    print("Element not interactable 3 times")
    return False


def save_htmls(email, input_file, folder):
    path = './' + folder + '/'
    options = webdriver.ChromeOptions()
    options.headless = False
    driver = webdriver.Chrome(executable_path='./chromedriver', options=options)
    driver.set_page_load_timeout(10)
    driver.get('https://www.google.com/')
    urls = []
    with open('./' + input_file, 'r') as f:
        for row in f:
            urls.append(row)
    for url in urls:
        print('*' * 10, url, '*' * 10)
        html = reset_pas(driver, url, email)
        if not html:
            continue
        else:
            i = url.replace('//', '').find('/') + 2
            f = open(f'{path+url[url.find("//") + 2: i]}.html', 'w')
            f.write(html)
            f.close()
