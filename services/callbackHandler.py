

class CallbackHandler:
    
    SEP = '~'

    def __init__(self):
        pass


    def createFirstMenu(self, chatId, yes, no, name):
        return self.createTrueFalseButtonKeyboard(chatId, yes, no, name)

    
    def createNextMenu(self, chatId, confirm, back, name, oldValue):
        return self.createTrueFalseButtonKeyboard(chatId, confirm, back, name, oldValue, True)


    def generateCallbackValue(self, chatId, name, value):
        return str(chatId) + self.SEP + str(name) + self.SEP + str(value)


    def isRequestAccepted(self, answer):
        return answer == 'yy' 
    

    def isRequestDeclined(self, answer):
        return answer == 'ny' 
    

    def isRequestCanceled(self, answer):
        return answer == 'yn' or answer == 'nn'
    

    def getChatIdFromData(self, data):
        return data.split(self.SEP)[0]


    def getNameFromData(self, data):
        return data.split(self.SEP)[1]


    def getValueFromData(self, data):
        return data.split(self.SEP)[2]


    def createTrueFalseButtonKeyboard(self, chatId, trueButtonLabel, falseButtonLabel, name, oldValue='', flip=False):
        calbackValueTrue = self.generateCallbackValue(chatId, name, oldValue + 'y')
        calbackValueFalse = self.generateCallbackValue(chatId, name, oldValue + 'n')
        buttonTrue = self.createCallbackButton(trueButtonLabel, calbackValueTrue)
        buttonFalse = self.createCallbackButton(falseButtonLabel, calbackValueFalse)
        keyBoard = {}
        if flip:
            keyBoard["inline_keyboard"] = [[buttonTrue, buttonFalse]]
        else:
            keyBoard["inline_keyboard"] = [[buttonFalse, buttonTrue]]
        return keyBoard
    

    def createCallbackButton(self, label, value):
        button = {}
        button["text"] = str(label)
        button["callback_data"] = str(value)
        return button