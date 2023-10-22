from logging import INFO, NullHandler
from threading import Thread
import datetime as d
import json, time

from config.constants import MSG_DATE_FORMAT

class TelegramNotificationBot:

    MSG_SENDER_DELAY_SECONDS = 60 * 5 ## 5 minutes
    INFO_MESSAGE_FILE_NAME = "message.info"
    infoMessage = ""

    def __init__(self, appConfig, telegramBot, content, subMan, callHandl):
        self.appConfig       = appConfig
        self.telegramBot     = telegramBot
        self.content         = content
        self.subManager      = subMan
        self.callbackHandler = callHandl

    ###
    # events
    def handleCallback(self, callback):
        adminChatId = self.appConfig['adminChatId']
        queryId = callback.json['id']
        answerRequestersId = callback.json['data'].split('-')[0]
        answerAccepted = callback.json['data'].split('-')[1]
        chatId = str(callback.json['from']['id'])
        messageId = callback.json['message']['message_id']
        lastKeyboard = callback.json['message']['reply_markup']
        self.telegramBot.answer_callback_query(queryId)
        if chatId != adminChatId:
            print(f'NOT ALLOWED: {chatId} wanted to confirm a request: {answerRequestersId}')
            self.telegramBot.send_message(chatId, f"das darfst du nicht!")
        else:
            print(f'callback: {queryId} = {answerAccepted}')
            keyBoard2 = self.callbackHandler.createTrueFalseButtonKeyboard(adminChatId, "bestätigen", "zurück", True)
            ## TODO die Logik funktioniert so nicht!! 
            ## ich muss mir die auswahl vom keyboard 1 merken
            if lastKeyboard != keyBoard2:
                # first click - ask again
                self.telegramBot.edit_message_reply_markup(chatId, messageId, reply_markup=json.dumps(keyBoard2))
            elif lastKeyboard == keyBoard2 and answerAccepted.lower() == 'false':
                # second click - but not accepted - go back
                keyBoard2 = self.callbackHandler.createTrueFalseButtonKeyboard(chatId, "Ja", "Nein")
                self.telegramBot.edit_message_reply_markup(chatId, messageId, reply_markup = json.dumps(keyBoard2))
            elif lastKeyboard == keyBoard2 and answerAccepted.lower() == 'true':
                # second click - and finally accepted
                self.telegramBot.edit_message_reply_markup(chatId, messageId, reply_markup = '')
                self.telegramBot.send_message(chatId, f"du hast auf die Anfrage akzeptiert")
                self.confirmRequest(answerRequestersId)
            else:
                # second click - and denied
                self.telegramBot.edit_message_reply_markup(chatId, messageId, reply_markup = '')
                self.telegramBot.send_message(chatId, f"du hast auf die Anfrage abgelehnt")
    

    def onStart(self, msg):
        curChatId = msg.from_user.id
        requestersName = msg.from_user.first_name
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
        firstMenu = self.callbackHandler.getFirstMenu(curChatId)
        self.telegramBot.send_message(adminChatId, individualAdminMessage, reply_markup = json.dumps(firstMenu))


    def onStop(self, msg):
        curChatId = msg.from_user.id
        if self.subManager.removeSubscriber(curChatId):
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
    # send messages
    def sendNewMessages(self, chatId, latestMessageDT):
        for message in self.content.msg["messages"]:
            msgPublishDT = d.datetime.strptime(message["date"], MSG_DATE_FORMAT)
            msgContent = message["content"]
            if latestMessageDT == None or msgPublishDT > latestMessageDT:
                try:
                    self.telegramBot.send_message(chatId, msgContent, disable_web_page_preview=True)
                    self.subManager.updateLatestMessage(chatId, msgPublishDT)
                except:
                    print(f"sending message to {chatId} failed")
                    ## TODO: count failures in the row
                    ## if more then 7 days remove chatId
        self.saveChatIdsToFile()

    def sendToAllWhoWant(self):
        while True:
            try:
                for chat in self.subManager.getAllSubscriberArray():
                    curChatId = chat["id"]
                    nowDT = d.datetime.now()
                    todayDateStr = nowDT.strftime("%Y-%m-%d")
                    lastMessageDT = d.datetime.strptime(chat["lastMessageDateTime"], MSG_DATE_FORMAT)
                    sendMessageDT = None
                    try:
                        sendMessageDT = d.datetime.strptime(todayDateStr + " " + chat["sendMessageTime"], MSG_DATE_FORMAT)
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
    def confirmRequest(self, requestersChatId):
        if self.subManager.addSubscriber(requestersChatId):
            self.telegramBot.send_message(requestersChatId, self.appConfig['startMessage']) 
            self.sendNewMessages(requestersChatId, None)
        
    
    

    ##
    # start
    def run(self):
        self.loadInfoMessage()
        self.subManager.loadChatIdsFromFile()
        self.initTelegramBot()
        self.initSendingNewMessages()
