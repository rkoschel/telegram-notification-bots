from time import sleep
import datetime as d
from threading import Thread, Lock
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

    MSG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
    WAIT_UNTIL_LOADING_CONTENT_IN_MIN = 90 ## default; change with app.config: "rssIntervalMinutes"
    MESSAGES_FILE_NAME = "messages.json"

    lock = Lock()

    def __init__(self, appConfig):
        self.appConfig = appConfig
        self.ytChannels = appConfig["ytChannels"]
        ##self.rssURL = appConfig["rssURL"]
        self.WAIT_UNTIL_LOADING_CONTENT_IN_MIN = int(appConfig["rssIntervalMinutes"])
        self.loadMessages()
        runRSSThread = Thread(target=self.loadMessagesInTheLoop, args=( ))
        runRSSThread.start()


    def loadMessagesInTheLoop(self):
        while True:
            print(f"wating for {self.WAIT_UNTIL_LOADING_CONTENT_IN_MIN} minutes ...")
            sleep(60 * self.WAIT_UNTIL_LOADING_CONTENT_IN_MIN)
            try:
                self.loadMessages()
            except:
                print("failed to load content this time")


    def loadMessagesFromOneYTChannel(self, ytRssChannelURL):
        print(f"load messages from {ytRssChannelURL}") ## debug
        newMsg = {"messages": []}
        NewsFeed = feedparser.parse(ytRssChannelURL)
        #print(f"{NewsFeed}") ## debug
        for entry in reversed(NewsFeed.entries):
            #print(entry) ## debug
            messageText = self.formatMessage(entry)
            print(messageText) ## debug
            published = self.getFormattedPublishedDate(str(entry["published_parsed"]))
            newMessage = {
                "date" : f"{published}",
                "content" : f"{messageText}"
            }
            newMsg["messages"].append(newMessage)
        return newMsg


    def loadMessages(self):
        for rssURL in self.ytChannels:
            try:
                newMsgs = self.loadMessagesFromOneYTChannel(rssURL)
                addedMsgs = self.msg["messages"] + newMsgs["messages"]
                print(f"#1# add to self.msg[]: {addedMsgs}")
                self.msg["messages"] = addedMsgs
            except:
                print(f"not possible to load messsages from {rssURL}")
            sleep(1)
        #logMessage = self.msg["messages"]
        #print(f"all messages: {logMessage}")
        self.msg["messages"].sort(key=self.sortMessagesFunction)
        self.persistMessages()


    def sortMessagesFunction(self, msg):
        try:
            return d.datetime.strptime(msg["date"], self.MSG_DATE_FORMAT)
        except:
            return d.datetime.now()


    def formatMessage(self, rssEntry):
        title = rssEntry["title"]
        link = rssEntry["link"]
        author = rssEntry["authors"][0]["name"]
        formattedMessage = "<b>" + author + "</b>\n\n" + title + "\n\n" + link + "\n"
        return formattedMessage


    def persistMessages(self):
        self.lock.acquire()
        try:
            messageFile = open(self.MESSAGES_FILE_NAME, 'w')
            messageFile.write(json.dumps(self.msg))
            messageFile.close
        except:
            print(f"error saving message file: {self.MESSAGES_FILE_NAME}")
        self.lock.release()

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
