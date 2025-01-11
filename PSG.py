import json
import base64
import requests
import PySimpleGUI as sg

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

# Replace these values with your information
GITLAB_URL = 'https://reindeer-thorough-plainly.ngrok-free.app'
REPO_ID = 'root%2Ftask_sync'
ACCESS_TOKEN = 'glpat-cQtHoz_Rjn5kWczaGsNk'
FILE_PATH = 'task1.json'
BRANCH = 'main'
REPO_API_URL = f'{GITLAB_URL}/api/v4/projects/{REPO_ID}/repository/files/{FILE_PATH}'

# Function to load tasks from GitLab
def load_tasks_from_gitlab():
    headers = {
        'PRIVATE-TOKEN': ACCESS_TOKEN
    }
    response = requests.get(f'{GITLAB_URL}/api/v4/projects/{REPO_ID}/repository/files/{FILE_PATH}/raw?ref={BRANCH}', headers=headers)
    response.raise_for_status()
    file_content = response.text
    data = json.loads(file_content)
    return data.get('tasks', [])

# Function to update and push tasks.json to GitLab
def save_tasks_to_gitlab(tasks):
    headers = {
        'PRIVATE-TOKEN': ACCESS_TOKEN
    }
    json_data = json.dumps({"tasks": tasks}).encode('utf-8')
    payload = {
        "branch": BRANCH,
        "commit_message": "Update tasks.json",
        "actions": [
            {
                "action": "update",
                "file_path": FILE_PATH,
                "content": base64.b64encode(json_data).decode('utf-8'),
                "encoding": "base64"
            }
        ]
    }
    response = requests.post(f'{GITLAB_URL}/api/v4/projects/{REPO_ID}/repository/commits', json=payload, headers=headers)
    response.raise_for_status()

# Function to update the task list in the window
def update_task_list(window, tasks):
    window["-TASKS-"].update([
        f"{'[x]' if task['completed'] else '[ ]'} {task['name']}" for task in tasks
    ])

# Main application
def main():
    tasks = load_tasks_from_gitlab()

    layout = [
        [sg.Text("Tasks", font=("Helvetica", 16))],
        [sg.Listbox(
            values=[], size=(50, 15), key="-TASKS-", enable_events=True
        )],
        [sg.Input(key="-NEW_TASK-", size=(50, 15))],
        [sg.Button("Add Task", bind_return_key=True), sg.Button("Mark Completed"), sg.Button("Delete Task")],
    ]

    window = sg.Window("Task Manager", layout, finalize=True)
    update_task_list(window, tasks)

    while True:
        event, values = window.read(timeout=3000)
        if event == sg.WINDOW_CLOSED:
            save_tasks_to_gitlab(tasks)
            break

        if event in ("Add Task", "-NEW_TASK-" + "\r"):
            new_task_name = values["-NEW_TASK-"].strip()
            if new_task_name:
                tasks.append({"name": new_task_name, "completed": False})
                update_task_list(window, tasks)
                window["-NEW_TASK-"].update("")
                save_tasks_to_gitlab(tasks)

        elif event == "Mark Completed":
            selected = values["-TASKS-"]
            if selected:
                task_name = selected[0][4:]  # Remove prefix like [x] or [ ]
                for task in tasks:
                    if task["name"] == task_name:
                        task["completed"] = not task["completed"]
                        break
                update_task_list(window, tasks)
                save_tasks_to_gitlab(tasks)

        elif event == "Delete Task":
            selected = values["-TASKS-"]
            if selected:
                task_name = selected[0][4:]
                tasks = [task for task in tasks if task["name"] != task_name]
                update_task_list(window, tasks)
                save_tasks_to_gitlab(tasks)

    window.close()

if __name__ == "__main__":
    main()
