from loguru import logger
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import Config
import Helpers
import re

def bookCourts(driver: webdriver.Firefox, wait: WebDriverWait):
    
    logger.info("Loading Salix Website")
    driver.get(Config.salix_website)
    logger.success("Loaded Salix Website")

    logger.info("Waiting for username input")
    wait.until(EC.element_to_be_clickable((By.ID, "username")))
    driver.find_element(By.ID, "username").send_keys(Config.salix_username)
    logger.success("Filled in username")

    logger.info("Looking for password input")
    driver.find_element(By.ID, "password").send_keys(Config.salix_password)
    logger.success("Filled in password")

    logger.info("Looking for login button")
    driver.find_element(By.ID, "kc-login").click()
    logger.success("Clicked login")

    logger.info("Waiting for logged-in site to load")
    reservations_xpath = "//span[contains(text(),'Pickleball reservations')]"
    wait.until(EC.element_to_be_clickable((By.XPATH, reservations_xpath)))
    driver.find_element(By.XPATH, reservations_xpath).click()
    logger.success("Clicked 'Pickelball reservations'")

    logger.info("Waiting for calendar to load")
    wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Pickle 1')]")))
    logger.success("Calendar loaded")

    # #going to click on the 'Today' button just to make sure it's always starting from today
    # logger.info("Clicking on the 'Today' button")
    # driver.find_element(By.XPATH, "//span[contains(text(), 'Today')]").click()
    # logger.success("Clicked on 'Today'")
    # ##might have to wait for loading here

    logger.info("Opening date selector")
    driver.find_element(By.CSS_SELECTOR, "div.v-slot-borderless:nth-child(4)").click()
    logger.success("Opened date selector")

    logger.info("Waiting for date selector to load")
    date_selector_css_selector = ".v-inline-datefield-calendarpanel-body"
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, date_selector_css_selector)))
    logger.success("Date selector loaded")

    logger.info("Looking for today's date")
    today_cell = driver.find_element(By.CSS_SELECTOR, ".v-inline-datefield-calendarpanel-day-today")
    logger.success("Found today's date")

    # /html/body/div[2]/div[2]/div/div/div[3]/div/div/table/tbody/tr[2]/td/table/tbody/tr[2]/td[6]/span
    logger.info("Building next week's XPATH")
    today_cell_xpath = Helpers.generateXPATH(today_cell, "")
    today_split_xpath = today_cell_xpath.split("/")
    row_string = today_split_xpath[-3]
    row_number = re.search(r"tr\[(\d+)\]", row_string).group(1)
    next_row_number = int(row_number) + 1
    today_split_xpath[-3] = f"tr[{next_row_number}]"
    next_week_cell_xpath = "/".join(today_split_xpath)
    logger.success("Built next week XPATH")

    logger.info("Clicking on next week")
    driver.find_element(By.XPATH, next_week_cell_xpath).click()
    logger.success("Clicked on next week cell")

# .v-panel-content > div:nth-child(1) > div:nth-child(1)

# v-calendar-event v-calendar-event-prime-time
# v-calendar-event v-calendar-event-prime-time

