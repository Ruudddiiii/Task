import json
import base64
import requests
from requests.auth import HTTPBasicAuth
import PySimpleGUI as sg
import pyttsx3
from datetime import datetime
import socket
import numpy as np
import sounddevice as sd

def play_beep(frequency=50000, duration=0.2, volume=0.3):
    # Generate a beep tone
    samplerate = 44100
    t = np.linspace(0, duration, int(samplerate * duration), endpoint=False)
    waveform = volume * np.sin(2 * np.pi * frequency * t)
    sd.play(waveform, samplerate)
    sd.wait()  # Wait for the sound to finish



def is_internet_available():
    """Check if the internet is available by trying to resolve a host."""
    try:
        # Try to resolve the hostname to test connectivity
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except OSError:
        return False

tts_engine = pyttsx3.init()

# GitHub settings
GITHUB_USERNAME = 'Ruudddiiii'
REPO_NAME = 'TaskTravelTime'
GITHUB_TOKEN = 'ghp_ESTOmJTSEeGkKgJ8BaoieosqnqRAq81H2Lo'
TASK_FILE = 'task1.json'

# Add your new theme colors and settings
my_new_theme = {'BACKGROUND': '#005E60',
                'TEXT': '#FFFFFF',
                'INPUT': '#212121',
                'TEXT_INPUT': '#FFFFFF',
                'SCROLL': '#005E60',
                'BUTTON': ('white', '#696969'),
                'PROGRESS': ('#696969', '#696969'),
                'BORDER': 1,
                'SLIDER_DEPTH': 0,
                'PROGRESS_DEPTH': 0}

sg.theme_add_new('MyNewTheme', my_new_theme)
sg.theme('MyNewTheme')

# GitHub API URLs
RAW_FILE_URL = f'https://raw.githubusercontent.com/{GITHUB_USERNAME}/{REPO_NAME}/main/{TASK_FILE}'
REPO_API_URL = f'https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}/contents/{TASK_FILE}'

# Function to load tasks from GitHub
def load_tasks_from_github():
    try:
        response = requests.get(REPO_API_URL, auth=HTTPBasicAuth(GITHUB_USERNAME, GITHUB_TOKEN))
        response.raise_for_status()
        file_data = response.json()
        file_content_base64 = file_data['content']
        file_content = base64.b64decode(file_content_base64).decode('utf-8')
        data = json.loads(file_content)
        return data.get('tasks', [])
    except Exception as e:
        sg.popup_error(f"Error loading tasks from GitHub: {e}")
        return []

# Function to update and push tasks.json to GitHub
def save_tasks_to_github(tasks):

        response = requests.get(REPO_API_URL, auth=HTTPBasicAuth(GITHUB_USERNAME, GITHUB_TOKEN))
        response.raise_for_status()
        file_data = response.json()
        sha = file_data['sha']

        json_data = json.dumps({"tasks": tasks}).encode('utf-8')
        base64_content = base64.b64encode(json_data).decode('utf-8')

        payload = {
            "message": "Update tasks.json",
            "content": base64_content,
            "sha": sha
        }

        response = requests.put(REPO_API_URL, json=payload, auth=HTTPBasicAuth(GITHUB_USERNAME, GITHUB_TOKEN))
        response.raise_for_status()


# Function to update the task list in the window
def update_task_list(window, tasks):
    window["-TASKS-"].update([
        f"{'[x]' if task['completed'] else '[ ]'} {task['name']}" for task in tasks
    ])

# Define layouts for different sections
def main_tasks_layout():
    return [
        [sg.Listbox(values=[], size=(50, 15), key="-TASKS-", enable_events=True, font=("Helvetica", 16))],
        [sg.Input(key="-NEW_TASK-", size=(50, 15), font=("Helvetica", 16))],
        [sg.Button("Add Task", bind_return_key=True, font=("Helvetica", 16)), sg.Button("Mark Completed", font=("Helvetica", 16)), sg.Button("Delete Task", font=("Helvetica", 16))]
    ]

def reminders_layout():
    return [

    ]

def travel_layout():
    return [

    ]

