from logging import INFO, NullHandler
from threading import Thread
import datetime as d
import json

class TelegramNotificationBot:

    def __init__(self, appConfig, telegramBot, content):
        self.appConfig      = appConfig
        self.telegramBot    = telegramBot
        self.content        = content

    CHAT_IDS_FILE_NAME  = 'chat.ids'
    INFO_MESSAGE_FILE_NAME = 'message.info'
    allChat     = {"ids" : []}
    infoMessage = ''
    
    ###
    # events
    def onStart(self, msg):
        curChatId = msg.from_user.id
        if not self.alreadyKnown(curChatId):
            self.allChat["ids"].append({"id" : curChatId})
            print(f'added {curChatId}')
            self.saveChatIdsToFile(self.allChat)
        self.telegramBot.send_message(curChatId, self.appConfig['startMessage']) 
        self.sendLatestNotifications(curChatId)

    def onStop(self, msg):
        curChatId = msg.from_user.id;
        newChats = {"ids" : []}
        for chat in self.allChat["ids"]:
            if chat["id"] != curChatId and chat["id"] != '':
                newChats["ids"].append(chat)
        self.allChat = newChats
        self.saveChatIdsToFile(self.allChat)
        print(f'deleted {curChatId}')
        self.telegramBot.send_message(curChatId, self.appConfig['stopMessage']);

    def onInfo(self, msg):
        curChatId = msg.from_user.id
        self.telegramBot.send_message(curChatId, self.infoMessage)

    def onBible(self, msg):
        curChatId = msg.from_user.id
        self.telegramBot.send_message(curChatId, self.appConfig["bibleMessage"])

    def onComments(self, msg):
        curChatId = msg.from_user.id
        self.telegramBot.send_message(curChatId, self.appConfig["commentsMessage"])


    ###
    # init functions
    def initTelegramBot(self):
        ## TODO make this more stable
        ## - check if the connection is still alive
        ## - re-connect if required
        runTelegramThread = Thread(target=self.telegramBot.infinity_polling)
        runTelegramThread.start()

    def loadInfoMessage(self):
        infoMessageFile = open(self.INFO_MESSAGE_FILE_NAME, 'r')
        self.infoMessage = infoMessageFile.read()
        infoMessageFile.close


    ###
    # manage chat ids
    def loadChatIdsFromFile(self):
        try:
            chatIdFile = open(self.CHAT_IDS_FILE_NAME, 'r')
            self.allChat = json.loads(chatIdFile.read())
            chatIdFile.close
        except:
            print('no valid chat.ids file')

    def saveChatIdsToFile(self, chatIds):
        chatIdFile = open(self.CHAT_IDS_FILE_NAME, 'w')
        chatIdFile.write(json.dumps(chatIds))
        chatIdFile.close


    ### 
    # send messages
    def sendLatestNotifications(self, chatId):
        for message in self.content.msg["messages"]:
            msgDate = d.datetime.strptime(message["date"], "%Y-%m-%d %H:%M:%S")
            msgContent = message["content"]
            #nowDate = d.datetime.now()
            self.telegramBot.send_message(chatId, msgContent, disable_web_page_preview=True)

    ## call this method in a loop / thread
    def sendToAllWhoWant(self, msgDate, msgContent):
        for chat in self.allChat['ids']:
            curChatId = chat["id"]
            #lastMessageDate = chat["lastMessageDate"]
            # sendMessageDate = chat["sendMessageDate"]
            ## TODO: if msgDate > lastMessageDate: sendMessage + setLasMessage
            self.sendLatestNotifications(curChatId)
 


    ###
    # misc
    def alreadyKnown(self, chatId):
        wasNew = False
        for chat in self.allChat['ids']:
            if chat['id'] == chatId:
                return True
        return False

    ##
    # start
    def start(self):
        self.loadInfoMessage()
        self.loadChatIdsFromFile()
        self.initTelegramBot()

        print(self.allChat) ## debug
