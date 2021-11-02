from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from crawlers.utils import get_datefmt_text, check_contain_datefmt_text
import subprocess
import yaml
import os
import platform


class Crawler:
    def __init__(self, wait_time: int=10):
        with open(os.path.join('config', 'config.yaml')) as f:
            config = yaml.load(f, Loader=yaml.FullLoader)
        self.chrome_path = config['chrome_path']
        self.driver = None
        self.wait = None
        self.wait_time = wait_time

    def open(self, url: str, driver_path: str):
        if platform.system().lower().startswith('window'):
            subprocess.Popen(
                r'{} --remote-debugging-port=9222 --user-data-dir="C:\chrometemp"'.format(self.chrome_path))
            option = Options()
            option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            self.driver = webdriver.Chrome(driver_path, options=option)
        else:
            self.driver = webdriver.Chrome(driver_path)

        self.wait = WebDriverWait(self.driver, self.wait_time)
        self.driver.get(url)

    @property
    def all_reviews_num(self):
        return int(self.wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/section/div/section/div[1]/div[2]/div[1]/h4/span'))).text)

    def get_info(self, wait: bool):
        if not wait:
            self.wait = WebDriverWait(self.driver, 0)

        reviews = [i.text.rstrip(' [more]') for i in self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'conWrap')))]

        try:
            scores = [i.text for i in self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'scoreNum')))]
            score_texts = [i.text for i in self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'scoreTxt')))]

            if len(scores) != len(reviews):
                for _ in range(len(reviews) - len(scores)):
                    scores.append('-')
                    score_texts.append('-')
        except Exception:
            scores = ['-' for _ in range(len(reviews))]
            score_texts = ['-' for _ in range(len(reviews))]

        dates = []

        for element in self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'txt'))):
            text = element.text
            if check_contain_datefmt_text(text):
                dates.append(get_datefmt_text(text))

        return {'date': dates, 'score': scores, 'score_category': score_texts, 'review': reviews}

    def get_pages_list(self):
        pages = []
        for text in self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'pageNumBox'))).text.split('\n'):
            if text.isnumeric():
                pages.append(int(text))

        return pages

    def click_page(self, page: int):
        self.wait.until(EC.element_to_be_clickable((By.XPATH, f'/html/body/section/div/section/div[2]/ul/li[{page}]'))).click()

    def click_pagemovebar(self, point: str):
        if point == 'left':
            self.wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/section/div/section/div[2]/button[1]'))).click()
        elif point == 'right':
            self.wait.until(EC.element_to_be_clickable((By.XPATH, '/html/body/section/div/section/div[2]/button[2]'))).click()
        else:
            raise Exception('Invalid pagemovebar')

    def quit(self):
        self.driver.quit()