def time_layout():
    return [
        # [sg.Listbox(values=["52","25","43","17"], key="-MINUTES-", enable_events=True, font=("Helvetica", 16))],
        [sg.Combo(["52","25","43","17","1"], default_value='25',size=(10, 1), key="-MINUTES-", enable_events=True, font=("Helvetica", 16))],
        # [sg.Text("Enter minutes:", font=("Helvetica", 14)), sg.InputText(size=(5, 1), key="-MINUTES-", font=("Helvetica", 14))],
        [sg.Text("Time Left:", font=("Helvetica", 14)), sg.Text("00:00", key="-TIMER-", font=("Helvetica", 14))],
        [sg.Button("Start", font=("Helvetica", 14))]

    ]


# Main application
def main():
    # if is_internet_available() == True:
    tasks = load_tasks_from_github()        
    
    layout = [
        [sg.Button("Tasks", font=("Helvetica", 15)),sg.Button("Time", font=("Helvetica", 15)), sg.Button("Reminders", font=("Helvetica", 15)), sg.Button("Travel", font=("Helvetica", 15))],
        [sg.Column(main_tasks_layout(), key="-TASK_PAGE-", visible=False),
        sg.Column(reminders_layout(), key="-REMINDERS_PAGE-", visible=False),
        sg.Column(travel_layout(), key="-TRAVEL_PAGE-", visible=False),
        sg.Column(time_layout(), key="-TIME_PAGE-", visible=True)]
    ]

    window = sg.Window("Tasks", layout, finalize=True)
    update_task_list(window, tasks)
    
    
    timer_running = False
    time_left = 0

    while True:
        event, values = window.read(timeout=100)  # Refresh every 100ms

        # Handle page navigation
        if event == "Reminders":
            window["-TASK_PAGE-"].update(visible=False)
            window["-REMINDERS_PAGE-"].update(visible=True)
            window["-TRAVEL_PAGE-"].update(visible=False)
            window["-TIME_PAGE-"].update(visible=False)
        elif event == "Travel":
            window["-TASK_PAGE-"].update(visible=False)
            window["-TRAVEL_PAGE-"].update(visible=True)
            window["-REMINDERS_PAGE-"].update(visible=False)
            window["-TIME_PAGE-"].update(visible=False)
        elif event == "Tasks":
            window["-TASK_PAGE-"].update(visible=True)
            window["-TRAVEL_PAGE-"].update(visible=False)
            window["-REMINDERS_PAGE-"].update(visible=False)
            window["-TIME_PAGE-"].update(visible=False)
        elif event == "Time":
            window["-TASK_PAGE-"].update(visible=False)
            window["-TRAVEL_PAGE-"].update(visible=False)
            window["-REMINDERS_PAGE-"].update(visible=False)
            window["-TIME_PAGE-"].update(visible=True)

        # Timer functionality
        if event == "Start" and window["-TIME_PAGE-"].visible:
            try:
                # Convert input minutes to seconds
                time_left = int(values["-MINUTES-"]) * 60
                timer_running = True
            except ValueError:
                sg.popup_error("Please enter a valid number of minutes.")

        if timer_running and window["-TIME_PAGE-"].visible:
            if time_left > 0:
                time_left -= 0.1  # Decrement timer in fractions of a second
                mins, secs = divmod(int(time_left), 60)
                window["-TIMER-"].update(f"{mins:02d}:{secs:02d}")
            else:
                timer_running = False
                window["-TIMER-"].update("Time's up!")
                play_beep()
                sg.popup("Time's up!")  # Optional notification

        # Handle task operations
        if event in ("Add Task", "-NEW_TASK-" + "\r"):
            new_task_name = values["-NEW_TASK-"].strip()
            if new_task_name:
                tasks.append({"name": new_task_name, "completed": False})
                update_task_list(window, tasks)
                window["-NEW_TASK-"].update("")
        elif event == "Mark Completed":
            selected = values["-TASKS-"]
            if selected:
                task_name = selected[0][4:]  # Remove prefix like [x] or [ ]
                for task in tasks:
                    if task["name"] == task_name:
                        task["completed"] = not task["completed"]
                        break
                update_task_list(window, tasks)
        elif event == "Delete Task":
            selected = values["-TASKS-"]
            if selected:
                task_name = selected[0][4:]
                tasks = [task for task in tasks if task["name"] != task_name]
                update_task_list(window, tasks)

        # Check for window close event
        if event == sg.WINDOW_CLOSED:
            # if is_internet_available():
            #     tasks = load_tasks_from_github()   
            save_tasks_to_github(tasks)
            break


    window.close()

if __name__ == "__main__":
    main()







