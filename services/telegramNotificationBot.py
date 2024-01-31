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
        data    = callback.json['data']
        requestersChatId = self.callbackHandler.getChatIdFromData(data)
        requestersName   = self.callbackHandler.getNameFromData(data)
        answer    = self.callbackHandler.getValueFromData(data)
        chatId    = str(callback.json['from']['id'])
        messageId = callback.json['message']['message_id']
        # lastKeyboard = callback.json['message']['reply_markup']
        
        self.telegramBot.answer_callback_query(queryId)

        if chatId != adminChatId:
            # should NEVER be True - but, just in case
            print(f'NOT ALLOWED: {chatId} wanted to confirm a request from  {requestersName}')
            self.telegramBot.send_message(adminChatId, f'error 11\n{chatId}\n{requestersName}')
        else:
            print(f'callback: {queryId} = {answer}')
            adminButtonConfirm = self.appConfig['adminButtonConfirm']
            adminButtonDecline = self.appConfig['adminButtonDecline']
            adminButtonYes = self.appConfig['adminButtonYes']
            adminButtonBack = self.appConfig['adminButtonBack']
            firstMenu = self.callbackHandler.createFirstMenu(requestersChatId, adminButtonConfirm, adminButtonDecline, requestersName)
            nextMenu = self.callbackHandler.createNextMenu(requestersChatId, adminButtonYes, adminButtonBack, requestersName, answer)
            if nextMenu is None:
                # should never be True
                self.telegramBot.edit_message_text('error 42', adminChatId, messageId, reply_markup = '')
            elif self.callbackHandler.isRequestCanceled(answer):
                adminRequestMessage = self.getFormattedConfigMessage('adminRequestMessage', requestersName)
                self.telegramBot.edit_message_text(adminRequestMessage, adminChatId, messageId, reply_markup=json.dumps(firstMenu))
            elif self.callbackHandler.isRequestAccepted(answer):
                adminConfirmedMessage = self.getFormattedConfigMessage('adminConfirmedMessage', requestersName)
                self.telegramBot.edit_message_text(adminConfirmedMessage, adminChatId, messageId, reply_markup = '')
                self.confirmRequest(requestersChatId, requestersName)
            elif self.callbackHandler.isRequestDeclined(answer):
                adminDeclinedMessage = self.getFormattedConfigMessage('adminDeclinedMessage', requestersName)
                self.telegramBot.edit_message_text(adminDeclinedMessage, adminChatId, messageId, reply_markup = '')
                self.declineRequest(requestersChatId)
            else:
                adminDoubleCheckMessage = self.getFormattedConfigMessage('adminDoubleCheckMessage', requestersName)
                self.telegramBot.edit_message_text(adminDoubleCheckMessage, adminChatId, messageId, reply_markup=json.dumps(nextMenu))
    

    def onStart(self, msg):
        curChatId = msg.from_user.id
        requestersName = msg.from_user.first_name
        if not self.subManager.alreadyKnown(curChatId):
            requestMessage = self.getFormattedConfigMessage('requestMessage', requestersName)
            adminRequestMessage = self.getFormattedConfigMessage('adminRequestMessage', requestersName)
            self.telegramBot.send_message(curChatId, requestMessage) 
            adminChatId = self.appConfig['adminChatId']
            firstMenu = self.callbackHandler.createFirstMenu(curChatId, 'Bestätigen', 'Ablehnen', requestersName)
            self.telegramBot.send_message(adminChatId, adminRequestMessage, reply_markup = json.dumps(firstMenu))
        else:
            requestMessage = self.getFormattedConfigMessage('alreadySubribedMessage', requestersName)
            self.telegramBot.send_message(curChatId, requestMessage)

    def onStop(self, msg):
        curChatId = msg.from_user.id
        if self.subManager.alreadyKnown(curChatId) and self.subManager.removeSubscriber(curChatId):
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
                    ## TODO: count failures in the row -> extend chat.ids structure
                    ## if more then 7 days remove chatId
        self.subManager.saveChatIdsToFile()


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
    def getFormattedConfigMessage(self, configMessageId, requestersName):
        generalAdminMessage = self.appConfig[configMessageId]
        if requestersName != '':
            return generalAdminMessage.replace('#_firstname_#', '' + requestersName)
        else:
            return generalAdminMessage.replace('#_firstname_#', '')
        

    def confirmRequest(self, requestersChatId, requestersName = '?'):
        print(f'request {requestersChatId} confirmed')
        if self.subManager.addSubscriber(requestersChatId):
            self.telegramBot.send_message(requestersChatId, self.appConfig['startMessage']) 
            self.sendNewMessages(requestersChatId, None)
    

    def declineRequest(self, requestersChatId):
        print(f'request {requestersChatId} declined')
        self.telegramBot.send_message(requestersChatId, self.appConfig['declineMessage']) 


    ##
    # start
    def run(self):
        self.loadInfoMessage()
        self.subManager.loadChatIdsFromFile()
        self.initTelegramBot()
        self.initSendingNewMessages()
