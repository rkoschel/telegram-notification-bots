## telebot docu -> https://pytba.readthedocs.io/en/latest/index.html
import telebot

from telebot import apihelper
from config.appConfig import appConfig
from services.callbackHandler import CallbackHandler
from services.contentProvider import ContentProvider
from services.subscriptionManager import SubscriptionManager
from services.telegramNotificationBot import TelegramNotificationBot

apihelper.SESSION_TIME_TO_LIVE = 5 * 60
telegramAPI = telebot.TeleBot(appConfig["telegramBotId"], parse_mode="HTML")

content = ContentProvider(appConfig)
subManager = SubscriptionManager(appConfig)
callbackHandler = CallbackHandler()
notificationBot = TelegramNotificationBot(appConfig, telegramAPI, content, subManager, callbackHandler)

@telegramAPI.callback_query_handler(func=notificationBot.handleCallback, kwargs="")
def botHandlerCallback(callback):
    notificationBot.handleCallback(callback)

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

@telegramAPI.message_handler(commands=["help"])
def handleBibleHelp(msg):
    notificationBot.onBibleHelp(msg)