from logging import INFO, NullHandler
from threading import Thread
import datetime as d
import json, time

class TelegramNotificationBot:

    def __init__(self, appConfig, telegramBot, content):
        self.appConfig      = appConfig
        self.telegramBot    = telegramBot
        self.content        = content

    MSG_SENDER_DELAY_SECONDS = 60 * 15 ## 15 minutes
    MSG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    CHAT_IDS_FILE_NAME  = "chat.ids"
    INFO_MESSAGE_FILE_NAME = "message.info"
    allChat     = {"ids" : []}
    infoMessage = ""
    
    ###
    # events
    def onStart(self, msg):
        curChatId = msg.from_user.id
        if not self.alreadyKnown(curChatId):
            self.allChat["ids"].append({"id" : curChatId})
            ## print(f"added {curChatId}") ## debug
            self.saveChatIdsToFile()
        self.telegramBot.send_message(curChatId, self.appConfig['startMessage']) 
        self.sendNewMessages(curChatId, None)

    def onStop(self, msg):
        curChatId = msg.from_user.id;
        newChats = {"ids" : []}
        for chat in self.allChat["ids"]:
            if chat["id"] != curChatId and chat["id"] != '':
                newChats["ids"].append(chat)
        self.allChat = newChats
        self.saveChatIdsToFile()
        ## print(f"deleted {curChatId}") ## debug
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
        runTelegramThread = Thread(target=self.telegramBot.infinity_polling)
        runTelegramThread.start()

    def initSendingNewMessages(self):
        runNewMsgsThread = Thread(target=self.sendToAllWhoWant)
        runNewMsgsThread.start()

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
            print("no valid chat.ids file")

    def saveChatIdsToFile(self):
        try: 
            chatIdFile = open(self.CHAT_IDS_FILE_NAME, 'w')
            chatIdFile.write(json.dumps(self.allChat))
            chatIdFile.close
        except:
            print("could'nt write chats to file")

    ### 
    # send messages
    def sendNewMessages(self, chatId, latestMessageDT):
        for message in self.content.msg["messages"]:
            msgPublishDT = d.datetime.strptime(message["date"], self.MSG_DATE_FORMAT)
            msgContent = message["content"]
            if latestMessageDT == None or msgPublishDT > latestMessageDT:
                self.telegramBot.send_message(chatId, msgContent, disable_web_page_preview=True)
                self.updateLatestMessage(chatId, msgPublishDT)
        self.saveChatIdsToFile()

    def sendToAllWhoWant(self):
        while True:
            try:
                for chat in self.allChat['ids']:
                    curChatId = chat["id"]
                    nowDT = d.datetime.now()
                    todayDateStr = nowDT.strftime("%Y-%m-%d")
                    lastMessageDT = d.datetime.strptime(chat["lastMessageDateTime"], self.MSG_DATE_FORMAT)
                    sendMessageDT = None
                    try:
                        sendMessageDT = d.datetime.strptime(todayDateStr + " " + chat["sendMessageTime"], self.MSG_DATE_FORMAT)
                    except:
                        print("no sendMessageTime defined for " + str(curChatId))
                    if sendMessageDT == None or nowDT > sendMessageDT:
                        self.sendNewMessages(curChatId, lastMessageDT)
            except:
                print("error during sending new messages")
            print("waiting for " + str(self.MSG_SENDER_DELAY_SECONDS) + " before checking to send new messages again")
            time.sleep(self.MSG_SENDER_DELAY_SECONDS)

    ###
    # misc
    def updateLatestMessage(self, chatId, latestMessageDT):
        for chat in self.allChat['ids']:
            if chat["id"] == chatId:
                chat["lastMessageDateTime"] = latestMessageDT.strftime(self.MSG_DATE_FORMAT)

    def alreadyKnown(self, chatId):
        wasNew = False
        for chat in self.allChat['ids']:
            if chat["id"] == chatId:
                return True
        return False

    ##
    # start
    def start(self):
        self.loadInfoMessage()
        self.loadChatIdsFromFile()
        self.initTelegramBot()
        self.initSendingNewMessages()
