import services.contentProvider as content
from services.tBotConfig import notificationBot
from services.appConfig import appConfig

if __name__ == '__main__':
    content.init(appConfig)
    notificationBot.start()

    
    
