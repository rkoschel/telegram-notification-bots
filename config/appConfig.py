import json
import logging
from logging.handlers import RotatingFileHandler
import os
import sys

# logging configuration
logging.basicConfig(  
    level=logging.WARNING,  # Log-Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format="%(asctime)s [%(levelname)s] [%(name)s] %(message)s"
)

logger = logging.getLogger("appConfig")
if os.access("/var/log", os.W_OK):
    rotatingFileHandler = RotatingFileHandler("/var/log/telegramNotificationBot.log", maxBytes=5*1024, backupCount=7) # Log to file with rotation
    logger.addHandler(rotatingFileHandler)
    logger.info("File logging enabled.")
else:
    logger.addHandler(logging.StreamHandler(sys.stdout)) # log to console if no file access
    logger.warning("No write access to /var/log, file logging disabled.")

# app configuration
appConfig = None
CONFIG_FILE_NAME    = "app.config"

try:
    configFile = open(CONFIG_FILE_NAME, "r")
    appConfig  = json.loads(configFile.read()) 
    configFile.close()
except:
    logger.error("could'nt load " + CONFIG_FILE_NAME)