from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import subprocess
import yaml
import os
import time
import platform
import re
from pprint import pprint


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
            subprocess.Popen(r'{} --remote-debugging-port=9222 --user-data-dir="C:\chrometemp"'.format(self.chrome_path))
            option = Options()
            option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            self.driver = webdriver.Chrome(driver_path, options=option)
        else:
            self.driver = webdriver.Chrome(driver_path)

        self.wait = WebDriverWait(self.driver, self.wait_time)
        self.driver.get(url)

    def click_clean_reviews_bar(self):
        self.wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="content"]/div[2]/div[1]/ul/li[2]/a'))).click()

    def click_more_show(self, click_cnt: int, infinity: bool):
        prev_height = self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")

        if infinity:
            while True:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#review > li.list-group-item.btn-more > a > span'))).click()
                time.sleep(2)

                curr_height = self.driver.execute_script("return document.body.scrollHeight")

                if curr_height == prev_height:
                    break

                prev_height = curr_height
        else:
            for _ in range(click_cnt):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#review > li.list-group-item.btn-more > a > span'))).click()
                time.sleep(2)

    def get_info(self):
        result = {'reviews': [], 'scores': []}
        html_source = self.driver.page_source

        soup = BeautifulSoup(html_source, 'html.parser')
        info_boxes = soup.find_all('li', class_='list-group-item star-point ng-scope')

        for info_box in info_boxes:
            score = len(info_box.find_all('span', class_='full ng-scope'))
            review = info_box.find('p', attrs={'ng-show': 'review.comment'}).text.replace('\n', ' ')
            result['reviews'].append(review)
            result['scores'].append(score)

        return result

    def quit(self):
        self.driver.quit()
