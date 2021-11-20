from time import sleep
import telebot
import json
from threading import Thread

telegramBot = telebot.TeleBot("2072795720:AAEAk_Mr5fES8mHS67usLMeIwShL9Gbfpo8", parse_mode='Markdown')

allChat = {
    'ids' : []
}

configFile = open('app.config', 'r')
appConfig = json.loads(configFile.read()) ##
configFile.close

@telegramBot.message_handler(commands=['start'])
def handleStart(msg):
    curChatId = msg.from_user.id
    if not alreadyKnown(curChatId):
        allChat['ids'].append({'id' : curChatId})
        print(f'added {curChatId}')
        chatIdFile = open('chat.ids', 'w')
        chatIdFile.write(str(allChat))
        chatIdFile.close
    telegramBot.send_message(curChatId, appConfig['startMessage']) 
    #telegramBot.send_message(curChatId, latestMessage) ## TODO send some of the latest videos

#@telegramBot.message_handler(commands=['stop'])
#def handleStop(msg):
#    curChatId = msg.from.id;
#    allChatIds_NEW = new Array();
#    for (let i = 0; i < allChatIds.length; i++) {
#        if(allChatIds[i] != curChatId && allChatIds[i] != '')
#            allChatIds_NEW.push(allChatIds[i]);
#    }
#    allChatIds = allChatIds_NEW;
#    fs.writeFileSync(CHATID_FILE, allChatIds.join('\n'));
#    bot.sendMessage(curChatId, appConfig.stopMessage);

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
