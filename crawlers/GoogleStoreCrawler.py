from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import subprocess
import yaml
import os
import time
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
            subprocess.Popen(r'{} --remote-debugging-port=9222 --user-data-dir="C:\chrometemp"'.format(self.chrome_path))
            option = Options()
            option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
            self.driver = webdriver.Chrome(driver_path, options=option)
        else:
            self.driver = webdriver.Chrome(driver_path)

        self.wait = WebDriverWait(self.driver, self.wait_time)
        self.driver.get(url)

    def click_all_reviews(self):
        self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#fcxH9b > div.WpDbMd > c-wiz > div > div.ZfcPIb > div > div > main > div > div.W4P4ne > div.XnFhVd > div > span'))).click()

    def get_info(self):
        result = {'reviews': [], 'scores': []}

        html_source = self.driver.page_source
        soup = BeautifulSoup(html_source, 'html.parser')
        print(soup)


        # reviews_info = self.driver.find_elements_by_xpath('//*[@jsname="fk8dgd"]//div[@class="d15Mdf bAhLNe"]')
        # reviews_info = self.driver.find_elements_by_xpath('//*[@id="fcxH9b"]/div[4]/c-wiz[3]/div/div[2]/div/div/main/div/div[1]')
        # reviews_info = self.driver.find_elements_by_class_name('UD7Dzf')
        # print(len(reviews_info))
        # print(reviews_info[:3])

        # for info in reviews_info:
        #     soup = BeautifulSoup(info.get_attribute('innerHTML'), 'html.parser')
        #     score = int(soup.find('div', role='img').get('aria-label').replace('별표 5개 만점에', '').replace('개를 받았습니다.', '').strip())
        #     review = soup.find('span', jsname='bN97Pc').text
        #
        #     if not review:
        #         review = soup.find('span', jsname='fbQN7e').text
        #     print(review)
        #
        #     result['reviews'].append(review)
        #     result['scores'].append(score)
        #     # print(f'[score {score}] {review}')
        #
        #     return result

    def scroll_down(self, scroll_cnt):
        for _ in range(scroll_cnt):
            self.driver.find_element_by_tag_name('body').send_keys(Keys.PAGE_DOWN)
            time.sleep(0.2)

            try:
                more_button = self.driver.find_element_by_css_selector('#fcxH9b > div.WpDbMd > c-wiz:nth-child(4) > div > div.ZfcPIb > div > div > main > div > div.W4P4ne > div:nth-child(2) > div.PFAhAf > div > span')
                more_button.click()
            except Exception:
                continue

    def quit(self):
        self.driver.quit()
