import os
import yaml
from crawlers import InterparkCrawler, TripadvisorCrawler, SteamCrawler, GoogleStoreCrawler, YogiyoCrawler
from selenium.common.exceptions import TimeoutException
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
        self.present_date = datetime.datetime.now().strftime('%Y%m%d')

    def interpark_crawling(self):
        for hotel, url in self.config['tripadvisor'].items():
            print(f'[{hotel}] crawling start!!!')
            crawler = InterparkCrawler.Crawler(wait_time=3)
            crawler.open(url=url, driver_path=self.driver_path)
            crawler.click_pagemovebar(point='left')

            df = pd.DataFrame()
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
                df = df.append(pd.DataFrame(info))
            crawler.quit()
            df = df.sort_values(by='date').reset_index(drop=True)
            df.to_csv(os.path.join('outputs', f'interpark_{hotel}_{self.present_date}.csv'), index=False)
            crawler.quit()
            print(df.head(), '\n')
            print(df.info(), '\n')
            print(df.scores.value_counts())

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
        df.to_csv(os.path.join('outputs', f'steam_battlegrounds_{self.present_date}.csv'), index=False)
        crawler.quit()
        print(df.head(), '\n')
        print(df.info(), '\n')
        print(df.scores.value_counts())

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

            df = pd.DataFrame(result)
            df.to_csv(os.path.join('outputs', f'tripadvisor_{hotel}_{self.present_date}.csv'), index=False)
            crawler.quit()
            print(df.head(), '\n')
            print(df.info(), '\n')
            print(df.scores.value_counts())

    def googlestore_crawling(self):
        for app, url in self.config['google_store'].items():
            print(app, url)
            crawler = GoogleStoreCrawler.Crawler(wait_time=3)
            crawler.open(url=url, driver_path=self.driver_path)
            crawler.click_all_reviews()
            reviews_info = crawler.get_info(scroll_cnt=100)
            df = pd.DataFrame(reviews_info)
            df.to_csv(os.path.join('outputs', f'googlestore_{app}_{self.present_date}.csv'), index=False)
            crawler.quit()
            print(df.head(), '\n')
            print(df.info(), '\n')
            print(df.scores.value_counts())

    def yogiyo_crawling(self):
        for restaurant, url in self.config['yogiyo'].items():
            print(restaurant, url)
            crawler = YogiyoCrawler.Crawler(wait_time=3)
            crawler.open(url=url, driver_path=self.driver_path)
            time.sleep(2)
            crawler.click_clean_reviews_bar()
            try:
                crawler.click_more_show(click_cnt=200, infinity=False)
            except TimeoutException as e:
                print(e)
            finally:
                reviews_info = crawler.get_info()
                df = pd.DataFrame(reviews_info)
                df.to_csv(os.path.join('outputs', f'yogiyo_{restaurant}_{self.present_date}.csv'), index=False)
                crawler.quit()
                print(df.head(), '\n')
                print(df.info(), '\n')
                print(df.scores.value_counts())


if __name__ == '__main__':
    excute = Main()
    # excute.interpark_crawling()
    # excute.steam_crawling()
    # excute.tripadvisor_crawling()
    # excute.googlestore_crawling()
    excute.yogiyo_crawling()
