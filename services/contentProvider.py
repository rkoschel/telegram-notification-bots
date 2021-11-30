from time import sleep
import json
from threading import Thread

## fully formatted messages, e.g.
## {
##  "date" : "2021-11-20 12:01:04",
##  "content" : "fully *formatted* text"
## }
msg = {"messages": []}


def load():
    global msg
    msg = {
        "messages": [
            {
                "date" : "2021-11-20 12:01:04",
                "content" : "provide fully *formatted* text"
            },
            {
                "date" : "2021-11-21 12:01:04",
                "content" : "with this _json_ structure"
            }
        ]
    } ## debug

    ## TODO
    ## read from youtube channel and convert to msg format