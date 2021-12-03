from services.botHandler import notificationBot
#from threading import Thread
#from flask import Flask, request, jsonify

#PORT = 5001
#app = Flask(__name__)


if __name__ == '__main__':
    #app.config['JSON_AS_ASCII'] = False
    # runFlaskThread = Thread(target=app.run, args=('0.0.0.0', PORT, False))
    # runFlaskThread.start()
    notificationBot.start()

    
    
