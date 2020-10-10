from stat_scraper.logs.loggers import app_logger
from stat_scraper.init_driver import get_driver
from stat_scraper.utils import write_text_file
from selenium.webdriver.common.keys import Keys
from multiprocessing import Pool
from tqdm import tqdm
import time


def make_url_event(events_id):
    template = 'https://www.flashscore.ru/match/{}/#point-by-point;1'
    result_urls = []
    for id in events_id:
        result_urls.append(template.format(id[4:]))
    return result_urls


def get_events_urls(champ_url):
    with get_driver() as driver:
        driver.get(champ_url)
        app_logger.info(f'Open page - {champ_url}')
        time.sleep(2)
        more_event = driver.find_elements_by_css_selector('a.event__more')
        if not more_event:
            app_logger.info('There is not more event btn on page {champ_url}')
        try:
            more_event[0].send_keys(Keys.END)
            for i in range(1, 5):
                app_logger.debug(f'get events page #{i}')
                time.sleep(1)
                more_event[0].click()
                if i > 8:
                    app_logger.debug('too many pages open')
        except Exception:
            app_logger.debug('All events open\n')
        time.sleep(1)
        events_lines = driver.find_elements_by_css_selector(
            'div.sportName div.event__match')
        events_id = [event.get_attribute('id') for event in events_lines]
        return make_url_event(events_id)


def run_parse(champ_url):
    count_records = 0
    try:
        events_urls = get_events_urls(champ_url)
        app_logger.info(f'Received {len(events_urls)} events urls')
        [write_text_file(
            'stat_scraper/urls/wta_events_urls.txt', event_url)
            for event_url in events_urls]
        count_records += len(events_urls)
        app_logger.info(f'Write in file {count_records} urls\n')
    except Exception:
        app_logger.exception('\nreceive or record error')
        write_text_file('stat_scraper/logs/failed_received_events_urls.txt', champ_url)


def run_multi_parse(urls, n_proc):
    app_logger.info(
        f'Start multiprocess function urls - {len(urls)} num processes - {n_proc}')
    with Pool(n_proc) as p:
        list(tqdm(p.imap(run_parse, urls), total=len(urls)))


if __name__ == '__main__':
    with open('stat_scraper/urls/atp_champs_by_years_urls.txt') as file:
        champ_urls = file.read().split(', ')
    run_multi_parse(champ_urls, 8)
    with open('stat_scraper/urls/wta_champs_by_years_urls.txt') as file:
        champ_urls = file.read().split(', ')
    run_multi_parse(champ_urls, 8)
