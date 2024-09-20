import PySimpleGUI as sg
import json
import requests
from requests.auth import HTTPBasicAuth
import base64

# GitHub settings
GITHUB_USERNAME = 'Ruudddiiii'
REPO_NAME = 'TaskTravelTime'
GITHUB_TOKEN = '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'
TASK_FILE = 'tasks.json'

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
    except requests.exceptions.RequestException as e:
        print(f"Error loading tasks from GitHub: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from GitHub response: {e}")
        return []

# Function to update and push tasks.json to GitHub
def save_tasks_to_github(tasks):
    try:
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
        print("Tasks successfully updated on GitHub")
    except requests.exceptions.RequestException as e:
        print(f"Error saving tasks to GitHub: {e}")

# Load tasks from GitHub
tasks = load_tasks_from_github()

# Define the layout of the GUI
layout = [
    [sg.Text('Task List')],
    [sg.Listbox(values=[task['name'] for task in tasks], size=(60, 20), key='-TASK_LIST-')],
    [sg.InputText(key='-NEW_TASK-', size=(60, 1))],
    [sg.Button('Add Task' ,bind_return_key=True), sg.Button('Delete Task'), sg.Button('Save Changes')],

]

# Create the window
window = sg.Window('Task Manager', layout)

# Event loop for GUI interaction
while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED :
        save_tasks_to_github(tasks)  # Trigger save before closing
        break

    # Check if Enter key was pressed in the input field
    if event == '-NEW_TASK-' and values['-NEW_TASK-'] != '':
        new_task = values['-NEW_TASK-'].strip()
        tasks.append({"name": new_task, "completed": False})
        window['-TASK_LIST-'].update([task['name'] for task in tasks])
        window['-NEW_TASK-'].update('')  # Clear the input field

    # Handle clicking the 'Add Task' button
    if event == 'Add Task':
        new_task = values['-NEW_TASK-'].strip()
        if new_task:
            tasks.append({"name": new_task, "completed": False})
            window['-TASK_LIST-'].update([task['name'] for task in tasks])
            window['-NEW_TASK-'].update('')  # Clear the input after adding the task

    # Handle 'Delete Task' button
    if event == 'Delete Task':
        selected_task = values['-TASK_LIST-']
        if selected_task:
            selected_task_name = selected_task[0]
            tasks = [task for task in tasks if task['name'] != selected_task_name]
            window['-TASK_LIST-'].update([task['name'] for task in tasks])

    # Save changes to GitHub
    if event == 'Save Changes':
        save_tasks_to_github(tasks)

# Close the window
window.close()
