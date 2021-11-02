from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from crawlers import utils
import subprocess
import yaml
import os
import time
from collections import OrderedDict
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

    def click_all_reviews(self):
        self.wait.until(EC.element_to_be_clickable(
            (By.XPATH, f'/html/body/div[1]/div[7]/div[5]/div[1]/div[3]/div[1]/div[8]/div/div/div[16]/div/div[4]/a'))).click()

    def click_view_alert_page(self):
        self.wait.until(EC.element_to_be_clickable((By.XPATH,f'/html/body/div[1]/div[7]/div[9]/div/div[1]/div[1]/span'))).click()

    def select_language(self, language: str):
        self.wait.until(EC.element_to_be_clickable((By.XPATH, f'/html/body/div[1]/div[7]/div[5]/div/div[1]/div[1]/div[3]/div[8]/div[1]'))).click()
        if language.lower() == 'korean':
            self.wait.until(
                EC.element_to_be_clickable((By.XPATH, f'/html/body/div[1]/div[7]/div[5]/div/div[1]/div[1]/div[3]/div[9]/div[9]/div[5]'))).click()
        elif language.lower() == 'english':
            pass
        else:
            raise Exception('Not implementation language')

    def infinity_scroll_down(self):
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:
            scroll_down = 0
            while scroll_down < 10:
                self.driver.find_element_by_tag_name("body").send_keys(Keys.PAGE_DOWN)
                time.sleep(0.2)
                scroll_down += 1

            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break

            last_height = new_height

    def scroll_down(self, scroll_down: int=50):
        for _ in range(scroll_down):
            self.driver.find_element_by_tag_name("body").send_keys(Keys.PAGE_DOWN)
            time.sleep(0.2)

    def get_info(self):
        extracted_info = OrderedDict()
        extracted_info['date'], extracted_info['recommend'], extracted_info['review'] = [], [], []

        recommend_ls = self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'title')))
        date_ls = self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'date_posted')))
        review_ls = self.wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'apphub_CardTextContent')))

        for recommend_elem, date_elem, review_elem in zip(recommend_ls, date_ls, review_ls):
            try:
                date = utils.change_steam_date_format(date_elem.text)
                recommend = recommend_elem.text

                sentences = review_elem.text.split('\n')[1:]
                if sentences[0] == 'EARLY ACCESS REVIEW':
                    review = ' '.join(sentences[1:])
                else:
                    review = ' '.join(sentences)
            except Exception as e:
                print('!!!! error : ', e)
                continue

            extracted_info['date'].append(date)
            extracted_info['recommend'].append(recommend)
            extracted_info['review'].append(review)

        return extracted_info

    def quit(self):
        self.driver.quit()
