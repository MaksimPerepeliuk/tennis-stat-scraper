from stat_scraper.logs.loggers import app_logger
from selenium.webdriver.common.keys import Keys
from stat_scraper.stats_parser import get_html
from stat_scraper.init_driver import get_driver
from bs4 import BeautifulSoup
from tqdm import tqdm
import time


def get_champs_urls(comp_menu):
    base_url = 'https://www.flashscore.com{}archive/'
    champs = comp_menu.select('ul.submenu li')
    champ_urls = []
    for competition in champs:
        champ_urls.append(base_url.format(competition.select('a')[0]['href']))
    return champ_urls


def get_champ_urls_by_years(html):
    soup = BeautifulSoup(html, 'lxml')
    base_url = 'https://www.flashscore.com{}/results/'
    champs_by_years = soup.select(
        'div#tournament-page-archiv div.leagueTable__seasonName a')
    required_years = ['2020', '2019', '2018', '2017',
                      '2016', '2015', '2014', '2013']
    urls = []
    for champ in champs_by_years:
        champ_year = champ.text.split(' ')[-1]
        if champ_year in required_years:
            urls.append(base_url.format(champ['href']))
    return urls


def open_hide_champ_list():
    url = 'https://www.flashscore.com/tennis/'
    with get_driver() as driver:
        driver = get_driver()
        driver.get(url)
        time.sleep(5)
        driver.execute_script("window.scrollTo(0, 800)")
        time.sleep(3)
        driver.find_element_by_css_selector('li#lmenu_5724 a').click()
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, 5500)")
        time.sleep(3)
        driver.find_element_by_css_selector('li#lmenu_5725 a').click()
        time.sleep(3)
        return driver.page_source

if __name__ == '__main__':
    html = open_hide_champ_list()
    soup = BeautifulSoup(html, 'lxml')
    atp_competitions = soup.select('li#lmenu_5724')[0]
    wta_competitions = soup.select('li#lmenu_5725')[0]
    champ_urls = get_champs_urls(atp_competitions)
    print(len(champ_urls))