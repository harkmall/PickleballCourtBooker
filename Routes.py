from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
import selenium.common.exceptions as Exceptions
from flask import request, Response
from loguru import logger
from PickleballCourtBooker import app
import SalixNavigator
import Messaging
import requests

@app.route("/book-court", methods=["POST"])
def respond():
    try:
        logger.success("Received request")
        if app.debug:
            driver = webdriver.Firefox()
        else:
            options = webdriver.FirefoxOptions()
            driver = webdriver.Remote(
                command_executor="http://192.168.13.152:4444/wd/hub", options=options
            )
                
        wait = WebDriverWait(driver, 10)

        court_booked = SalixNavigator.bookCourts(driver=driver, wait= wait)
        message = "Court booked for next week @ 6pm" if court_booked else "No courts available next week @ 6pm"
        Messaging.sendEmail(messageBody=message)

        return Response(status=200)
    
    except Exceptions.NoSuchElementException as exception:
        logger.error(exception.msg)
        Messaging.sendEmail("Court Booker: Something broke :(")
        return str(exception), 404
    except Exceptions.TimeoutException as exception:
        logger.error(exception.msg)
        Messaging.sendEmail("Court Booker: Something broke :(")
        return str(exception), 504
    except Exceptions.NoSuchFrameException as exception:
        logger.error(exception.msg)
        Messaging.sendEmail("Court Booker: Something broke :(")
        return str(exception), 404
    except Exception as exception: #pylint: disable=broad-exception-caught
        logger.error(exception)
        Messaging.sendEmail("Court Booker: Something broke :(")
        return str(exception), 500
    finally:
        # send ping to uptime monitor
        if not app.debug:
            requests.get("https://hc-ping.com/548d3824-965a-4405-8bcb-aa37383923cf", timeout=10)
        logger.info("Closing browser")
        driver.quit()
        logger.success("Browser Closed")