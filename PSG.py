import json
import base64
import requests
from requests.auth import HTTPBasicAuth
import PySimpleGUI as sg
# from datetime import datetime

# GitHub settings
GITHUB_USERNAME = 'Ruudddiiii'
REPO_NAME = 'TaskTravelTime'
GITHUB_TOKEN = 'ghp_ESTOmJTSEeGkKgJ8BaoieosqnqRAq81H2Lo'
TASK_FILE = 'task1.json'

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
        sg.popup("Tasks successfully updated on GitHub")
    except Exception as e:
        sg.popup_error(f"Error saving tasks to GitHub: {e}")

# Function to update the task list in the window
def update_task_list(window, tasks):
    window["-TASKS-"].update([
        f"{'[x]' if task['completed'] else '[ ]'} {task['name']}" for task in tasks
    ])

# Main application
def main():
    tasks = load_tasks_from_github()

    layout = [
        [sg.Text("Task Manager", font=("Helvetica", 16))],
        [sg.Listbox(
            values=[], size=(40, 15), key="-TASKS-", enable_events=True
        )],
        [sg.Input(key="-NEW_TASK-")],
        [sg.Button("Add Task"), sg.Button("Mark Completed"), sg.Button("Delete Task"), sg.Button("Sync Tasks")],
    ]

    window = sg.Window("Task Manager", layout, finalize=True)
    update_task_list(window, tasks)


    # update_task_list(window, tasks)

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break

        if event == "Add Task":
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

        elif event == "Sync Tasks":
            save_tasks_to_github(tasks)

    window.close()

if __name__ == "__main__":
    main()
