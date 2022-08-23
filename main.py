import time
from datetime import datetime
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import pandas as pd

URL =  "https://snokinghockeyleague.com/#/home/team/1081/2609" # enter team url here for the season
OUTPUT_FILE_NAME = "schedule.csv"
GAME_DURATION = "1:30"
TYPE = "GAME"
GAME_TYPE = "REGULAR"


options = Options()
options.headless = True
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
driver.get(URL)
time.sleep(3)
scheduleLink = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/div/div/div/div/div/fieldset/div/div/div[2]/div/div/ul/li[2]/a')
scheduleLink.click()
time.sleep(3)
html = driver.page_source
MySoup = BeautifulSoup(html, "html.parser")
results = MySoup.find(name="h4", text="Schedule").find_next(name="table")
schedule = results.find_all("tr")

gameSchedule = {
                "Type": {},
                "Game Type": {},
                "Home": {},
                "Away": {},
                "Date": {}, 
                "Time": {},
                "Duration": {},
                "Location": {},
                }
                
today = datetime.now()
for i in range(len(schedule[1:])):
    game = schedule[i+1]
    rawDate = game.find_next("td")
    date = datetime.strptime(rawDate.getText(), "%m/%d/%Y")
    if date.date() > today.date():
        gameTime = rawDate.find_next("td").find_next("td")
        rink = gameTime.find_next("td")
        home = rink.find_next("td")
        away = home.find_next("td")
        gameSchedule['Type'][i+1] = TYPE
        gameSchedule['Game Type'][i+1] = GAME_TYPE
        gameSchedule['Home'][i+1] = home.getText()
        gameSchedule['Away'][i+1] = away.getText()
        gameSchedule['Date'][i+1] = date.strftime("%d/%m/%Y")
        gameSchedule['Time'][i+1] = gameTime.getText()
        gameSchedule['Duration'][i+1] = GAME_DURATION
        gameSchedule['Location'][i+1] = rink.getText()
    else:
        continue

df = pd.DataFrame(gameSchedule)
df.to_csv(OUTPUT_FILE_NAME, index=False)