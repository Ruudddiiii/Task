import requests
import json

RAW_FILE_URL = 'https://raw.githubusercontent.com/Ruudddiiii/TaskTravelTime/main/task1.json'

def load_tasks_from_github():
    try:
        response = requests.get(RAW_FILE_URL)
        response.raise_for_status()  # Raise an error for bad HTTP status
        data = response.json()  # Parse the JSON content
        return data.get('tasks', [])
    except requests.exceptions.RequestException as e:
        print(f"Error loading tasks: {e}")
        return []

tasks = load_tasks_from_github()
print(tasks)
