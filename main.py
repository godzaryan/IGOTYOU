import sys
import threading
import pyautogui
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPainter, QBrush, QColor
from PyQt6.QtWidgets import QApplication, QLabel, QWidget
import platform
import speech_recognition as sr
import pyttsx3
import asyncio
import time
import os
import subprocess
import shutil
from fuzzywuzzy import fuzz, process
import pygetwindow as gw
import win32com.client
import psutil
import google.generativeai as genai
from pynput import keyboard
import win32gui

class Popup(QWidget):
    current_popup = None  # Track the current visible popup

    def __init__(self, message: str, duration: int = 5000):
        super().__init__()

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.SplashScreen)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.label = QLabel(message, self)
        self.label.setFont(QFont("Century Gothic", 12))
        self.label.adjustSize()

        padding = 40
        self.resize(self.label.width() + padding, self.label.height() + padding)

        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = screen.height() - self.height() - 50
        self.move(x, y)

        # Close any existing popup before showing a new one
        if Popup.current_popup:
            Popup.current_popup.close()
        Popup.current_popup = self

        self.show()
        QTimer.singleShot(duration, self.close)

    def closeEvent(self, event):
        if Popup.current_popup == self:
            Popup.current_popup = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect()
        radius = 30
        painter.setBrush(QBrush(QColor(0, 0, 0, 120)))
        painter.drawRoundedRect(rect, radius, radius)

        self.label.setGeometry(20, 20, self.label.width(), self.label.height())

