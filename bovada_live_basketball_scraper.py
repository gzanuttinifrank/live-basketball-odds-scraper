from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from requests.exceptions import ConnectionError
from bs4 import BeautifulSoup
import time
from csv import writer
from datetime import datetime
from dateutil import tz
from datetime import date
import pytz
import re
import pandas as pd
import itertools
import requests
import numpy as np


def open_bovada(driver, sport, league='', direct_url=True, sleeptime=0):
    if direct_url:
        driver.get('http://www.bovada.lv/sports/' + sport + '/' + league)
        driver.refresh()
    else:
        driver.get('http://www.bovada.lv/sports')
        # navigate to the NFL odds page
        driver.find_element_by_class_name('sec-menu-btn.static-btn').click()
        time.sleep(sleeptime)
        # driver.find_element_by_class_name('icon.static-icon.icon-football').click()
        wait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'sp-tab-bar-btn.static-btn ')))
        btns = driver.find_elements_by_class_name('sp-tab-bar-btn.static-btn ')
        for btn in btns:
            if btn.text == 'Football':
                fb_btn = btn
                break
        fb_btn.click()
        time.sleep(sleeptime)
        wait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'custom-dropdown.custom-field.small-field.inverse.event-path-filter')))
        leagues = driver.find_element_by_class_name('custom-dropdown.custom-field.small-field.inverse.event-path-filter')
        leagues.click()
        time.sleep(sleeptime)
        items = leagues.find_elements_by_tag_name("li")
        for item in items:
            if item.text[0:5] == 'NFL (':
                nfl_item = item
                break
        nfl_item.click()

        # time.sleep(1)
        driver.refresh()


def createID(row):
    gid = todaydate + row.League.replace(" ","") + row.Away_Team.replace(" ","") + row.Home_Team.replace(" ","")
    return gid


def change_odds_format(odds_format):
    # arg format: can take one of: 'American' 'Decimal' or 'Fractional'
    new_odds_format = odds_format + ' Odds'
    # switch to decimal odds
    wait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'sp-odds-format-selector-filter')))
    odds_type_list = driver.find_element_by_class_name('sp-odds-format-selector-filter')
    # odds_type = driver.find_element_by_class_name('custom-dropdown.custom-field.small-field')
    odds_type_list.click()
    wait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'active')))
    items = odds_type_list.find_elements_by_tag_name("li")
    for item in items:
        if item.text.strip() == new_odds_format:
            item.click()
            break


def show_all_games():
    # show all games
    try:
        wait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'show-all-button')))
        try:
            show_all_btn = driver.find_element_by_class_name('show-all-button')
        except NoSuchElementException:
            raise TimeoutException
        if show_all_btn:
            try:
                show_all_btn.click()
            except (ElementClickInterceptedException, StaleElementReferenceException):
                reget_site(rest_time=3)
                # show_all_games()
    except TimeoutException:
        pass


def reget_site(endtime=None, min_sleep=5, rest_time=15):
    # min_sleep is the minimum number of seconds to sleep before reloading the website
    # sleep
    if not endtime:
        endtime = time.time()
    sleeptime = max((rest_time - (int(endtime) % rest_time) + np.random.randn(1) * 2)[0], min_sleep)
    # print(sleeptime)
    time.sleep(sleeptime)
    # refresh
    driver.refresh()
    # show all games
    show_all_games()


def append_nan(*args):
    res = []
    for arg in args:
        to_append = arg
        to_append.append(np.nan)
        res.append(to_append)
    return res


def start_driver():
    open_bovada(driver, 'basketball')
    change_odds_format('Decimal')
    show_all_games()
    consecutive_failures = 0
    consecutive_nothing_happening = 0


CHROME_PATH = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
CHROMEDRIVER_PATH = '/Users/gzanuttinifrank/Desktop/chromedriver'
WINDOW_SIZE = "1920,1080"

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
chrome_options.binary_location = CHROME_PATH


driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=chrome_options)
start_driver()

# open_bovada(driver, 'basketball')
curr_url = driver.current_url
consecutive_failures = 0
consecutive_nothing_happening = 0

# change_odds_format('Decimal')

# show_all_games()

sleeptime = 15 - int(time.time()) % 15
time.sleep(sleeptime)


