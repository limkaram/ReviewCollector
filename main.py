import os
import yaml
from crawlers import InterparkCrawler, SteamCrawler
import pandas as pd
import numpy as np
import time
import datetime

pd.set_option('display.max_columns', None)
PROJECT_ROOT_PATH = os.getcwd()


class Main:
    def __init__(self):
        with open(os.path.join(PROJECT_ROOT_PATH, 'config', 'config.yaml')) as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)
        self.driver_path = self.config['chromedriver_path']

    def interpark_crawling(self):
        for hotel, url in self.config['interpark'].items():
            print(f'[{hotel}] crawling start!!!')
            crawler = InterparkCrawler.Crawler(wait_time=3)
            crawler.open(url=url, driver_path=self.driver_path)
            crawler.click_pagemovebar(point='left')

            df_info = pd.DataFrame()
            all_reviews_num = crawler.all_reviews_num
            complete_reviews_num = 0

            for page in crawler.get_pages_list():
                if page > 1:
                    crawler.click_page(page)
                time.sleep(1)
                info = crawler.get_info(wait=False)
                complete_reviews_num += len(info['review'])
                processing_ratio = 100 * (complete_reviews_num / all_reviews_num)

                print(f'[page {page}] [{complete_reviews_num}/{all_reviews_num}({processing_ratio:.1f}%)]')
                print(info['date'], '\n', info['score'], '\n', info['score_category'], '\n', info['review'], '\n')
                df_info = df_info.append(pd.DataFrame(info))
            crawler.quit()
            df_info = df_info.sort_values(by='date').reset_index(drop=True)
            print(df_info.info(), '\n')
            present_date = datetime.datetime.now().strftime('%Y%m%d')
            df_info.to_csv(os.path.join('outputs', f'interpark_{hotel}_{present_date}.csv'), index=False)

    def steam_crawling(self):
        url = self.config['steam']['battlegrounds']
        crawler = SteamCrawler.Crawler(driver_path=self.driver_path)
        crawler.open(url=url)
        crawler.infinity_scroll_down()
        crawler.click_all_reviews()
        crawler.click_view_alert_page()
        crawler.select_language(language='korean')
        # crawler.infinity_scroll_down()
        crawler.scroll_down(scroll_down=10000)
        data = crawler.get_info()
        df = pd.DataFrame(data)
        print(df.head())
        print('')
        print(df.info())
        present_date = datetime.datetime.now().strftime('%Y%m%d')
        df.to_csv(os.path.join('outputs', f'steam_battlegrounds_{present_date}.csv'), index=False)
        time.sleep(60)


if __name__ == '__main__':
    excute = Main()
    excute.interpark_crawling()
    # excute.steam_crawling()