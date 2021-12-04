import json

# import os
# rootFolder = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

appConfig = None
CONFIG_FILE_NAME    = "app.config"
try:
    configFile      = open(CONFIG_FILE_NAME, "r")
    appConfig       = json.loads(configFile.read()) 
    configFile.close
except:
    print("could'nt load " + CONFIG_FILE_NAME)