from stat_scraper.logs.loggers import app_logger
from stat_scraper.stats_parser import get_html
from selenium.webdriver.common.keys import Keys
from multiprocessing import Pool
from bs4 import BeautifulSoup
from tqdm import tqdm
import time


# def normalize_list_urls(urls):
#     stop_strings = ['', ' ']
#     filtered_urls = list(filter(lambda url: url not in stop_strings, urls))
#     return [url.strip() for url in filtered_urls]


# def get_country_urls():
#     file_content = open('stat_scraper/urls/country_urls_ext.txt').read()
#     return normalize_list_urls(file_content.split(', '))


# def write_url_in_file(url, filename):
#     with open(filename, 'a') as file:
#         file.write(f'{url}, ')


# def make_file_champ_urls(country_urls, amount_seasons=8):
#     for url in tqdm(country_urls):
#         archive_url = url + 'archive/'
#         driver = get_driver()
#         driver.get(archive_url)
#         time.sleep(1)
#         champs_by_years = driver.find_elements_by_css_selector(
#             'div.leagueTable__season div.leagueTable__seasonName')
#         for i, champ in enumerate(champs_by_years[:amount_seasons]):
#             champ_text = champ.find_element_by_css_selector('a').text
#             season = champ_text.split(' ')[1]
#             country = driver.find_element_by_css_selector(
#                 'h2.tournament').text.split('\n')[1]
#             try:
#                 champ_url = champ.find_element_by_css_selector(
#                     'a').get_attribute('href')
#                 app_logger.debug(
#                     f'received url - {champ_url} by {country} {season}')
#                 write_url_in_file(champ_url, 'stat_scraper/urls/champ_urls_ext.txt')
#             except Exception:
#                 app_logger.exception(
#                     '\nError getting or writing in file element')


# def make_url_event(events_id):
#     template = 'https://www.flashscore.ru/match/{}'
#     result_urls = []
#     for id in events_id:
#         result_urls.append(template.format(id[4:]))
#     return result_urls


# def get_events_urls(champoinate_url):
#     driver = get_driver()
#     driver.get(champoinate_url)
#     app_logger.debug(f'Open page - {champoinate_url}')
#     time.sleep(1)
#     more_event = driver.find_element_by_css_selector('a.event__more')
#     more_event.send_keys(Keys.END)
#     try:
#         for i in range(1, 11):
#             app_logger.debug(f'get events page #{i}')
#             time.sleep(1)
#             more_event.click()
#             if i > 8:
#                 app_logger.debug('too many pages open')
#     except Exception:
#         app_logger.debug('All events open\n')
#     time.sleep(1)
#     events_lines = driver.find_elements_by_css_selector(
#         'div.sportName div.event__match')
#     events_id = [event.get_attribute('id') for event in events_lines]
#     driver.quit()
#     return make_url_event(events_id)


# def run_parse(champ_url):
#     count_records = 0
#     try:
#         events_urls = normalize_list_urls(
#             get_events_urls(champ_url + 'results/'))
#         app_logger.info(f'Received {len(events_urls)} events urls')
#         [write_url_in_file(event_url, 'stat_scraper/urls/events_urls_ext.txt') for event_url in events_urls]
#         count_records += len(events_urls)
#         app_logger.info(f'Total number of records = {count_records}\n')
#     except Exception:
#         app_logger.exception('\nreceive or record error')
#         write_url_in_file(champ_url, 'stat_scraper/urls/failed_received_urls.txt')

# def run_multi_parse(urls, n_proc):
#     app_logger.info(f'Start multiprocess function urls - {len(urls)} num processes - {n_proc}')
#     with Pool(n_proc) as p:
#         r = list(tqdm(p.imap(run_parse, urls), total=len(urls)))


# if __name__ == '__main__':
#     # country_urls = normalize_list_urls(
#     #     open('stat_scraper/urls/country_urls.txt').read().split(', '))
#     # make_file_champ_urls(country_urls)
#     champ_urls = champ_urls = open(
#         'stat_scraper/urls/champ_urls_ext.txt').read().split(', ')
#     run_multi_parse(champ_urls, 8)
