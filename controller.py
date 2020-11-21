import pyautogui
import pydirectinput
import keyboard

def makeAction(action, key):
    if action == "press":
        pyautogui.press(key)
    if action == "double-press":
        pyautogui.press(key)
        pyautogui.press(key)
    if action == "say":
        print(key)