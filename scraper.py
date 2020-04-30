import requests
import urllib.request
from bs4 import BeautifulSoup
from datetime import datetime
import time
import csv
from selenium import webdriver
import schedule
from lxml import html

def retrieve_website():
    headers = {'user-agent': 'Mozilla/5.0 (X11, Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari.537.17'}
    url = 'https://www.vesselfinder.com/vessels/FREYJA-W-IMO-9754422-MMSI-212792000'
    reqs = requests.get(url, headers=headers)
    soup = BeautifulSoup(reqs.content, 'lxml')
    with open('output.html', 'w', encoding='utf-8') as file:
        file.write(str(soup))
    with open('output.html', 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'lxml')

    data = soup.find_all('td')
    coordinates = data[21].get_text()

    dtg_str_soup = BeautifulSoup(str(data[25]), features='lxml')
    dtg = dtg_str_soup.td['data-title']

    head_sp = data[19].get_text()
    heading = head_sp.split(' / ')[0]
    speed = head_sp.split(' / ')[1]

    coordinates = str(coordinates)
    print(coordinates)
    north = coordinates.split(('/'))[0]
    east = coordinates.split(('/'))[1]

    dtg = dtg.replace(',', '').split('UTC')
    print(str(dtg[0]).strip())
    dtg = datetime.strptime(str(dtg[0]).strip(), '%b %d %Y %H:%M')
    date = dtg.strftime('%Y-%m-%d')
    current_time = dtg.strftime('%H:%M')

    global ctr

    with open('AIS_track.csv', 'a', newline='') as csv_file:
        writer = csv.writer(csv_file, delimiter=',')
        writer.writerow([ctr, north, east, date, current_time, heading, speed])

    dtg = datetime.now()
    screenshot = dtg.strftime("screenshoots/%Y%m%d_%H%M_screenshot.png")

    img_rul = soup.find_all('a', href=True)
    img_rul = img_rul[22]['href']

    DRIVER = 'chromedriver'
    driver = webdriver.Chrome(DRIVER)
    driver.get('https://www.vesselfinder.com/'+img_rul)
    time.sleep(5)
    driver.save_screenshot(screenshot)
    driver.quit()

    print(ctr, 'Last AIS data was sent at:', current_time, 'UTC')

    ctr =+ 1

ctr = 0

retrieve_website()

schedule.every(900).seconds.do(retrieve_website)
while True:
    schedule.run_pending()
    time.sleep(1)

