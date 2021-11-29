from time import sleep
import json
from threading import Thread

## fully formatted messages, e.g.
## {
##  "date" : "2021-11-20 12:01:04",
##  "content" : "fully *formatted* text"
## }
msg = {"messages": []}


def init():
    global msg
    msg = {
        "messages": [
            {
                "date" : "2021-11-20 12:01:04",
                "content" : "fully *formatted* text"
            },
            {
                "date" : "2021-11-21 12:01:04",
                "content" : "fully *formatted* text 2"
            }
        ]
    } ## debug

    ## TODO
    ## read from youtube channel and convert to msg format