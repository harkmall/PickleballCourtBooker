"""
Configuration file, loading environment variables
"""
import os
from dotenv import load_dotenv, dotenv_values
from PickleballCourtBooker import app

if app.debug:
    load_dotenv()
    app.config.from_mapping(dotenv_values())
else:
    app.config.from_mapping(os.environ.items())

salix_website = app.config.get("SALIX_WEBSITE")
salix_username = app.config.get("SALIX_USERNAME")
salix_password = app.config.get("SALIX_PASSWORD")