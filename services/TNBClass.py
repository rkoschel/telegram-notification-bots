from logging import INFO, NullHandler
from threading import Thread
import datetime as d
import json, time

class TelegramNotificationBot:

    def __init__(self, appConfig, telegramBot, content):
        self.appConfig      = appConfig
        self.telegramBot    = telegramBot
        self.content        = content

    MSG_SENDER_DELAY_SECONDS = 60 * 5 ## 5 minutes
    MSG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    CHAT_IDS_FILE_NAME  = "chat.ids"
    REQUESTED_IDS_FILE_NAME  = "requested.ids"
    INFO_MESSAGE_FILE_NAME = "message.info"
    allChat          = {"ids" : []}
    requestedChatIds = {"ids" : []}
    infoMessage = ""
    
    ###
    # events
    def handleCallback(self, callback):
        adminChatId = self.appConfig['adminChatId']
        queryId = callback.json['id']
        answerRequestersId = callback.json['data'].split('-')[0]
        answerAccepted = callback.json['data'].split('-')[1]
        chatId = str(callback.json['from']['id'])
        messageId = callback.json['message']['message_id']
        self.telegramBot.answer_callback_query(queryId)
        ## TODO: instead of removing the buttons, replace them with "I'm sure.", "whops, back"
        self.telegramBot.edit_message_reply_markup(chatId, messageId, reply_markup="")
        # TODO: check if answerRequesterId is in self.requestedChatIds
        ## what does it mean??
        if chatId != adminChatId:
            print(f'NOT ALLOWED: {chatId} wanted to confirm a request: {answerRequestersId}')
            self.telegramBot.send_message(chatId, f"das darfst du nicht!")
        else:
            print(f'callback: {queryId} = {answerAccepted}')
            self.telegramBot.send_message(chatId, f"du hast auf die Anfrage mit {answerAccepted} reagiert.")
            if answerAccepted.lower() == 'true':
                # TODO send confirmation to subscriber
                self.confirmRequest(answerRequestersId)
        
    
    def onStart(self, msg):
        curChatId = msg.from_user.id
        requestersName = msg.from_user.first_name
        if not self.alreadyRequested(curChatId):
            self.requestedChatIds["ids"].append({"id" : curChatId})
            ## print(f"added {curChatId}") ## debug
            self.saveRequestedChatIdsToFile()
        generalRequestMessage = self.appConfig['requestMessage']
        if requestersName != '':
            individualRequestMessage = generalRequestMessage.replace('#_firstname_#', ' ' + requestersName)
        else:
            individualRequestMessage = generalRequestMessage.replace('#_firstname_#', '')
        generalAdminMessage = self.appConfig['adminMessage']
        if requestersName != '':
            individualAdminMessage = generalAdminMessage.replace('#_firstname_#', ' ' + requestersName)
        else:
            individualAdminMessage = generalAdminMessage.replace('#_firstname_#', '')
        self.telegramBot.send_message(curChatId, individualRequestMessage) 
        adminChatId = self.appConfig['adminChatId']
        buttonYes = self.createCallbackButton("YES", curChatId, True)
        buttonNo = self.createCallbackButton("NO", curChatId, False)
        keyBoard = {}
        keyBoard["inline_keyboard"] = [[buttonYes, buttonNo]]
        self.telegramBot.send_message(adminChatId, individualAdminMessage, reply_markup = json.dumps(keyBoard))

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

    def onBibleHelp(self, msg):
        curChatId = msg.from_user.id
        self.telegramBot.send_message(curChatId, self.appConfig["bibleHelpMessage"])


    ###
    # init functions
    def initTelegramBot(self):
        runTelegramThread = Thread(target=self.telegramBot.infinity_polling)
        runTelegramThread.start()

    def initSendingNewMessages(self):
        runNewMsgsThread = Thread(target=self.sendToAllWhoWant)
        runNewMsgsThread.start()

    def loadInfoMessage(self):
        try:
            infoMessageFile = open(self.INFO_MESSAGE_FILE_NAME, 'r')
            self.infoMessage = infoMessageFile.read()
            infoMessageFile.close
        except:
            print("couldn't load message file")
            self.infoMessage = "Info"

    ###
    # manage chat ids
    def loadChatIdsFromFile(self):
        try:
            chatIdFile = open(self.CHAT_IDS_FILE_NAME, 'r')
            self.allChat = json.loads(chatIdFile.read())
            chatIdFile.close
        except:
            print("no valid chat.ids file")

    def loadRequestedIdsFromFile(self):
        try:
            requestIdFile = open(self.REQUESTED_IDS_FILE_NAME, 'r')
            self.requestedChatIds = json.loads(requestIdFile.read())
            requestIdFile.close
        except:
            print("no valid request.ids file")

    def saveRequestedChatIdsToFile(self):
        try: 
            chatIdFile = open(self.REQUESTED_IDS_FILE_NAME, 'w')
            chatIdFile.write(json.dumps(self.allChat))
            chatIdFile.close
        except:
            print("could'nt write chats to file")

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
                try:
                    self.telegramBot.send_message(chatId, msgContent, disable_web_page_preview=True)
                    self.updateLatestMessage(chatId, msgPublishDT)
                except:
                    print(f"sending message to {chatId} failed")
                    ## TODO: count failures in the row
                    ## if more then 10 days remove chatId
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
            print("waiting for " + str(self.MSG_SENDER_DELAY_SECONDS/60) + " min. before checking to send new messages again")
            time.sleep(self.MSG_SENDER_DELAY_SECONDS)

    ###
    # misc
    def createCallbackButton(self, label, chatId, returnValue):
        button = {}
        button["text"] = str(label)
        button["callback_data"] = str(chatId) + "-" + str(returnValue)
        return button
    
    def confirmRequest(self, requestersChatId):
        if not self.alreadyKnown(requestersChatId):
            self.allChat["ids"].append({"id" : requestersChatId})
            ## print(f"added {curChatId}") ## debug
            self.saveChatIdsToFile()
        self.telegramBot.send_message(requestersChatId, self.appConfig['startMessage']) 
        self.sendNewMessages(requestersChatId, None)
        
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
    
    def alreadyRequested(self, chatId):
        wasNew = False
        for chat in self.requestedChatIds['ids']:
            if chat["id"] == chatId:
                return True
        return False

    ##
    # start
    def start(self):
        self.loadInfoMessage()
        self.loadRequestedIdsFromFile()
        self.loadChatIdsFromFile()
        self.initTelegramBot()
        self.initSendingNewMessages()
