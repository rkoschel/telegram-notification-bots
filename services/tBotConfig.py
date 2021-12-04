import services.contentProvider as content
import services.botservice as bs
import telebot

from services.appConfig import appConfig
from telebot import apihelper

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