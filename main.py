import time, os
from datetime import datetime
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL =  "https://snokinghockeyleague.com/#/home/team/1081/2609" # enter team url here for the season
GAME_DURATION = "1:30"
TYPE = "GAME"
GAME_TYPE = "REGULAR"
EMAIL = ""
PASSWORD = ""

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
fileName = f"{URL.split('/')[-1]}.csv"

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
        gameSchedule['Title'][i+1] = ""
        gameSchedule['Type'][i+1] = TYPE
        gameSchedule['Game Type'][i+1] = GAME_TYPE
        gameSchedule['Home'][i+1] = home.getText()
        gameSchedule['Away'][i+1] = away.getText()
        gameSchedule['Date'][i+1] = date.strftime("%d/%m/%Y")
        gameSchedule['Time'][i+1] = gameTime.getText()
        gameSchedule['Duration'][i+1] = GAME_DURATION
        gameSchedule['Location'][i+1] = rink.getText()

df = pd.DataFrame(gameSchedule)
df.to_csv(fileName, index=False)

if EMAIL and PASSWORD:
    driver.get("https://www.benchapp.com/schedule/import")
    driver.find_element(By.NAME, "email").send_keys(EMAIL)
    driver.find_element(By.NAME, "password").send_keys(PASSWORD)
    current_url = driver.current_url
    driver.find_element(By.XPATH, "/html/body/div[1]/div[2]/div[1]/div/div[2]/div/form/div[3]/span/button").click()
    WebDriverWait(driver, 30).until(EC.url_changes(current_url))
    browse = driver.find_element(By.XPATH, "/html/body/div[1]/div[7]/section/div[2]/div/div/section/div[1]/div/div[2]/div/label/input")
    browse.send_keys(f"{os.getcwd()}/{fileName}")
    time.sleep(5)
    driver.find_element(By.XPATH, "/html/body/div[1]/div[7]/section/div[2]/div/div/section/div[1]/div/div[3]/div[2]/div/div/div[3]/div/div[2]/button[2]/span").click()
    time.sleep(5)

driver.close()
print("Done!")