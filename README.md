# ✨ IGOTYOU: Your Intuitive AI Voice and Gesture Assistant ✨

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg?style=for-the-badge&logo=python)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![GitHub Stars](https://img.shields.io/github/stars/godzaryan/IGOTYOU?style=for-the-badge&color=gold)](https://github.com/godzaryan/IGOTYOU/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/godzaryan/IGOTYOU?style=for-the-badge&color=silver)](https://github.com/godzaryan/IGOTYOU/network/members)

---

## 🚀 Overview

**IGOTYOU** is an innovative and highly intuitive AI-powered voice and gesture assistant designed to streamline your daily computer interactions. It combines natural language processing with advanced gesture recognition to provide a seamless and hands-free control experience. Whether you're a busy professional, a creative, or simply looking for a more efficient way to manage your digital life, IGOTYOU is here to enhance your productivity and simplify complex tasks.

"IGOTYOU" is developed by **Team Anonymous**, consisting of:
* **Tanisha Seal**: Software Developer and QA Tester
* **Akash Kumar**: Project Manager and Software Developer
* **Bithika Purkait**: UI/UX Designer and Marketing Professional

---

## 🌟 Features

* 🗣️ **Voice Command & Control**: Interact with your system using natural voice commands.
    * Open and close applications.
    * Manage active windows (minimize, maximize, close).
    * Switch between open windows effortlessly.
    * Control system volume and screen brightness.
* ✍️ **Voice Typing**: Dictate text directly into any foreground application.
    * Activate and deactivate voice typing with simple commands.
    * Utilizes a dedicated "Delete" key shortcut for quick deactivation.
* 👋 **Gesture Control**: Leverage hand gestures for intuitive navigation.
    * **Swipe Right/Left**: Switch between application windows (Alt+Tab functionality).
    * **Index Finger Pointer**: Enable precise mouse cursor control using your index finger.
    * **Open Hand Gesture**: Exit cursor control mode easily.
* 🔊 **Real-time Audio Visualizer**: A dynamic and visually appealing circular audio visualizer that responds to desktop audio, featuring an integrated GIF loop for an enhanced user experience.
* 💬 **Smart AI Responses**: Powered by Google's Gemini-1.5-Flash model, providing concise and relevant answers to your queries.
* ✨ **Elegant Notifications**: Non-intrusive, transient popup notifications for user feedback and status updates.

---

## 🛠️ Requirements

### Operating System
* Windows (due to dependencies like `pygetwindow`, `win32gui`, `pycaw`, `screen_brightness_control`, `win32com.client`, `psutil`)

### Python Version
* Python 3.8 or higher is recommended.

### Dependencies
You can install all required Python packages using `pip`:

```bash
pip install -r requirements.txt
````

Or install them individually:

```bash
pip install pyttsx3 speechRecognition PyAudio fuzzywuzzy python-Levenshtein pygetwindow pycaw comtypes screen_brightness_control opencv-python mediapipe pyautogui pyqt6 psutil google-generativeai pynput Pillow
```

**Note:** Some dependencies like `PyAudio` might require additional system-level libraries (e.g., PortAudio for `PyAudio`). Please refer to their respective documentation for detailed installation instructions if you encounter issues.

### Hardware

  * **Microphone**: For voice commands and voice typing.
  * **Webcam**: For gesture control.

-----

## 🚀 Getting Started

### 1\. Clone the Repository

```bash
git clone [https://github.com/YOUR_USERNAME/IGOTYOU.git](https://github.com/YOUR_USERNAME/IGOTYOU.git)
cd IGOTYOU
```

### 2\. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3\. Google Gemini API Key Setup

**Important**: The `main.py` file contains a placeholder for the Google Gemini API key:
`genai.configure(api_key="YOUR_API_KEY")`

You **must** replace `"YOUR_API_KEY"` with your actual Google Gemini API key. You can obtain one from the [Google AI Studio](https://aistudio.google.com/app/apikey).

### 4\. GIF for Audio Visualizer (Optional)

The `QtAudioVisualizer.py` file expects a GIF file named `your_gif.gif` in the same directory.
`gif_path = 'your_gif.gif'`
You can replace `'your_gif.gif'` with the path to your desired GIF file, or provide one in the project's root directory.

### 5\. Run the Application

```bash
python main.py
```

-----

## 💡 Usage

Once the application is running, a small, non-intrusive notification will appear at the bottom of your screen, indicating that the voice assistant is listening.

### Voice Commands:

Simply speak your commands. Here are some examples:

  * "Open Chrome"
  * "Start Notepad"
  * "Close active window"
  * "Kill Spotify"
  * "Switch to next window"
  * "Switch to previous window"
  * "Minimize window"
  * "Maximize window"
  * "Increase volume by 0.1"
  * "Decrease brightness by 10"
  * "Set brightness to 50"
  * "Enable voice typing"
  * "Disable voice typing"
  * "What is the capital of France?" (for AI query)

### Voice Typing:

1.  Say "Enable voice typing".
2.  Start speaking. Your speech will be typed into the currently active window.
3.  To stop voice typing, press the `Delete` key on your keyboard or say "Disable voice typing".

### Gesture Control:

Ensure your webcam is active and visible.

  * **Switch Windows:**
      * **Swipe Right:** Move your hand from left to right in front of the camera (simulates `Alt + Tab`).
      * **Swipe Left:** Move your hand from right to left in front of the camera (simulates `Alt + Shift + Tab`).
  * **Cursor Control:**
      * **Index Finger Pointing:** Point your index finger forward. The mouse cursor will follow your finger's movement.
      * **Open Hand Gesture:** Open your palm widely to exit cursor control mode.

-----

## 📁 Project Structure

```
IGOTYOU/
├── main.py                     # Main application entry point, voice assistant logic, and popup notifications
├── Functions.py                # Collection of helper functions for system control (volume, brightness, window management)
├── objectDetection.py          # Implements gesture control using MediaPipe for hand tracking
└── QtAudioVisualizer.py        # Real-time desktop audio visualizer with GIF integration using Pygame
├── README.md                   # This file
└── requirements.txt            # List of Python dependencies
├── run.bat                     # An automated script to run the program
```

-----

## 🤝 Contributing

We welcome contributions\! If you have suggestions for improvements, new features, or bug fixes, please follow these steps:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature-name`).
3.  Make your changes.
4.  Commit your changes (`git commit -m 'feat: Add new awesome feature'`).
5.  Push to the branch (`git push origin feature/your-feature-name`).
6.  Open a Pull Request.

-----

## 🙏 Acknowledgements

  * [Google Gemini API](https://ai.google.dev/) for powerful AI capabilities.
  * [PyQt6](https://www.riverbankcomputing.com/software/pyqt/intro) for GUI development.
  * [SpeechRecognition](https://pypi.org/project/SpeechRecognition/) for speech-to-text.
  * [pyttsx3](https://pypi.org/project/pyttsx3/) for text-to-speech.
  * [MediaPipe](https://www.google.com/search?q=https://google.github.io/mediapipe/) for robust hand tracking.
  * [pyautogui](https://pyautogui.readthedocs.io/en/latest/) for GUI automation.
  * [pygetwindow](https://pygetwindow.readthedocs.io/en/latest/) for window management.
  * [pycaw](https://github.com/AndreMiras/pycaw) for audio control.
  * [screen\_brightness\_control](https://pypi.org/project/screen-brightness-control/) for brightness control.
  * [fuzzywuzzy](https://pypi.org/project/fuzzywuzzy/) for fuzzy string matching.
  * [psutil](https://psutil.readthedocs.io/en/latest/) for process management.
  * [Pygame](https://www.pygame.org/) for the audio visualizer.
  * [Pillow](https://www.google.com/search?q=https://python-pillow.org/) for GIF handling.

-----

Made with ❤️ by Team Anonymous
