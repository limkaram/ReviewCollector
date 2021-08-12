import os
import yaml
from crawlers import interparkCrawler
import pandas as pd
import time
import datetime

pd.set_option('display.max_columns', None)
PROJECT_ROOT_PATH = os.getcwd()


class Main:
    def __init__(self):
        with open(os.path.join(PROJECT_ROOT_PATH, 'config', 'config.yaml')) as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)
        self.driver_path = os.path.join(r'C:\Users\LIMKARAM\PycharmProjects\ReviewCollector\chromedriver.exe')

    def interpark_crawling(self):
        for hotel, url in self.config['interpark'].items():
            print(f'[{hotel}] crawling start!!!')
            df_info = pd.DataFrame()
            crawler = interparkCrawler.Crawler(wait_time=3)
            crawler.open(url=url, driver_path=self.driver_path)
            crawler.click_pagemovebar(point='left')

            for page in crawler.get_pages_list():
                if page > 1:
                    crawler.click_page(page)
                time.sleep(1)
                info = crawler.get_info(wait=False)
                print(f'[page {page}]')
                print(info['date'], '\n', info['score'], '\n', info['score_category'], '\n', info['review'], '\n')
                df_info = df_info.append(pd.DataFrame(info))
            crawler.quit()
            df_info = df_info.sort_values(by='date').reset_index(drop=True)
            print(df_info.info(), '\n')
            present_date = datetime.datetime.now().strftime('%Y%m%d')
            df_info.to_csv(os.path.join('outputs', f'interpark_{hotel}_{present_date}.csv'), index=False)


if __name__ == '__main__':
    excute = Main()
    excute.interpark_crawling()