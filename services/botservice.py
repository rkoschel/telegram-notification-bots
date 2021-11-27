from time import sleep
import telebot
import json
from threading import Thread


CONFIG_FILE_NAME = 'app.config'
CHAT_IDS_FILE_NAME = 'chat.ids'

allChat = {'ids' : []}

configFile = open(CONFIG_FILE_NAME, 'r')
appConfig = json.loads(configFile.read()) ##
configFile.close

telegramBot = telebot.TeleBot(appConfig['telegramBotId'], parse_mode='Markdown')


@telegramBot.message_handler(commands=['start'])
def handleStart(msg):
    curChatId = msg.from_user.id
    if not alreadyKnown(curChatId):
        allChat['ids'].append({'id' : curChatId})
        print(f'added {curChatId}')
        saveChatIdsToFile(allChat)
    telegramBot.send_message(curChatId, appConfig['startMessage']) 
    #telegramBot.send_message(curChatId, latestMessage) ## TODO send some of the latest videos

@telegramBot.message_handler(commands=['stop'])
def handleStop(msg):
    global allChat
    curChatId = msg.from_user.id;
    newChats = {'ids' : []}
    for chat in allChat['ids']:
        if chat['id'] != curChatId and chat['id'] != '':
            newChats['ids'].append(chat)
    allChat = newChats
    saveChatIdsToFile(allChat)
    print(f'deleted {curChatId}')
    telegramBot.send_message(curChatId, appConfig['stopMessage']);

def saveChatIdsToFile(chatIds):
    chatIdFile = open(CHAT_IDS_FILE_NAME, 'w')
    chatIdFile.write(str(chatIds))
    chatIdFile.close

#@telegramBot.message_handler(commands=['info'])
#def handleInfo(msg):
#    let curChatId = msg.from.id;
#    bot.sendMessage(curChatId, infoMessage);

#@telegramBot.message_handler(commands=['bible'])
#def handleBible(msg):
#    let curChatId = msg.from.id;
#    bot.sendMessage(curChatId, appConfig.bibleMessage);

#@telegramBot.message_handler(commands=['comments'])
#def handleComments(msg):
#    let curChatId = msg.from.id
#    bot.sendMessage(curChatId, appConfig.commentsMessage)

def alreadyKnown(chatId):
    wasNew = False
    for chat in allChat['ids']:
        if chat['id'] == chatId:
            return True
    return False

def start():
    runTelegramThread = Thread(target=telegramBot.infinity_polling)
    runTelegramThread.start()
