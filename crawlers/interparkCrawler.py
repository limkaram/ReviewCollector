from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from crawlers.utils import get_datefmt_text, check_contain_datefmt_text
import subprocess


class Crawler:
    def __init__(self):
        self.driver = None
        self.reviews = None
        self.scores = None
        self.score_texts = None
        self.dates = None

    def open(self, url: str, driver_path: str, headless: bool=False, wait_time: int=3):
        subprocess.Popen(r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\chrometemp"')  # 디버거 크롬 구동
        option = Options()
        option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

        if headless:
            option.add_argument('headless')
        self.driver = webdriver.Chrome(driver_path, options=option)
        self.driver.get(url)
        self.driver.implicitly_wait(wait_time)

    def get_info(self):
        self.reviews = [i.text.rstrip(' [more]') for i in self.driver.find_elements_by_class_name('conWrap')]
        try:
            self.scores = [i.text for i in self.driver.find_elements_by_class_name('scoreNum')]
            self.score_texts = [i.text for i in self.driver.find_elements_by_class_name('scoreTxt')]

            if len(self.scores) != len(self.reviews):
                for _ in range(len(self.reviews) - len(self.scores)):
                    self.scores.append(None)
                    self.score_texts.append(None)
        except Exception:
            self.scores = [None for _ in range(len(self.reviews))]
            self.score_texts = [None for _ in range(len(self.reviews))]

        dates = []
        for element in self.driver.find_elements_by_class_name('txt'):
            text = element.text
            if check_contain_datefmt_text(text):
                dates.append(get_datefmt_text(text))
        self.dates = dates

        return {'date': self.dates, 'score': self.scores, 'score_category': self.score_texts, 'review': self.reviews}

    def get_pages_list(self):
        pages = []
        for text in self.driver.find_element_by_class_name('pageNumBox').text.split('\n'):
            if text.isnumeric():
                pages.append(int(text))

        return pages

    def click_page(self, page: int, wait_time: int=1):
        self.driver.find_element_by_xpath(f'/html/body/section/div/section/div[2]/ul/li[{page}]').click()
        self.driver.implicitly_wait(wait_time)

    def click_pagebar(self, point: str, wait_time: int=1):
        if point == 'left':
            self.driver.find_element_by_xpath('/html/body/section/div/section/div[2]/button[1]').click()
        elif point == 'right':
            self.driver.find_element_by_xpath('/html/body/section/div/section/div[2]/button[2]').click()
        else:
            raise Exception('Invalid pagebar')
        self.driver.implicitly_wait(wait_time)

    def quit(self):
        self.driver.quit()
