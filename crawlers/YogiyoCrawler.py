from selenium import webdriver
from selenium.webdriver.chrome.options import Options
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

    def click_all_reviews(self):
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#fcxH9b > div.WpDbMd > c-wiz > div > div.ZfcPIb > div > div > main > div > div.W4P4ne > div.XnFhVd > div > span'))).click()

    def get_info(self, scroll_cnt: int):
        result = {'reviews': [], 'scores': []}
        container = set()

        for _ in range(scroll_cnt):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            more_button = self.driver.find_elements_by_xpath(
                '//*[@id="fcxH9b"]/div[4]/c-wiz[2]/div/div[2]/div/div/main/div/div[1]/div[2]/div[2]/div')

            if more_button:
                more_button[0].click()

            html_source = self.driver.page_source
            soup = BeautifulSoup(html_source, 'html.parser')
            info_boxes = soup.find_all('div', jscontroller='H6eOGe')

            for i, info_box in enumerate(info_boxes):
                review = info_box.find('span', jsname='bN97Pc').text
                score_text = info_box.find('div', role='img').get('aria-label')
                score = self._cleaning_score_text(score_text)
                container.add((score, review))
            print(container)

        for score, review in list(container):
            result['reviews'].append(review)
            result['scores'].append(score)

        return result

    @staticmethod
    def _cleaning_score_text(score_text: str):
        # example string : 별표 5개 만점에 1개를 받았습니다.
        return int(re.match(r'별표 [0-9]개 만점에 ([0-9])개를 받았습니다.', score_text).group(1))

    def quit(self):
        self.driver.quit()
