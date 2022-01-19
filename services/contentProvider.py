from time import sleep
from threading import Thread
import datetime as d
import json
import re
import feedparser

class ContentProvider:

    ## fully formatted messages, e.g.
    ## {
    ##  "date" : "2021-11-20 12:01:04",
    ##  "content" : "fully *formatted* text"
    ## }
    msg = {"messages": []}

    WAIT_UNTIL_LOADING_CONTENT_IN_MIN = 90 ## default; change with app.config: "rssIntervalMinutes"
    MESSAGES_FILE_NAME = "messages.json"


    def __init__(self, appConfig):
        self.rssURL = appConfig['rssURL']
        self.WAIT_UNTIL_LOADING_CONTENT_IN_MIN = int(appConfig["rssIntervalMinutes"])
        self.loadMessages()
        runRSSThread = Thread(target=self.loadMessagesInTheLoop, args=( ))
        runRSSThread.start()


    def loadMessagesInTheLoop(self):
        while True:
            try:
                self.loadMessages()
                print(f"wating for {self.WAIT_UNTIL_LOADING_CONTENT_IN_MIN} minutes ...")
                sleep(60 * self.WAIT_UNTIL_LOADING_CONTENT_IN_MIN)
            except:
                print("failed to load content this time")


    def loadMessages(self):
        newMsg = {"messages": []}
        NewsFeed = feedparser.parse(self.rssURL)
        entry = NewsFeed.entries[0]
        ## print(entry) ## debug
        bibleText = "INFO: Dieser Dienst wird aus organisatorischen Gründen einige Zeit nicht zur Verfügung stehen.\nWeitere Infos: https://t.me/bibelbots" ##original:# self.formatMessage(entry["summary"])
        published = self.getFormattedPublishedDate(str(entry["published_parsed"]))
        newMessage = {
            "date" : f"{published}",
            "content" : f"{bibleText}"
        }
        newMsg["messages"].append(newMessage)
        self.msg = newMsg
        self.persistMessages()


    def formatMessage(self, message):
        formattedMessage = message
        msgParts = message.split(" (<a ")
        if len(msgParts) == 2:
            formattedMessage = "<b>" + msgParts[0] + "</b> (<a " + msgParts[1]
        return formattedMessage


    def persistMessages(self):
        try:
            messageFile = open(self.MESSAGES_FILE_NAME, 'w')
            messageFile.write(json.dumps(self.msg))
            messageFile.close
        except:
            print(f"error saving message file: {self.MESSAGES_FILE_NAME}")


    def getFormattedPublishedDate(self, dateString):
        date = self.getPublishDate(dateString)
        return str(date["year"]) + "-" + str(date["month"]) + "-" + str(date["day"]) + " " + str(date["hour"]) + ":" + str(date["min"]) + ":" + str(date["sec"])


    def getPublishDate(self, dateString):
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
