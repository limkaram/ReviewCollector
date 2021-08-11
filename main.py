import os
import yaml
from crawlers import interparkCrawler
from pprint import pprint
import pandas as pd


class Main:
    def __init__(self):
        with open('config/config.yaml') as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)
        self.driver_path = os.path.join(r'C:\Users\LIMKARAM\PycharmProjects\ReviewCollector\chromedriver.exe')

    def interpark_crawling(self):
        interpark_annex_url = self.config['interpark']['annex']
        result_df = pd.DataFrame()

        crawler = interparkCrawler.Crawler()
        crawler.open(url=interpark_annex_url, driver_path=self.driver_path, headless=False)
        crawler.click_pagebar(point='left')

        for page in crawler.get_pages_list():
            crawler.click_page(page, wait_time=1)
            info = crawler.get_info()
            pprint(info)
            result_df = result_df.append(pd.DataFrame(info))
        result_df.to_csv(os.path.join('outputs', 'interpark_20210811.csv'), index=False)


if __name__ == '__main__':
    excute = Main()
    excute.interpark_crawling()