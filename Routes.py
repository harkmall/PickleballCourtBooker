from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
import selenium.common.exceptions as Exceptions
from flask import request, Response
from loguru import logger
from PickleballCourtBooker import app
import SalixNavigator

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
                
        wait = WebDriverWait(driver, 60)
        
        SalixNavigator.bookCourts(driver=driver, wait= wait)

        return Response(status=200)
    
    except Exceptions.NoSuchElementException as exception:
        logger.error(exception.msg)
        # Messaging.sendErrorNotification(
        #     subject="!!Ticket Checker Error!!", messageBody=f"Couldn't find element:\n\n{exception.msg}"
        # )
        return str(exception), 404
    except Exceptions.TimeoutException as exception:
        logger.error(exception.msg)
        # Messaging.sendErrorNotification(
        #     subject="!!Ticket Checker Error!!", messageBody=f"Timeout:\n\n{exception.msg}"
        # )
        return str(exception), 504
    except Exceptions.NoSuchFrameException as exception:
        logger.error(exception.msg)
        # Messaging.sendErrorNotification(
        #     subject="!!Ticket Checker Error!!", messageBody=f"Frame not found:\n\n{exception.msg}"
        # )
        return str(exception), 404
    except Exception as exception: #pylint: disable=broad-exception-caught
        logger.error(exception)
        # Messaging.sendErrorNotification(
        #     subject="!!Ticket Checker Error!!", messageBody=f"Shit's broke:\n\n{exception}"
        # )
        return str(exception), 500
    finally:
        # send ping to uptime monitor
        # if not app.debug:
        #     requests.get("https://hc-ping.com/6805f3aa-c998-4df3-a571-1b487bd89c00", timeout=10)
        logger.info("Closing browser")
        driver.quit()
        logger.success("Browser Closed")