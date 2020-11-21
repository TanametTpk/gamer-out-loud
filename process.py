import json
import keyboard
import pyautogui
import sys
import time
from controller import makeAction

isShouldEnd = False
isMouseDown = False
filePath = ""
config = {}
isRegister = False
_boardcast = -1
rateLimit = 10
limitCount = -1
isCanEnd = False
setEndProgram = -1

pyautogui.FAILSAFE = False

def registerBoardcast(callback):
    global isRegister
    global _boardcast
    isRegister = True
    _boardcast = callback

def boardcast(event, message):
    if isRegister:
        _boardcast(event, message)

def registerEndProgram(callback):
    global isCanEnd
    global setEndProgram
    isCanEnd = True
    setEndProgram = callback

def parseToTableFormat(voice_reg_command):
    result = []
    for command in voice_reg_command:
        newFormat = {
            "key": command["key"],
            "name": command["name"],
            "word": ",".join(command["when"]),
            "action": command["do"] + "-" + command["action"]
        }
        result.append(newFormat)

    return result

def parseToConfigFormat(tableFormats):
    result = []
    for tableFormat in tableFormats:
        action = tableFormat["action"].split("-")
        configFormat = {
            "key": tableFormat["key"],
            "name": tableFormat["name"],
            "when": tableFormat["word"].split(","),
            "do": action[0],
            "action": action[1]
        }
        result.append(configFormat)

    return result

def saveConfig(newConfig):
    global filePath
    try:
        f = open(filePath, 'w', encoding='utf-8')
        config = json.dumps(newConfig, indent=4)
        f.write(config)
        f.close()
    except:
        print("can't write config", sys.exc_info()[0])
    else:
        f.close()

def received_data(data):
    global isShouldEnd
    global isCanEnd
    global setEndProgram
    if data["event"] == "control":
        splitedCommand = data["msg"].split("-")

        if len(splitedCommand) < 2:
            return

        command = splitedCommand[0]
        keys = splitedCommand[1]
        makeAction(command, keys)

    elif data["event"] == "add-command":
        payload = data["msg"].split(",")

        if len(payload) < 4:
            return

        tableFormat = {
            "key": payload[0],
            "name": payload[1],
            "word": payload[2],
            "action": payload[3]
        }

        new_commands = parseToConfigFormat([tableFormat])[0]
        config["voice_reg"].append(new_commands)
        saveConfig(config)

    elif data["event"] == 'remove-command':
        commandKey = data["msg"]
        voice_regs = config["voice_reg"]

        for i in range(len(voice_regs)):
            voice_reg = voice_regs[i]
            if voice_reg["key"] == commandKey:
                voice_regs.pop(i)
                break

        config["voice_reg"] = voice_regs
        saveConfig(config)

    elif data["event"] == 'request-commands':
        payload = parseToTableFormat(config["voice_reg"])
        boardcast("received-commands", json.dumps(payload))
    elif data["event"] == 'kill-process':
        isShouldEnd = True
        if isCanEnd:
            setEndProgram()

def loadConfig(file):
    global config
    global filePath
    filePath = file
    try:
        f = open(file, 'r', encoding='utf-8')
        raw_config = f.read()
        config = json.loads(raw_config)
        f.close()
    except:
        print("can't load config, maybe file not found or wrong json format", sys.exc_info()[0])
    else:
        f.close()

def reloadConfig():
    loadConfig(filePath)

def process(data):
    global isShoudEnd
    commands = config["voice_reg"]
    for command in commands:
        isMatch = False
        words = command["when"]

        for word in words:
            if word in data.lower():
                isMatch = True
                break

        if isMatch:
            do = command["do"]
            action = command["action"]

            if do == "end":
                print("end")
                return True
            elif do == "reload":
                print("reload")
                reloadConfig()
            else:
                makeAction(do, action)

    return isShouldEnd

def volProcess(vol):
    global isMouseDown
    global limitCount

    limitCount = (limitCount + 1) % rateLimit
    if limitCount == 0:
        boardcast("received-vol", str(vol))

    if 200 > vol > 100 and keyboard.is_pressed('space'):
        makeAction("double-press", "space")
        return

    if vol > 350:
        makeAction("press", "q")
        print("vol", vol)
    if vol > 100:
        if not isMouseDown:
            pyautogui.mouseDown()
            isMouseDown = True
            print("down")
    else:
        if isMouseDown:
            pyautogui.mouseUp()
            isMouseDown = False
            print("up")