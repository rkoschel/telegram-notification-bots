from time import sleep
from threading import Thread
import datetime as d
import json
import re
import feedparser


## fully formatted messages, e.g.
## {
##  "date" : "2021-11-20 12:01:04",
##  "content" : "fully *formatted* text"
## }
msg = {"messages": []}

WAIT_UNTIL_LOADING_CONTENT_IN_MIN = 1
MESSAGES_FILE_NAME = "messages.json"

def init(appConfig):
    rssURL = appConfig['rssURL']
    loadMessages(rssURL)
    runRSSThread = Thread(target=loadMessagesInTheLoop, args=(rssURL, ))
    runRSSThread.start()

def loadMessagesInTheLoop(rssURL):
    while True:
        try:
            print(f"wating for {WAIT_UNTIL_LOADING_CONTENT_IN_MIN} minutes ...")
            sleep(60 * WAIT_UNTIL_LOADING_CONTENT_IN_MIN)
            loadMessages(rssURL)
        except:
            print("failed to load content this time")

def loadMessages(rssURL):
    global msg
    newMsg = {"messages": []}
    NewsFeed = feedparser.parse(rssURL)
    entry = NewsFeed.entries[0]
    ## print(entry) ## debug
    bibleText = entry["summary"]
    published = getFormattedPublishedDate(str(entry["published_parsed"]))
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

def getFormattedPublishedDate(dateString):
    date = getPublishDate(dateString)
    return str(date["year"]) + "-" + str(date["month"]) + "-" + str(date["day"]) + " " + str(date["hour"]) + ":" + str(date["min"]) + ":" + str(date["sec"])

def getPublishDate(dateString):
    ## print(dateString) ## debug
    year = list(map(int, re.findall("tm_year=(\d+)", dateString)))
    month = list(map(int, re.findall("tm_mon=(\d+),", dateString)))
    day = list(map(int, re.findall("tm_mday=(\d+)", dateString)))
    hour = list(map(int, re.findall("tm_hour=(\d+)", dateString)))
    min = list(map(int, re.findall("tm_min=(\d+)", dateString)))
    sec = list(map(int, re.findall("tm_sec=(\d+)", dateString)))
    return {"year" : year[0],
            "month" : month[0],
            "day" : day[0],
            "hour" : hour[0],
            "min" : min[0],
            "sec" : sec[0]}
