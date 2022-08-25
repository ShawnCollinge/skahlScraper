import time, os, requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
load_dotenv()

TEAM_ID =  "2200" # enter team number
GAME_DURATION = "1:15"
TYPE = "GAME"

def find_season(seasons):
    for season in seasons:
        if "skahl" in season['name'].lower():
            return season

def is_playoffs(season):
    return "playoffs" in season['name'].lower() 

scriptPath = os.path.dirname(__file__)

response = requests.get("https://api.codetabs.com/v1/proxy/?quest=https://snokinghockeyleague.com/api/season/all/0")
seasons = response.json()['seasons']

season = find_season(seasons)
gameType = "PLAYOFF" if is_playoffs(season) else "REGULAR"
url = f"https://api.codetabs.com/v1/proxy/?quest=https://snokinghockeyleague.com/api/game/list/{season['id']}/0/{TEAM_ID}"
fileName = f"{TEAM_ID}.csv"

response = requests.get(url)
schedule = response.json()

gameSchedule = {
                "Type": {},
                "Game Type": {},
                "Title": {},
                "Home": {},
                "Away": {},
                "Date": {}, 
                "Time": {},
                "Duration": {},
                "Location": {},
                }

with open(f"{scriptPath}/recentDate.txt", "r") as f:
    recentDate = datetime.strptime(f.read(), "%d/%m/%Y")

for i in range(len(schedule)):
    game = schedule[i]
    date = datetime.strptime(game['date'], "%m/%d/%Y")
    if date.date() > recentDate.date():
        gameSchedule['Title'][i+1] = ""
        gameSchedule['Type'][i+1] = TYPE
        gameSchedule['Game Type'][i+1] = gameType
        gameSchedule['Home'][i+1] = game['teamHomeName']
        gameSchedule['Away'][i+1] = game['teamAwayName']
        gameSchedule['Date'][i+1] = savedDate = date.strftime("%d/%m/%Y")
        gameSchedule['Time'][i+1] = game['time']
        gameSchedule['Duration'][i+1] = GAME_DURATION
        gameSchedule['Location'][i+1] = game['rinkName']
        recentDate = date


if len(gameSchedule['Title']) > 0:
    df = pd.DataFrame(gameSchedule)
    df.to_csv(f"{scriptPath}/{fileName}", index=False)

    options = Options()
    options.headless = True
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get("https://www.benchapp.com/schedule/import")
    driver.find_element(By.NAME, "email").send_keys(os.getenv('EMAIL'))
    driver.find_element(By.NAME, "password").send_keys(os.getenv('PASSWORD'))
    current_url = driver.current_url
    driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[1]/div/div[2]/div/form/div[3]/span/button").click()
    WebDriverWait(driver, 30).until(EC.url_changes(current_url))
    browse = driver.find_element(By.XPATH, "/html/body/div[1]/div[7]/section/div[2]/div/div/section/div[1]/div/div[2]/div/label/input")
    browse.send_keys(f"{scriptPath}/{fileName}")
    time.sleep(5)
    driver.find_element(By.XPATH, "/html/body/div[1]/div[7]/section/div[2]/div/div/section/div[1]/div/div[3]/div[2]/div/div/div[3]/div/div[2]/button[2]/span").click()
    time.sleep(5)

    os.remove(f"{scriptPath}/{fileName}") 
    driver.close()
    with open(f"{scriptPath}/recentDate.txt", "w") as f:
        f.write(savedDate)