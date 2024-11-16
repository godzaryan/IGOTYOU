import sys
import threading
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
import winreg
import win32com.client
import psutil

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
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.app_instance = app_instance  # To call popup update from here
        self.setup_recognizer()
        self.failed_attempts = 0
        self.last_calibration_time = time.time()

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
            program_name = str(command).removeprefix("close ").removeprefix("kill ")
            self.close_matching_process(program_name)

        elif "how are you" in command:
            self.speak("I am just a program, but thanks for asking!")
            Popup("I am just a program, but thanks for asking!", 5000)
        elif "what is your name" in command:
            self.speak("I am called Dan, your voice assistant.")
            Popup("I am called Dan, your voice assistant.", 5000)
        elif "goodbye" in command:
            self.speak("Goodbye! Have a great day!")

    def run_program(self, program_name):
        self.app_instance.show_notification(f"Starting {program_name}...")
        shortcuts = self.get_start_menu_shortcuts()
        best_match, score = process.extractOne(program_name.lower(), shortcuts.keys()) if shortcuts else (None, 0)
        if score > 70 and best_match:
            subprocess.Popen(shortcuts[best_match], shell=True)  # Open the program in the background
        else:
            self.app_instance.show_notification(f"No suitable program found for '{program_name}'")

    def close_matching_process(self, process_name):
        self.app_instance.show_notification(f"Closing process {process_name}...")
        processes = {p.info["name"].lower(): p for p in psutil.process_iter(["name", "pid"])}
        best_match, score = process.extractOne(process_name.lower(), processes.keys()) if processes else (None, 0)
        if score > 70 and best_match:
            processes[best_match].terminate()

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
