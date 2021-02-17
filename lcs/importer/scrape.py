import requests
import time
import json
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from lcs.secrets.riot import RIOT_USERNAME, RIOT_PASSWORD


class MatchHistoryScraper:

  def __init__(self, url):
    self.url = url

  def get_player_stats(self, soup):
    champ = soup.find("div", class_="champion-icon").div.get("data-rg-id").strip()
    strings_for_player = list(soup.stripped_strings)
    # 0 18
    # 1 IMT Revenge
    # 2 4
    # 3 /
    # 4 3
    # 5 /
    # 6 4
    # 7 320
    # 8 16.4k

    stats = {
      "summonerName": strings_for_player[1],
      "champion": champ,
      "stats": {
        "kills": strings_for_player[2],
        "deaths": strings_for_player[4],
        "assists": strings_for_player[6],
        "firstBlood": False,
        "gold": int(float(strings_for_player[8].replace('k', '')) * 1000),
        "minions": strings_for_player[7],
      }
    }
    return stats

  def get_obj_stats(self, soup):
    objectives = {
      "dragons": soup.find("div", class_="dragon-kills").span.string,
      "barons": soup.find("div", class_="baron-kills").span.string,
      "turrets": soup.find("div", class_="tower-kills").span.string,
    }
    return objectives

  def get_team_stats(self, team_html):

    player_data_list = [self.get_player_stats(p) for p in team_html.find_all('div', class_="classic player")]
    return {
      "players": player_data_list,
      "teamStats": self.get_obj_stats(team_html)
    }

  def run(self):
    s = requests.Session()
    driver = webdriver.Chrome(executable_path="/Users/mdai/Documents/chromedriver")

    driver.get(self.url)
    signin = driver.find_element_by_link_text("SIGN IN")
    signin.click()

    username_input = driver.find_element_by_name("username")
    username_input.clear()
    username_input.send_keys(RIOT_USERNAME)


    password_input = driver.find_element_by_name("password")
    password_input.clear()
    password_input.send_keys(RIOT_PASSWORD)
    password_input.send_keys(Keys.RETURN)

    element = WebDriverWait(driver, 10).until(
      EC.presence_of_element_located((By.CSS_SELECTOR, ".minions-col"))
    )

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'lxml')

    team_b = soup.find("div", class_="classic team-100 team")
    team_r = soup.find("div", class_="classic team-200 team")

    winning_team = "blue" if team_b.find("div", class_="game-conclusion").string.strip() == "VICTORY" else "red"

    match_stat = {
      "blueTeam": self.get_team_stats(team_b),
      "redTeam": self.get_team_stats(team_r),
      "winner": winning_team,
      "gameDuration": soup.find("span", class_="map-header-duration").div.string,
      "date": soup.find("span", class_="map-header-date").div.string,
      "url": self.url,
    }

    FIRST_BLOOD_ROW_INDEX = 5
    detailed_stats = soup.find("tbody", id="stats-body")
    fb_first_player_elem = detailed_stats.contents[FIRST_BLOOD_ROW_INDEX].find("div", class_="grid-cell")
    first_blood_elem = detailed_stats.find("div", text="●")
    first_blood_index = int(first_blood_elem.get("id").split("-")[-1]) - int(fb_first_player_elem.get("id").split("-")[-1])
    
    if first_blood_index < 5:
      match_stat["blueTeam"]["players"][first_blood_index % 5]["stats"]["firstBlood"] = True
    else:
      match_stat["redTeam"]["players"][first_blood_index % 5]["stats"]["firstBlood"] = True

    with open("match_importer.txt", 'w')  as file:
      file.write(json.dumps(match_stat, indent=2))
    return match_stat

