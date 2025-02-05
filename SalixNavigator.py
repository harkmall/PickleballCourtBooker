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

def bookCourts(driver: webdriver.Firefox, wait: WebDriverWait):
    
    logger.info("Loading Salix Website")
    driver.get(Config.salix_website)
    logger.success("Loaded Salix Website")

    logger.info("Waiting for username input")
    wait.until(EC.element_to_be_clickable((By.ID, "user-text-field")))
    driver.find_element(By.ID, "user-text-field").send_keys(Config.salix_username)
    logger.success("Filled in username")

    logger.info("Looking for password input")
    driver.find_element(By.ID, "password-text-field").send_keys(Config.salix_password)
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
    # next_row_number = int(row_number) + 2 #testing with 2 weeks away, TAKE THIS OUT
    today_split_xpath[-3] = f"tr[{next_row_number}]"
    next_week_cell_xpath = "/".join(today_split_xpath)
    logger.success("Built next week XPATH")

    logger.info("Clicking on next week")
    driver.find_element(By.XPATH, next_week_cell_xpath).click()
    logger.success("Clicked on next week cell")

    logger.info("Waiting for calendar to disappear")
    wait.until(EC.invisibility_of_element_located((By.CSS_SELECTOR, date_selector_css_selector)))
    logger.success("Calendar disappeared")

    logger.info("Looking for open 6pm slot")
    # court 5 for some reason books in 1 hour slots... not sure how to deal with that yet
    timeslot_calendar_xpath = "/html/body/div[1]/div/div[2]/div/div[2]/div/div/div/div[2]/div/div/div/div/div[2]/div" #ugly, but I think necessary
    timeslot_calendar = driver.find_element(By.XPATH, timeslot_calendar_xpath)
    court_columns = timeslot_calendar.find_elements(By.XPATH, "div")
    logger.info("Looping through columns")
    for column in court_columns:
        logger.info(f"Looking at column {column}")
        day_slots_div = column.find_element(By.CLASS_NAME, "v-calendar-day-times")
        open_time_slots = day_slots_div.find_elements(By.CLASS_NAME, "v-calendar-event-prime-time")
        logger.success(f"Found {open_time_slots} open time slots in column {column}")
        if len(open_time_slots) == 0:
            logger.success(f"No open time slots in column {column}")
            continue
        for open_time_slot in open_time_slots:
            logger.info(f"Looking for time labels in open time slot in column {column}")
            time_label = open_time_slot.find_element(By.XPATH, "div/span").text
            logger.info(f"Found time label {time_label} in open time slot in column {column}")
            if app.debug:
                if time_label != "8:00 PM":
                    continue
            elif time_label != "6:00 PM":
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

            error_wait = WebDriverWait(driver, 5)
            counter = 0
            total_tries = 300
            while counter < total_tries:
                try:
                    logger.info("Looking for 'OK' button")
                    ok_button = popup.find_element(By.XPATH, "//span[contains(text(), 'OK')]")
                    driver.execute_script("arguments[0].click();", ok_button)
                    logger.success("Clicked 'OK' button")
                    logger.info("Waiting for error popup")
                    error_wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "v-Notification-error"))).click()
                    logger.success(f"Closed error popup. Retries left: {total_tries-counter}")
                    counter += 1
                except Exceptions.NoSuchElementException:
                    logger.success("Error popup is not showing, booking succeeded")
                    return (True, "Court booked for next week @ 6pm")
                except Exceptions.TimeoutException:
                    logger.success("Error popup is not showing, booking succeeded")
                    return (True, "Court booked for next week @ 6pm")

            logger.success("Ran out of retries")
            return (False, "Ran out of retries")

    logger.success("No open 6pm slots available")
    return (False, "No open 6pm slots available")
