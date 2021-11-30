import services.contentProvider as content
from logging import INFO, NullHandler
import telebot
import json
from threading import Thread
import datetime


CONFIG_FILE_NAME    = 'app.config'
CHAT_IDS_FILE_NAME  = 'chat.ids'
INFO_MESSAGE_FILE_NAME = 'message.info'

allChat     = {"ids" : []}
appConfig   = { }
infoMessage = ''

## static config
## is required to make telegram annotations work
configFile = open(CONFIG_FILE_NAME, 'r')
appConfig = json.loads(configFile.read()) ##
configFile.close

telegramBot = telebot.TeleBot(appConfig['telegramBotId'], parse_mode='HTML')

@telegramBot.message_handler(commands=['start'])
def handleStart(msg):
    curChatId = msg.from_user.id
    if not alreadyKnown(curChatId):
        allChat["ids"].append({"id" : curChatId})
        print(f'added {curChatId}')
        saveChatIdsToFile(allChat)
    telegramBot.send_message(curChatId, appConfig['startMessage']) 
    sendMessages(curChatId)

@telegramBot.message_handler(commands=['stop'])
def handleStop(msg):
    global allChat
    curChatId = msg.from_user.id;
    newChats = {"ids" : []}
    for chat in allChat["ids"]:
        if chat["id"] != curChatId and chat["id"] != '':
            newChats["ids"].append(chat)
    allChat = newChats
    saveChatIdsToFile(allChat)
    print(f'deleted {curChatId}')
    telegramBot.send_message(curChatId, appConfig['stopMessage']);

@telegramBot.message_handler(commands=['info'])
def handleInfo(msg):
    curChatId = msg.from_user.id
    telegramBot.send_message(curChatId, infoMessage)

#@telegramBot.message_handler(commands=['bible'])
#def handleBible(msg):
#    let curChatId = msg.from.id;
#    bot.sendMessage(curChatId, appConfig.bibleMessage);

#@telegramBot.message_handler(commands=['comments'])
#def handleComments(msg):
#    let curChatId = msg.from.id
#    bot.sendMessage(curChatId, appConfig.commentsMessage)


###
# init functions
###
def initTelegramBot():
    global telegramBot
    ## TODO make this more stable
    ## - check if the connection is still alive
    ## - re-connect if required
    runTelegramThread = Thread(target=telegramBot.infinity_polling)
    runTelegramThread.start()

def loadInfoMessage():
    global infoMessage
    infoMessageFile = open(INFO_MESSAGE_FILE_NAME, 'r')
    infoMessage = infoMessageFile.read()
    infoMessageFile.close


###
# manage chat ids
###
def loadChatIdsFromFile():
    global allChat
    try:
       chatIdFile = open(CHAT_IDS_FILE_NAME, 'r')
       allChat = json.loads(chatIdFile.read())
       chatIdFile.close
    except:
        print('no valid chat.ids file')

def saveChatIdsToFile(chatIds):
    chatIdFile = open(CHAT_IDS_FILE_NAME, 'w')
    chatIdFile.write(json.dumps(chatIds))
    chatIdFile.close


### 
# send messages
###
def sendMessages(chatId):
    for message in content.msg["messages"]:
        telegramBot.send_message(chatId, message["content"], disable_web_page_preview=True)

def sendToAllWhoWant():
    pass
    ## TODO check which message should be send to whom
    for chat in allChat['ids']:
        ## if chat["time"] == ...
        pass 


###
# misc
###
def alreadyKnown(chatId):
    wasNew = False
    for chat in allChat['ids']:
        if chat['id'] == chatId:
            return True
    return False

##
# start
##
def start():
    content.load(appConfig)
    loadInfoMessage()
    loadChatIdsFromFile()
    initTelegramBot()

    print(allChat) ## debug
