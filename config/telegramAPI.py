import telebot

from telebot import apihelper
from config.appConfig import appConfig

from services.contentProvider import ContentProvider
from services.TNBClass import TelegramNotificationBot

apihelper.SESSION_TIME_TO_LIVE = 5 * 60
telegramAPI = telebot.TeleBot(appConfig["telegramBotId"], parse_mode="HTML")

content = ContentProvider(appConfig)
notificationBot = TelegramNotificationBot(appConfig, telegramAPI, content)

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