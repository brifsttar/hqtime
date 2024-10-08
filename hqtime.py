import ctypes
import time
from time import sleep
import logging as log
from datetime import datetime as dt
from random import randrange
import os

import keyring
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from config import *

LOG_FORMAT = '%(asctime)-15s [%(levelname)-8s]: %(message)s'


def message_box(title, text, style):
    return ctypes.windll.user32.MessageBoxW(0, text, title, style)


def main():
    log.basicConfig(
        format=LOG_FORMAT,
        level=log.INFO,
        handlers=[
            log.FileHandler("hqtime.log"),
            log.StreamHandler()
        ]
    )
    now = dt.now()
    if not WFH_DAYS:
        # If there's no user-defined WFH days, we ask if current time is earlier than clock-out time
        if now.weekday() > 4:
            return
        h = WFH_HOURS[-1]
        clock_out = now.replace(hour=int(h), minute=int(60 * (h % 1)), second=0)
        if now > clock_out:
            return
    elif now.weekday() not in WFH_DAYS:
        log.info(f"{now} is not WFH")
        return
    r = message_box('HQTime Auto-badgeage', 'WFH today?', 3)
    if r != 6:
        log.info(f"User declined WFH")
        return

    hours = []
    random_offset_range = 30
    now = dt.now()
    for h in WFH_HOURS:
        # Offset in minutes
        offset = randrange(random_offset_range) - (random_offset_range / 2.)
        # To hour
        h += offset / 60
        hour = now.replace(hour=int(h), minute=int(60 * (h % 1)), second=0)
        hours.append(hour)

    while True:
        try:
            # I'd like to use autofill from the browser, but there's a bug which makes autofill not work in headless,
            # so, yeah...
            options = Options()
            # options.use_chromium = True
            options.headless = True
            # HQTime buttons fails at default res
            options.add_argument("window-size=1920,1080")
            # https://stackoverflow.com/questions/79004567/selenium-headless-broke-after-chrome-update
            options.add_argument('--window-position=-2400,-2400')

            chrome_install = ChromeDriverManager().install()

            folder = os.path.dirname(chrome_install)
            chromedriver_path = os.path.join(folder, "chromedriver.exe")

            service = Service(executable_path=chromedriver_path)

            # driver = Edge(executable_path=EDGE_DRIVER_PATH, options=options)
            driver = webdriver.Chrome(service=service, options=options)
            driver.get("https://hqtime.ifsttar.fr/")
            driver.find_element(By.ID, "USERID").send_keys(USERNAME)
            driver.find_element(By.ID, "XXX_PASSWORD").send_keys(keyring.get_password(*PASSWORD))
            driver.find_element(By.ID, 'connect').submit()
            # We need to actually select the password field for it to be autofilled
            # driver.find_element_by_id("XXX_PASSWORD").send_keys(Keys.RETURN)

            delay = 3
            WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'cbx_image'))).click()
            WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'role_2'))).click()
            WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'INDICATORS_cpn_2')))
            driver.find_element(By.XPATH, '//*[@title="WBA"]').click()

            WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'CHKFCT_BAD')))

            badgeages = len(driver.find_elements(By.XPATH,'//div[@id="G"]//table[@role="presentation"]/tbody/tr'))
            if badgeages >= len(hours):
                log.info("Done for the day")
                return
            next_badgeage = hours[badgeages]
            now = dt.now()
            time_to = (next_badgeage - now).total_seconds()
            if time_to < 0:
                log.info("Badging")
                driver.find_element(By.XPATH,'//*[@class="btnbad_btn"]').click()
                WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'modale_title')))
                driver.find_element(By.XPATH,'//div[@class="modale_bottom button"]//input[@value="Oui"]').click()
                sleep(1)
                driver.close()
            else:
                driver.close()
                log.info(f"Sleeping {time_to}s until next badging at {next_badgeage}")
                time.sleep(time_to)
        except Exception as e:
            log.exception(e)


if __name__ == '__main__':
    main()
