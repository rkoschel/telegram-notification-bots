from time import sleep
import json
from threading import Thread
import feedparser


## fully formatted messages, e.g.
## {
##  "date" : "2021-11-20 12:01:04",
##  "content" : "fully *formatted* text"
## }
msg = {"messages": []}

loopDelayInMinutes = 1
MESSAGES_FILE_NAME = "messages.json"

def load(appConfig):
    rssURL = appConfig['rssURL']
    loadMessages(rssURL)
    runRSSThread = Thread(target=loadMessagesInTheLoop, args=(rssURL, ))
    runRSSThread.start()

def loadMessagesInTheLoop(rssURL):
    while True:
        try:
            print(f"wating for {loopDelayInMinutes} minutes ...")
            sleep(60 * loopDelayInMinutes)
            loadMessages(rssURL)
        except:
            print("failed to load content this time")

def loadMessages(rssURL):
    global msg
    newMsg = {"messages": []}
    NewsFeed = feedparser.parse(rssURL)
    entry = NewsFeed.entries[1]
    bibleText = entry["summary"]
    published = entry["published_parsed"]
    newMessage = {
        "date" : f"{published}",
        "content" : f"{bibleText}"
    }
    newMsg["messages"].append(newMessage)
    msg = newMsg
    persistMessages()


def persistMessages():
    chatIdFile = open(MESSAGES_FILE_NAME, 'w')
    chatIdFile.write(json.dumps(msg))
    chatIdFile.close
