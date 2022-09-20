import time, os, requests, smtplib
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

TEAM_ID =  2706 # enter team number
GAME_DURATION = "1:15"
TYPE = "GAME"
SEASON_ID = 1082
TEAM_NAME = "warriors"

def find_season(seasons):
    for season in seasons:
        if "skahl" in season['name'].lower():
            return season

def is_playoffs(season):
    return "playoffs" in season['name'].lower() 

def email_for_error(theMessage):
    conn = smtplib.SMTP('smtp.gmail.com', 587)
    conn.ehlo()
    conn.starttls()
    conn.login(os.getenv('FROM_EMAIL'), os.getenv('FROM_EMAIL_PASSWORD'))
    conn.sendmail(os.getenv('FROM_EMAIL'), os.getenv('EMAIL'), f"Subject: Schedule conflict found \n\n {theMessage}")
    conn.quit()

scriptPath = os.path.dirname(__file__)
# response = requests.get("https://api.codetabs.com/v1/proxy/?quest=https://snokinghockeyleague.com/api/season/all/0")
# seasons = response.json()['seasons']
# season = find_season(seasons)
# gameType = "PLAYOFF" if is_playoffs(season) else "REGULAR"
gameType = "REGULAR"
url = f"https://api.codetabs.com/v1/proxy/?quest=https://snokinghockeyleague.com/api/game/list/{SEASON_ID}/0/{TEAM_ID}"
fileName = f"{TEAM_ID}.csv"
response = requests.get(url)
schedule = response.json()


try:
    df = pd.read_csv(f"{scriptPath}/{fileName}")
    recentDate = datetime.strptime(df['Date'].iloc[-1], "%d/%m/%Y")
    gameSchedule = df.to_dict()
except:
    recentDate = datetime.now()
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
                "Notes": {},
                }

needsUpdate = False

for i in range(len(schedule)):
    game = schedule[i]
    date = datetime.strptime(game['date'], "%m/%d/%Y")
    errorState = False
    if date < recentDate:
        errorState = (gameSchedule['Home'][i] != game['teamHomeName'] or gameSchedule['Away'][i] != game['teamAwayName'] or gameSchedule['Time'][i] != game['time'])
    if errorState:
        email_for_error(f"Error for game on {date.strftime('%m/%d/%Y')} {gameSchedule['Away'][i]} @ {gameSchedule['Home'][i]}")
    if errorState or date > recentDate:   
        needsUpdate = True 
        gameSchedule['Title'][i] = ""
        gameSchedule['Type'][i] = TYPE
        gameSchedule['Game Type'][i] = gameType
        gameSchedule['Home'][i] = game['teamHomeName']
        gameSchedule['Away'][i] = game['teamAwayName']
        gameSchedule['Date'][i] = savedDate = date.strftime("%d/%m/%Y")
        gameSchedule['Time'][i] = game['time']
        gameSchedule['Duration'][i] = GAME_DURATION
        gameSchedule['Location'][i] = game['rinkName']
        gameSchedule['Notes'] = "Dark sweaters" if TEAM_NAME in game['teamHomeName'].lower() else "Light sweaters"

if needsUpdate:
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
    driver.close()