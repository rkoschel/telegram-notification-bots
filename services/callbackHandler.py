

class CallbackHandler:
    

    def __init__(self):
        pass


    def getFirstMenu(self, chatId):
        return self.createTrueFalseButtonKeyboard(chatId, "Ja", "Nein")


    def createTrueFalseButtonKeyboard(self, chatId, trueButtonLabel, falseButtonLabel, skip=False):
        buttonTrue = self.createCallbackButton(trueButtonLabel, chatId, True)
        buttonFalse = self.createCallbackButton(falseButtonLabel, chatId, False)
        keyBoard = {}
        if skip:
            keyBoard["inline_keyboard"] = [[buttonTrue, buttonFalse]]
        else:
            keyBoard["inline_keyboard"] = [[buttonFalse, buttonTrue]]
        return keyBoard
    

    def createCallbackButton(self, label, chatId, returnValue):
        button = {}
        button["text"] = str(label)
        button["callback_data"] = str(chatId) + "-" + str(returnValue)
        return button