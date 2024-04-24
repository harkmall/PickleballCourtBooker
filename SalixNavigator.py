from loguru import logger
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
import selenium.common.exceptions as Exceptions
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from PickleballCourtBooker import app
import Config
import Helpers
import re
import time

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
    logger.info("Building next week's XPATH")
    today_cell_xpath = Helpers.generateXPATH(today_cell, "")
    today_split_xpath = today_cell_xpath.split("/")
    row_string = today_split_xpath[-3]
    row_number = re.search(r"tr\[(\d+)\]", row_string).group(1)
    next_row_number = int(row_number) + 1
    today_split_xpath[-3] = f"tr[{next_row_number}]"
    if app.debug:
        day_string = today_split_xpath[-2]
        day_number = re.search(r"td\[(\d+)\]", day_string).group(1)
        next_week_day_plus_one_number = int(day_number) + 1
        today_split_xpath[-2] = f"td[{next_week_day_plus_one_number}]"
    next_week_cell_xpath = "/".join(today_split_xpath)
    logger.success("Built next week XPATH")

    logger.info("Clicking on next week")
    driver.find_element(By.XPATH, next_week_cell_xpath).click()
    logger.success("Clicked on next week cell")

    logger.info("Waiting for loading to finish")
    loading_bar = driver.find_element(By.CLASS_NAME, "v-loading-indicator")
    while True:
        loading_bar_style = loading_bar.get_attribute('style')
        if loading_bar_style == r"position: absolute; display: block;":
            break
        else:
            time.sleep(.05)
    while True:
        loading_bar_style = loading_bar.get_attribute('style')
        if loading_bar_style == r"position: absolute; display: none;":
            break
        else:
            time.sleep(.05)
    logger.success("Loading bar shown and gone")

    logger.info("Looking for open 6pm slot")
    # court 5 for some reason books in 1 hour slots... not sure how to deal with that yet
    timeslot_calendar_xpath = "/html/body/div[1]/div/div[2]/div/div[2]/div/div/div/div[2]/div/div/div/div/div[2]/div" #ugly, but I think necessary
    timeslot_calendar = driver.find_element(By.XPATH, timeslot_calendar_xpath)
    court_columns = timeslot_calendar.find_elements(By.XPATH, "div")
    for column in court_columns:
        day_slots_div = column.find_element(By.CLASS_NAME, "v-calendar-day-times")
        open_time_slots = day_slots_div.find_elements(By.CLASS_NAME, "v-calendar-event-prime-time")
        if len(open_time_slots) == 0:
            continue
        for open_time_slot in open_time_slots:
            time_label = open_time_slot.find_element(By.XPATH, "div/span").text
            if time_label != "6:00 PM":
                continue

            logger.success("Found open 6pm slot")
            open_time_slot.click()
            logger.info("Waiting for booking popup")
            wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "popupContent")))
            popup = driver.find_element(By.CLASS_NAME, "popupContent")
            logger.success("Booking popup opened")
            logger.info("Looking for 'Social Reservation' button")
            popup.find_element(By.XPATH, "//label[contains(text(),'Social Reservation')]").click()
            logger.success("Clicked 'Social Reservation' button")
            logger.info("Waiting for booking info to load")
            wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "v-form-content")))
            logger.success("Booking info loaded")

            error_wait = WebDriverWait(driver, 2)
            counter = 0
            while counter < 10:
                try:
                    logger.info("Looking for 'OK' button")
                    ok_button = popup.find_element(By.XPATH, "//span[contains(text(), 'OK')]")
                    driver.execute_script("arguments[0].click();", ok_button)
                    logger.success("Clicked 'OK' button")
                    logger.info("Waiting for error popup")
                    error_wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "v-Notification-error"))).click()
                    logger.success(f"Closed error popup. Retries left: {10-counter}")
                    counter += 1
                except Exceptions.NoSuchElementException:
                    logger.success("Error popup is not showing, booking succeeded")
                    return True
                except Exceptions.TimeoutException:
                    logger.success("Error popup is not showing, booking succeeded")
                    return True

            logger.success("Ran out of retries")
            return False

    logger.success("No open 6pm slots available")
    return False
