import json

from config.constants import MSG_DATE_FORMAT


class SubscriptionManager:

    CHAT_IDS_FILE_NAME  = "chat.ids"
    allChat             = {"ids" : []}

    def __init__(self, config):
        self.appConfig = config


    def addSubscriber(self, chatId):
        if not self.alreadyKnown(chatId):
            self.allChat["ids"].append({"id" : chatId})
            print(f"added {chatId}") ## debug
            return self.saveChatIdsToFile()
        else:
            return False


    def removeSubscriber(self, chatId):
        newChats = {"ids" : []}
        for chat in self.allChat["ids"]:
            if str(chat["id"]) != str(chatId) and chat["id"] != '':
                newChats["ids"].append(chat)
        self.allChat = newChats
        return self.saveChatIdsToFile()
    

    def getAllSubscriberArray(self):
        return self.allChat['ids']


    def alreadyKnown(self, chatId):
        for chat in self.allChat['ids']:
            if str(chat["id"]) == str(chatId):
                return True
        return False


    def updateLatestMessage(self, chatId, latestMessageDT):
        for chat in self.allChat['ids']:
            if str(chat["id"]) == str(chatId):
                chat["lastMessageDateTime"] = latestMessageDT.strftime(MSG_DATE_FORMAT)


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
            return True
        except:
            print("could'nt write chats to file")
            return False