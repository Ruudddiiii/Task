import requests
import json

RAW_FILE_URL = 'https://raw.githubusercontent.com/Ruudddiiii/TaskTravelTime/main/task1.json'
GITHUB_TOKEN = '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'

def load_tasks_from_github():
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    try:
        response = requests.get(RAW_FILE_URL, headers=headers)
        response.raise_for_status()
        data = response.json()  # Parse JSON content
        return data.get('tasks', [])
    except requests.exceptions.RequestException as e:
        print(f"Error loading tasks: {e}")
        return []

tasks = load_tasks_from_github()
print(tasks)
