import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import subprocess
import yaml
import os
import re
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
        text_xpath = '/html/body/div[2]/div[2]/div[2]/div[9]/div/div[1]/div[1]/div/div/div[3]/div[1]/div[1]/div[4]/ul/li[2]/label/span[2]'
        text = self.wait.until(EC.presence_of_element_located((By.XPATH, text_xpath))).text

        return int(text.replace(',', '').lstrip('(').rstrip(')'))

    def get_info(self):
        each_page_reviews_info = {'reviews': [], 'scores': []}

        for i in range(3, 8):
            try:
                review = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f'#component_15 > div > div:nth-child(3) > div:nth-child({i}) > div.cqoFv._T > div.dovOW > div.duhwe._T.bOlcm.dMbup > div.pIRBV._T > q > span'))).text
                score_text = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f'#component_15 > div > div:nth-child(3) > div:nth-child({i}) > div.cqoFv._T > div.elFlG.f.O > div > span'))).get_attribute('class')
                score = self._cleaning_score_text(score_text)

                each_page_reviews_info['reviews'].append(review)
                each_page_reviews_info['scores'].append(score)
            except selenium.common.exceptions.TimeoutException:
                print('selenium.common.exceptions.TimeoutException')
                break

        if len(each_page_reviews_info['reviews']) != len(each_page_reviews_info['scores']):
            raise Exception('[ERROR] :: not same len(reviews list) != len(scores list)')

        return each_page_reviews_info

    def click_next(self):
        try:
            next_button = self.driver.find_element_by_css_selector('#component_15 > div > div:nth-child(3) > div.ClYTS.MD > div > a.ui_button.nav.next.primary')
            next_button.send_keys(Keys.ENTER)
        except selenium.common.exceptions.TimeoutException:
            raise Exception('selenium.common.exceptions.TimeoutException :: this page is end')

    @staticmethod
    def _cleaning_score_text(score_text: str):
        return int(re.search(r'([0-9])([0-9])', score_text).group(1))

    def quit(self):
        self.driver.quit()
