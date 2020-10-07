from collections import Counter
from stat_scraper.init_driver import get_driver
from stat_scraper.logs.loggers import app_logger
# from stat_scraper.utils import write_csv, write_text_file
# from multiprocessing import Pool
# from tqdm import tqdm
from bs4 import BeautifulSoup
import time


def get_html(url):
    try:
        with get_driver() as driver:
            driver.get(url)
            time.sleep(1)
            html = driver.page_source
            app_logger.info(f'Received html {url}\n')
            return html
    except Exception:
        app_logger.exception(f'Error received html {url}\n')


def bp_counter(line):
    bp_counts = 0
    for points in line:
        if 'BP' in points:
            bp_counts += 1
    return bp_counts


def sp_counter(line):
    sp_counts = 0
    for points in line:
        if 'SP' in points:
            sp_counts += 1
    return sp_counts


def win_fp_counter(first_points, player_position):
    win_first_point = 0
    point = first_points.split(':')[player_position]
    if point == '15':
        win_first_point += 1
    return win_first_point


def points_counter(line, player_position):
    points_win = 0
    points_lost = 0
    points_result = line[-1]
    if 'BPSP' in points_result:
        points = points_result[:-4]
    elif 'MP' in points_result:
        points = points_result[:-4]
    elif 'BP' in points_result:
        points = points_result[:-2]
    elif 'SP' in points_result:
        points = points_result[:-2]
    else:
        points = points_result
    points_parts = points.split(':')
    points_win += int(points_parts[player_position].replace('A', '50'))
    points_lost += int(points_parts[player_position - 1].replace('A', '50'))
    return (points_win, points_lost)


def get_match_line_stats(game_lines, player, n_set):
    points_length = 0
    breakpoint_counts = 0
    setpoint_counts = 0
    win_points = 0
    lost_points = 0
    win_first_points = 0
    player_position = 0 if player == 'p1' else 1
    for tr in game_lines:
        tds = tr.select('td')
        line = tds[0].text
        line_parts = line.split(', ')
        points_length += len(line_parts)
        breakpoint_counts += bp_counter(line_parts)
        setpoint_counts += sp_counter(line_parts)
        points = points_counter(line_parts, player_position)
        win_points += points[0]
        lost_points += points[1]
        win_first_points += win_fp_counter(line_parts[0], player_position)
    return {
            f'{player}_points_len': points_length,
            f'{player}_bp': breakpoint_counts,
            f'{player}_sp': setpoint_counts,
            f'{player}_win_points': win_points,
            f'{player}_lost_points': lost_points,
            f'{player}_win_fp': win_first_points,
        }


def get_result_serving(game_serve, player, n_set):
    lost_serve_counts = 0
    win_serve_counts = 0
    for tr in game_serve:
        tds = tr.select('td')
        if 'LOST' in tds[0].text or 'LOST' in tds[4].text:
            lost_serve_counts += 1
        else:
            win_serve_counts += 1
    return {
        f'{player}_lost_games': lost_serve_counts,
        f'{player}_win_games': win_serve_counts,
    }


def get_set_stats(set_soup, n_set):
    tds = set_soup.select('tr')[1].select('td')
    player_serving = ('p2', 'p1') if len(
        tds[1].select('span')) == 0 else ('p1', 'p2')
    odd_game_serve = set_soup.select('tr.odd.fifteens_available')
    odd_game_line = set_soup.select('tr.odd.fifteen')
    even_game_serve = set_soup.select('tr.even.fifteens_available')
    even_game_line = set_soup.select('tr.even.fifteen')
    odd_line_stat = get_match_line_stats(odd_game_line, player_serving[0], n_set)
    odd_serv_stat = get_result_serving(odd_game_serve, player_serving[0], n_set)
    even_line_stat = get_match_line_stats(even_game_line, player_serving[1], n_set)
    even_serv_stat = get_result_serving(even_game_serve, player_serving[1], n_set)
    return {**odd_serv_stat, **odd_line_stat, **even_serv_stat, **even_line_stat}


def sort_order_total_stats(total_stats):
    order = ['p1_win_games', 'p1_lost_games', 'p1_win_points',
             'p1_lost_points', 'p1_win_fp', 'p1_bp', 'p1_sp',
             'p1_points_len', 'p2_win_games', 'p2_lost_games',
             'p2_win_points', 'p2_lost_points', 'p2_win_fp',
             'p2_bp', 'p2_sp', 'p2_points_len']
    ordered_ts = {}
    for key in order:
        ordered_ts[key] = total_stats[key]
    return ordered_ts


def get_total_stats(sets_stats):
    total_stats = Counter()
    for set_stat in sets_stats:
        if len(set_stat) != 16:
            raise Exception(f'Len set stats != 16 = {len(set_stat)}')
        total_stats.update(set_stat)
    return sort_order_total_stats(total_stats)


def get_all_sets_stats(soup, sets_count):
    sets_stats = []
    for i in range(1, sets_count+1):
        set_id = f'tab-mhistory-{i}-history'
        set_soup = soup.select(f'div#{set_id}')[0]
        sets_stats.append(get_set_stats(set_soup, i))
    return get_total_stats(sets_stats)


def get_event_stats(html, url):
    soup = BeautifulSoup(html, 'lxml')
    date = soup.select('div#utime')[0].text
    coverage = soup.select(
        'div.description__match span.description__country a')[0].text.split(',')[1].strip()
    p1 = soup.select('div.home-box div.tname__text a')[0].text.strip()
    p2 = soup.select('div.away-box div.tname__text a')[0].text.strip()
    result_board = soup.select(
        'div#event_detail_current_result span.scoreboard')
    p1_res_score = result_board[0].text
    p2_res_score = result_board[1].text
    match_status = soup.select(
        'div#flashscore div.match-info div.info-status')[0].text.strip()
    sets_count = int(p1_res_score) + int(p2_res_score)
    sets_stats = get_all_sets_stats(soup, sets_count)
    return {
        'url': url,
        'date': date,
        'status': match_status,
        'coverage': coverage,
        'p1': p1,
        'p2': p2,
        'p1_res_score': p1_res_score,
        'p2_res_score': p2_res_score,
        'sets_count': sets_count,
        **sets_stats
    }


# url = 'https://www.flashscore.com/match/MPNrXaWq/#point-by-point;1'
# url = 'https://www.flashscore.com/match/fyXBxdlb/#point-by-point;1'

# print(get_event_stats(get_html(url), url))
