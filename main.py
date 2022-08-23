import time
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import pandas as pd

URL =  "https://snokinghockeyleague.com/#/home/team/1079/2609"
OUTPUT_FILE_NAME = "schedule.csv"
TEAM_NAME = "mid ice crisis"

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
                "Date": {}, 
                "Time": {},
                "Rink": {},
                "Home": {}
                }

teamName = TEAM_NAME.lower()
for i in range(len(schedule[1:])):
    game = schedule[i+1]
    date = game.find_next("td")
    gameTime = date.find_next("td").find_next("td")
    rink = gameTime.find_next("td")
    isHome = rink.find_next("td").getText().lower() == teamName
    gameSchedule['Date'][i+1] = date.getText()
    gameSchedule['Time'][i+1] = gameTime.getText()
    gameSchedule['Rink'][i+1] = rink.getText()
    gameSchedule['Home'][i+1] = isHome

df = pd.DataFrame(gameSchedule)
df.to_csv(OUTPUT_FILE_NAME, index=False)