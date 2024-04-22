
from PickleballCourtBooker import app
from email.message import EmailMessage
import smtplib
import Config

def sendEmail(messageBody: str):
    """Send an email

    Args:
        subject (str): Subject line of the email
        messageBody (str): Message body of the email
        emails (list): List of email addresses to send the email to
    """
    if app.debug:
        return
    smtpHost = "smtp.gmail.com"
    mailserver = smtplib.SMTP_SSL(smtpHost, port=465)
    mailserver.connect(smtpHost, port=465)
    mailserver.login(Config.email_username, Config.email_password)
    message = EmailMessage()
    message["From"] = Config.email_username
    message["To"] = [Config.text_email]
    message.set_content(messageBody)
    mailserver.send_message(message)
    mailserver.quit()