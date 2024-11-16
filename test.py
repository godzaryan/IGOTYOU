import pyautogui
import time
import win32gui
import pygetwindow as gw
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
import ctypes
import screen_brightness_control as sbc

def win_tab_and_next_window():
    # Open Task View
    pyautogui.keyDown("win")
    pyautogui.press("tab")
    pyautogui.keyUp("win")
    time.sleep(0.3)
    pyautogui.press("right")
    time.sleep(0.3)
    pyautogui.press("enter")


def win_tab_and_previous_window():
    # Open Task View
    pyautogui.keyDown("win")
    pyautogui.press("tab")
    pyautogui.keyUp("win")
    time.sleep(0.3)
    pyautogui.press("left")
    time.sleep(0.3)
    pyautogui.press("enter")


def type_text_in_foreground_window(text):
    hwnd = win32gui.GetForegroundWindow()

    if hwnd:
        time.sleep(0.2)

        pyautogui.write(text)
        #print(f"Typed '{text}' in the foreground window successfully.")
    #else:
        #print("No active foreground window found.")

def minimize_active_window():
    win = gw.getActiveWindow()
    if win:
        win.minimize()
    else:
        print("No active window found.")

def maximize_active_window():
    win = gw.getActiveWindow()
    if win:
        win.maximize()
    else:
        print("No active window found.")

def close_active_window():
    win = gw.getActiveWindow()
    if win:
        win.close()
    else:
        print("No active window found.")

user32 = ctypes.windll.user32
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = ctypes.cast(interface, ctypes.POINTER(IAudioEndpointVolume))

def get_current_volume():
    return volume.GetMasterVolumeLevelScalar()

def set_system_volume(x):
    x = max(0.0, min(1.0, x))
    volume.SetMasterVolumeLevelScalar(x, None)

def increase_volume_by(x):
    set_system_volume(min(1.0, get_current_volume() + x))

def decrease_volume_by(x):
    set_system_volume(max(0.0, get_current_volume() - x))

def increase_brightness(x):
    sbc.set_brightness(sbc.get_brightness()[0] + x)

def decrease_brightness(x):
    sbc.set_brightness(sbc.get_brightness()[0] - x)

def set_brightness(level):
    sbc.set_brightness(level)

#type_text_in_foreground_window("Hello, World!")
set_brightness(100)
#win_tab_and_next_window()