with open('/Users/gzanuttinifrank/Documents/data/bovada/basketball/basketball_live_odds_bovada.csv', 'a') as f:
    while True:
        try:
            wait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'period')))
        except TimeoutException:
            print("Failed iteration of loop")
            consecutive_failures += 1
            if consecutive_failures == 4:
                print("Restarting driver")
                driver.quit()
                driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=chrome_options)
                start_driver()
            else:
                reget_site(rest_time=5)
            continue

        consecutive_failures = 0

        starttime = time.time()
        print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())))

        try:
            page = requests.get(curr_url)
        except ConnectionError:
            print("Failed: connection error")
            reget_site(rest_time=30)
            continue
        try:
            wait(driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'happening-now-bucket')))
        except TimeoutException:
            print("Failed: could not find 'happening-now-bucket'")
            consecutive_nothing_happening += 1
            if consecutive_nothing_happening == 10:
                print("Restarting driver")
                driver.quit()
                driver = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, options=chrome_options)
                start_driver()
            else:
                reget_site(rest_time=60)
            continue
        consecutive_nothing_happening = 0
        live_events = driver.find_element_by_class_name('happening-now-bucket')
        le_html = live_events.get_attribute('innerHTML')
        soup = BeautifulSoup(le_html, 'html.parser')

        localtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        todaydate = str(date.today()).replace("-", "")

        gametimes = soup.find_all(class_='period')
        gt_strings = [gt.get_text().strip() for gt in gametimes]
        periods = [gt[0:2] for gt in gt_strings][::2]
        time_rem = [gt[2:] for gt in gt_strings][::2]

        # scores = soup.find_all(class_='score-nr')
        # print("Num of scores", len(scores) / 4)
        # if len(scores) == 0:
        #     reget_site(min_sleep=1)
        #     continue
        # scores = [pd.to_numeric(s.get_text()) for s in scores]
        # away_scores = scores[::4]
        # home_scores = scores[1::4]

        leagues = soup.find_all(class_='league-header')
        league_names = []
        grouped_events = soup.find_all(class_='grouped-events')
        for i in range(len(grouped_events)):
            event = grouped_events[i]
            league_names += [leagues[i].get_text()] * len(event.find_all(class_='coupon-container multiple live-game'))

        teams = soup.find_all(class_='name')
        team_names = [team.get_text() for team in teams]
        away_teams = team_names[::2]
        home_teams = team_names[1::2]

        away_ml = []
        home_ml = []
        home_scores = []
        away_scores = []
        games = soup.find_all(class_='coupon-content more-info')
        for i in range(len(games)):
            game = games[i]
            results = game.find(class_='results')
            try:
                scores = results.find_all(class_='score-nr')
            except AttributeError:
                print("AttributeError in scores")
                away_scores, home_scores, away_ml, home_ml = append_nan(away_scores, home_scores, away_ml, home_ml)
                continue
            if scores:
                a_score = pd.to_numeric(scores[0].get_text())
                h_score = pd.to_numeric(scores[1].get_text())
            else:
                a_score = np.nan
                h_score = np.nan
            away_scores.append(a_score)
            home_scores.append(h_score)
            market_cont = game.find(class_='markets-container')
            ml_market = market_cont.find_all(class_='market-type')[1]
            items = ml_market.find_all(class_='bet-price')
            if (ml_market.find(class_='suspended')) or (len(items) == 0):
                away_ml, home_ml = append_nan(away_ml, home_ml)
                continue
            else:
                if abs(pd.to_numeric(items[0].get_text().strip().replace("EVEN", '2'))) > 99:
                    change_odds_format('Decimal')
                    away_scores = []
                    break
                if len(items) == 1:
                    price = pd.to_numeric(items[0].get_text().strip().replace("EVEN", '2'))
                    score_diff = a_score - h_score
                    if (price > 2 and score_diff > 0) or (price < 2 and score_diff < 0):
                        home_ml.append(price)
                        away_ml.append(np.nan)
                    else:
                        home_ml.append(np.nan)
                        away_ml.append(price)
                else:
                    away_ml.append(pd.to_numeric(items[0].get_text().strip().replace("EVEN", '2')))
                    home_ml.append(pd.to_numeric(items[1].get_text().strip().replace("EVEN", '2')))

        if len(away_scores) == 0 or sum(~np.isnan(away_scores)) == 0:
            reget_site()
            continue

        df_dict = {'Period': periods, 'Time_Remaining': time_rem, 'League': league_names, 'Away_Team': away_teams,
                   'Home_Team': home_teams, 'Away_Score': away_scores, 'Home_Score': home_scores, 'Away_Line': away_ml,
                   'Home_Line': home_ml}
        # print('Period', len(periods))
        # print('Time_Remaining', len(time_rem))
        # print('League', len(league_names))
        # print('Away_Team', len(away_teams))
        # print('Home_Team', len(home_teams))
        print('Away_Score', len(away_scores), away_scores)
        print('Home_Score', len(home_scores), home_scores)
        print('Away_Line', len(away_ml), away_ml)
        print('Home_Line', len(home_ml), home_ml)
        try:
            odds_df = pd.DataFrame(df_dict,
                                   columns=['Period', 'Time_Remaining', 'League', 'Away_Team', 'Home_Team', 'Away_Score',
                                            'Home_Score', 'Away_Line', 'Home_Line'])
        except ValueError:
            print("ValueError: arrays must all be same length")
            print('Period', len(periods))
            print('Time_Remaining', len(time_rem))
            print('League', len(league_names))
            print('Away_Team', len(away_teams))
            print('Home_Team', len(home_teams))
            print('Away_Score', len(away_scores), away_scores)
            print('Home_Score', len(home_scores), home_scores)
            print('Away_Line', len(away_ml), away_ml)
            print('Home_Line', len(home_ml), home_ml)
            print("\n\n\n")
            reget_site()
            continue
        game_ids = odds_df.apply(createID, axis=1)
        odds_df['GameID'] = game_ids
        odds_df['Scrape_Time'] = localtime

        odds_df.to_csv(f, header=False)

        endtime = time.time()
        print('Time diff:', endtime - starttime)

        reget_site(endtime=endtime)