class VoiceAssistant:
    def __init__(self, app_instance):
        super().__init__()
        self.voice_typing_enabled = False
        self.stop_voice_typing = False  # Flag to stop voice typing
        self.keyboard_listener = None  # For listening to the 'Del' key press
        self.recognizer = sr.Recognizer()
        genai.configure(api_key="YOUR_API_KEY")
        self.model = genai.GenerativeModel("gemini-1.5-flash")
        self.engine = pyttsx3.init()
        self.app_instance = app_instance  # To call popup update from here
        self.setup_recognizer()
        self.failed_attempts = 0
        self.last_calibration_time = time.time()

    def enable_voice_typing(self):
        self.voice_typing_enabled = True
        self.stop_voice_typing = False

        # Start a thread to monitor for the 'Del' key press
        self.keyboard_listener = threading.Thread(target=self.monitor_stop_key, daemon=True)
        self.keyboard_listener.start()

        self.speak("Voice typing enabled. Start speaking.")
        while self.voice_typing_enabled and not self.stop_voice_typing:
            try:
                with sr.Microphone() as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    self.app_instance.show_notification("Listening for typing...")
                    audio = self.recognizer.listen(source, timeout=5)

                    # Recognize speech
                    typed_text = self.recognizer.recognize_google(audio, language='en-US')
                    self.type_text_in_foreground_window(typed_text)

            except sr.UnknownValueError:
                self.app_instance.show_notification("Sorry, I couldn't understand that.")
            except sr.RequestError as e:
                self.app_instance.show_notification(f"Request error: {e}")
            except Exception as e:
                self.app_instance.show_notification(f"Error during voice typing: {e}")
                self.voice_typing_enabled = False

        self.speak("Voice typing disabled.")
        self.app_instance.show_notification("Voice typing stopped.")

    def monitor_stop_key(self):
        def on_press(key):
            if key == keyboard.Key.delete:
                self.stop_voice_typing = True
                return False  # Stop listener

        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()

    def type_text_in_foreground_window(self, text):
        hwnd = win32gui.GetForegroundWindow()

        if hwnd:
            time.sleep(0.2)  # Short delay to ensure the target window is ready
            pyautogui.write(text)

    def setup_recognizer(self):
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.energy_threshold = 300
        self.recognizer.pause_threshold = 0.8
        self.recognizer.non_speaking_duration = 0.5

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def listen_and_respond(self):
        with sr.Microphone() as source:
            self.app_instance.show_notification("Voice Assistant is running and listening...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

            while True:
                try:
                    if time.time() - self.last_calibration_time > 10 or self.failed_attempts >= 3:
                        self.app_instance.show_notification("Re-calibrating for ambient noise...")
                        self.recognizer.adjust_for_ambient_noise(source, duration=1)
                        self.last_calibration_time = time.time()
                        self.failed_attempts = 0

                    self.app_instance.show_notification("Listening...")
                    audio = self.recognizer.listen(source, timeout=5)
                    command = self.recognizer.recognize_google(audio, language='en-US').lower()
                    self.app_instance.show_notification(f"You said: {command}", 5000)
                    self.respond(command)

                    self.failed_attempts = 0

                except sr.UnknownValueError:
                    self.app_instance.show_notification("Sorry, I didn't catch that.")
                    self.recognizer.adjust_for_ambient_noise(source, duration=1)
                    self.last_calibration_time = time.time()
                    self.failed_attempts += 1
                except sr.RequestError as e:
                    self.app_instance.show_notification(f"Could not request results; {e}")
                except Exception as ex:
                    self.app_instance.show_notification(f"An unexpected error occurred: {ex}")
                    self.recognizer = sr.Recognizer()
                    self.setup_recognizer()
                    time.sleep(1)

    def respond(self, command):
        if str(command).startswith("open ") or str(command).startswith("start "):
            program_name = str(command).removeprefix("open ").removeprefix("start ")
            if shutil.which(program_name):
                self.speak("Starting " + program_name)

                threading.Thread(target=self.run_program, args=(program_name,), daemon=True).start()  # Run in a background thread
            else:
                self.run_program(program_name)

        elif str(command).startswith("close ") or str(command).startswith("kill "):
            if ("active" in str(command) or "foreground" in str(command) or "current" in str(command)) and "window" in str(command):
                self.close_active_window()
            else:
                program_name = str(command).removeprefix("close ").removeprefix("kill ")
                self.close_matching_process(program_name)

        elif command.startswith("enable voice typing"):
            self.enable_voice_typing()

            
        elif command.startswith("disable voice typing"):
            self.voice_typing_enabled = False
            self.stop_voice_typing = True

        elif str(command).startswith("switch"):
            if "next" in str(command):
                self.win_tab_and_next_window()
            else:
                self.win_tab_and_previous_window()

        elif str(command).startswith("minimise"):
            if "window" in str(command):
                self.minimize_active_window()

        elif str(command).startswith("maximize"):
            if "window" in str(command):
                self.maximize_active_window()

        else:
            response = self.model.generate_content("Imagine your name is nova and you are a voice assistant based AI made by team Anonymous and your project name is \"I GOT YOU\", the members in the team are Tanisha Seal as Software developer and QA tester, Akash Kumar as Project manager and Software developer and Bithika Purkait as UI/UX designer and marketing professional. now based on all these data Answer the below question in very short and you don't need to mention who made you or your project name or anything unnecessary data without asking by user which is not required : \n" + command)
            self.speak(response.text)
            Popup(response.text, 5000)






    def minimize_active_window(self):
        win = gw.getActiveWindow()
        if win:
            win.minimize()
        else:
            print("No active window found.")

    def maximize_active_window(self):
        win = gw.getActiveWindow()
        if win:
            win.maximize()
        else:
            print("No active window found.")

    def close_active_window(self):
        win = gw.getActiveWindow()
        if win:
            win.close()
        else:
            print("No active window found.")


    def win_tab_and_next_window(self):
        # Open Task View
        pyautogui.keyDown("win")
        pyautogui.press("tab")
        pyautogui.keyUp("win")
        time.sleep(0.3)
        pyautogui.press("right")
        time.sleep(0.3)
        pyautogui.press("enter")

    def win_tab_and_previous_window(self):
        # Open Task View
        pyautogui.keyDown("win")
        pyautogui.press("tab")
        pyautogui.keyUp("win")
        time.sleep(0.3)
        pyautogui.press("left")
        time.sleep(0.3)
        pyautogui.press("enter")





    def get_start_menu_apps(self):
        try:
            command = 'powershell -Command "Get-StartApps | ForEach-Object { $_.Name + \'|\' + $_.AppID }"'
            result = subprocess.run(command, capture_output=True, text=True, shell=True)

            if result.returncode != 0:
                raise Exception("Failed to retrieve Start Menu apps.")

            apps = {}
            for line in result.stdout.strip().split('\n'):
                name, appid = line.split('|', 1)
                apps[name.lower()] = appid

            return apps
        except Exception as e:
            print(f"Error retrieving Start Menu apps: {e}")
            return {}

    def find_executable(self, program_name):
        for path in os.environ["PATH"].split(os.pathsep):
            exe_path = os.path.join(path, program_name)
            if os.path.isfile(exe_path) and os.access(exe_path, os.X_OK):
                return exe_path
        return None

    def find_start_menu_shortcut(self, program_name):
        start_menu_paths = [
            os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
            os.path.expandvars(r"%PROGRAMDATA%\Microsoft\Windows\Start Menu\Programs")
        ]

        shortcuts = []
        for path in start_menu_paths:
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith(".lnk"):
                        shortcuts.append(os.path.join(root, file))

        # Fuzzy match the shortcut names
        shortcut_names = {os.path.splitext(os.path.basename(shortcut))[0].lower(): shortcut for shortcut in shortcuts}
        best_match, score = process.extractOne(program_name.lower(), shortcut_names.keys()) if shortcut_names else (
        None, 0)

        if score > 70:
            return shortcut_names[best_match]
        return None

    def run_program(self, app_name):
        # Get the list of Start Menu apps
        apps = self.get_start_menu_apps()
        if not apps:
            print("Failed to retrieve Start Menu apps.")
            return

        # Fuzzy match to find the best match for the app name
        best_match, score = process.extractOne(app_name.lower(), apps.keys()) if apps else (None, 0)

        if score > 70 and best_match:
            app_id = apps[best_match]
            try:
                if "!" in app_id:  # UWP app detected
                    ps_command = f"Start-Process shell:AppsFolder\\{app_id}"
                    subprocess.run(["powershell", "-Command", ps_command], check=True)
                    print(f"Successfully started UWP app '{best_match}'.")
                elif os.path.exists(app_id):  # Traditional executable or shortcut
                    subprocess.Popen(app_id, shell=True)
                    print(f"Successfully started traditional app '{best_match}'.")
                else:  # Search for executable or shortcut
                    exe_name = f"{best_match}.exe"
                    exe_path = self.find_executable(exe_name)
                    if exe_path:
                        subprocess.Popen(exe_path, shell=True)
                        print(f"Successfully started '{best_match}' via executable path.")
                    else:
                        shortcut_path = self.find_start_menu_shortcut(best_match)
                        if shortcut_path:
                            # Use COM interface to resolve the .lnk file to its target
                            shell = win32com.client.Dispatch("WScript.Shell")
                            shortcut = shell.CreateShortcut(shortcut_path)
                            subprocess.Popen(shortcut.TargetPath, shell=True)
                            print(f"Successfully started '{best_match}' via Start Menu shortcut.")
                        else:
                            print(f"Executable or shortcut for '{best_match}' not found.")
            except subprocess.CalledProcessError:
                print(f"Failed to start '{best_match}'.")
            except Exception as e:
                print(f"An error occurred while starting '{best_match}': {e}")
        else:
            print(f"No suitable program found for '{app_name}'.")

    def close_matching_process(self, process_name):
        self.app_instance.show_notification(f"Closing all processes matching {process_name}...")

        # Create a dictionary of processes (name: process object)
        processes = {p.info["name"].lower(): p for p in psutil.process_iter(["name", "pid"]) if p.info["name"]}

        # Find the best matching process name
        best_match, score = process.extractOne(process_name.lower(), processes.keys()) if processes else (None, 0)

        if score > 70 and best_match:
            matched_process_name = best_match
            killed_count = 0

            # Terminate all processes matching the best match name
            for proc in psutil.process_iter(["name", "pid"]):
                try:
                    if proc.info["name"].lower() == matched_process_name:
                        proc.kill()
                        killed_count += 1
                except psutil.NoSuchProcess:
                    pass  # Process may have already exited
                except psutil.AccessDenied:
                    self.app_instance.show_notification(
                        f"Access denied for process '{proc.info['name']}' (PID {proc.pid}).")
                except Exception as e:
                    self.app_instance.show_notification(
                        f"Error terminating process '{proc.info['name']}' (PID {proc.pid}): {e}")

            self.app_instance.show_notification(f"Killed {killed_count} instance(s) of '{matched_process_name}'.")
        else:
            self.app_instance.show_notification(f"No suitable processes found for '{process_name}'.")


class IGOTYOU:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.assistant = VoiceAssistant(self)


    def show_notification(self, message: str, duration: int = 5000):
        # This will show the message in a popup
        Popup(message, duration)

    def start_voice_assistant(self):
        assistant_thread = threading.Thread(target=self.assistant.listen_and_respond, daemon=True)
        assistant_thread.start()

    def run(self):
        # Show the initial notification for the voice assistant
        #self.show_notification("🔊 Voice Assistant is Ready. Listening in background...")
        self.assistant.listen_and_respond()  # Start the voice assistant in a separate thread
        sys.exit(self.app.exec())

if __name__ == "__main__":
    app_instance = IGOTYOU()
    app_instance.run()
