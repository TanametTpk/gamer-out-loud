import speech_recognition as sr
import sounddevice as sd
from time import ctime
import time
import os
import numpy as np
import threading
from process import process, received_data, registerBoardcast, registerEndProgram
import random

def nextSentence():
    return str(random.random())

messages = {}
orders_sentences = []
current_sentence = nextSentence()
orders_sentences.append(current_sentence)
max_sentences = 5
isEnd = False
subscriber = -1
isHaveSubscriber = False
r = sr.Recognizer()

def register(callback):
    global isHaveSubscriber
    global subscriber
    subscriber = callback
    isHaveSubscriber = True

def duplexRegister(callback, incomming_register):
    register(callback)
    registerBoardcast(boardcast)
    incomming_register(received_data)

def endProgram():
    global isEnd
    isEnd = True

registerEndProgram(endProgram)

def boardcast(event, data):
    if isHaveSubscriber:
        subscriber(event, data)

def translate(audio, id_sentence):
    global current_sentence
    global isEnd
    data = ""
    try:
        data = r.recognize_google(audio, language="th")
        boardcast("received-speech", data)
        shouldEnd = process(data)
        if shouldEnd:
            isEnd = True
            boardcast("end", "")
    except sr.UnknownValueError:
        pass
        # print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        pass
        # print("Could not request results from Google Speech Recognition service; {0}".format(e))

class translateThread (threading.Thread):
    def __init__(self, threadID, audio, sentenceID):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.audio = audio
        self.sentenceID = sentenceID
        
    def run(self):
        translate(self.audio, self.sentenceID)

def listen():
    with sr.Microphone() as source:
        count = 0
        MAXCOUNT = 100
        while not isEnd:
            audio = r.record(source, duration=1)
            thread = translateThread("m" + str(count), audio, current_sentence)
            thread.start()
            count = (count + 1) % MAXCOUNT