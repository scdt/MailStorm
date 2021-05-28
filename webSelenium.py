from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import TimeoutException
import re
import time


class WebSelenium():

    def loadWait(driver):
        time.sleep(1)
        for _ in range(3):
            page_state = driver.execute_script("return document.readyState;")
            if page_state == "complete":
                break
            time.sleep(1)
        time.sleep(3)
        return

    '''
    Метод для поиска поля ввода email
    Принимает лист из WebEelement, возрващает найденный WebElement или Non
    '''
    def findEmailInput(elements):
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
    def findButton(driver):
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
            if class_attr is not None and re.search(r'btn|but', class_attr, re.IGNORECASE) and (element not in inputs3):
                inputs3.append(element)
        if len(inputs3) == 1:
            return inputs3[0]
        return None

    def resetPas(driver, url, email):
        try:
            driver.get(url)
        except TimeoutException:
            pass
        for count in range(3):
            elements = driver.find_elements_by_tag_name("input")
            element = WebSelenium.findEmailInput(elements)
            if element is None:
                print("Email input field not found")
                return False
            try:
                element.send_keys(email)
            except ElementNotInteractableException:
                time.sleep(1)
                continue
            time.sleep(1)
            html_old = driver.page_source
            try:
                element.send_keys(Keys.ENTER)
            except Exception:
                print('Send_keys Enter exception')
            WebSelenium.loadWait(driver)
            html_new = driver.page_source
            if html_old != html_new:
                return html_new
            else:
                button = WebSelenium.findButton(driver)
                try:
                    button.click()
                    WebSelenium.loadWait(driver)
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

    def saveHtmls(email, input_file, folder):
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
            html = WebSelenium.resetPas(driver, url, email)
            if not html:
                continue
            else:
                i = url.replace('//', '').find('/') + 2
                f = open(f'{path+url[url.find("//") + 2: i]}.html', 'w')
                f.write(html)
                f.close()
