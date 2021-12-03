import services.contentProvider as content
import services.botservice as bs
import telebot
import json
from telebot import apihelper

CONFIG_FILE_NAME    = "app.config"
configFile      = open(CONFIG_FILE_NAME, "r")
appConfig       = json.loads(configFile.read()) 
configFile.close

content.init(appConfig)

apihelper.SESSION_TIME_TO_LIVE = 5 * 60
telegramAPI = telebot.TeleBot(appConfig["telegramBotId"], parse_mode="HTML")

notificationBot = bs.TelegramNotificationBot(appConfig, telegramAPI, content)

@telegramAPI.message_handler(commands=["start"])
def botHandleStart(msg):
    notificationBot.onStart(msg)

@telegramAPI.message_handler(commands=["stop"])
def botHandleStop(msg):
    notificationBot.onStop(msg)

@telegramAPI.message_handler(commands=["info"])
def botHandleInfo(msg):
    notificationBot.onInfo(msg)

@telegramAPI.message_handler(commands=["bible"])
def botHandleBible(msg):
    notificationBot.onBible(msg)

@telegramAPI.message_handler(commands=["comments"])
def handleComments(msg):
    notificationBot.onComments(msg)