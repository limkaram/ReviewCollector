import os
import yaml
from crawlers import InterparkCrawler, TripadvisorCrawler, SteamCrawler, GoogleStoreCrawler, YogiyoCrawler
import pandas as pd
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
        for hotel, url in self.config['tripadvisor'].items():
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
        crawler = SteamCrawler.Crawler()
        crawler.open(url=url, driver_path=self.driver_path)
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

    def tripadvisor_crawling(self):
        result = {'reviews': [], 'scores': []}

        for hotel, url in self.config['tripadvisor'].items():
            print(f'hotel name : {hotel}')
            print(f'url : {url}\n')
            crawler = TripadvisorCrawler.Crawler(wait_time=3)
            crawler.open(url=url, driver_path=self.driver_path)
            all_reviews_num = crawler.all_reviews_num
            complete_reviews_num = 0

            while complete_reviews_num < all_reviews_num:
                each_page_info = crawler.get_info()
                reviews, scores = each_page_info['reviews'], each_page_info['scores']
                result['reviews'].extend(reviews)
                result['scores'].extend(scores)
                complete_reviews_num += len(reviews)
                processing_ratio = 100 * (complete_reviews_num / all_reviews_num)
                print(f'[{complete_reviews_num}/{all_reviews_num}({processing_ratio:.1f}%)]')
                print(reviews)
                print(scores)
                print('')
                try:
                    crawler.click_next()
                except Exception as e:
                    print(e)
                    break
                time.sleep(2)

            df_info = pd.DataFrame(result)
            print(df_info.head())
            print(df_info.info())
            print(df_info.scores.value_counts())
            present_date = datetime.datetime.now().strftime('%Y%m%d')
            df_info.to_csv(os.path.join('outputs', f'tripadvisor_{hotel}_{present_date}.csv'), index=False)
            crawler.quit()

    def googlestore_crawling(self):
        for app, url in self.config['google_store'].items():
            print(app, url)
            crawler = GoogleStoreCrawler.Crawler(wait_time=3)
            crawler.open(url=url, driver_path=self.driver_path)
            crawler.click_all_reviews()
            reviews_info = crawler.get_info(scroll_cnt=100)
            df_info = pd.DataFrame(reviews_info)
            print(df_info.head(), '\n')
            print(df_info.info())
            present_date = datetime.datetime.now().strftime('%Y%m%d')
            df_info.to_csv(os.path.join('outputs', f'googlestore_{app}_{present_date}.csv'), index=False)
            time.sleep(15)
            crawler.quit()

    def yogiyo_crawling(self):
        for restaurant, url in self.config['yogiyo'].items():
            print(restaurant, url)
            crawler = YogiyoCrawler.Crawler(wait_time=3)
            crawler.open(url=url, driver_path=self.driver_path)
            crawler.click_clean_reviews_bar()
            time.sleep(15)
            break


if __name__ == '__main__':
    excute = Main()
    # excute.interpark_crawling()
    # excute.steam_crawling()
    # excute.tripadvisor_crawling()
    # excute.googlestore_crawling()
    excute.yogiyo_crawling()