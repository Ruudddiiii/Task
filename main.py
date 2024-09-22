import json
import requests
from requests.auth import HTTPBasicAuth
import base64
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.properties import BooleanProperty, StringProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
import random

# Generate a random number between 0 and 1
# random_number = random.random()

# GitHub settings
GITHUB_USERNAME = 'Ruudddiiii'
REPO_NAME = 'TaskTravelTime'
GITHUB_TOKEN = ''
TASK_FILE = 'tasks.json'

# GitHub API URLs
REPO_API_URL = f'https://api.github.com/repos/{GITHUB_USERNAME}/{REPO_NAME}/contents/{TASK_FILE}'
Window.clearcolor = (random.random(), random.random(), random.random(), random.random())

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
        print(f"Error loading tasks from GitHub: {e}")
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
    except Exception as e:
        print(f"Error saving tasks to GitHub: {e}")

class SelectableTaskItem(RecycleDataViewBehavior, BoxLayout):
    text = StringProperty()
    selected = BooleanProperty(False)

    def refresh_view_attrs(self, rv, index, data):
        # Set the label text for the task
        self.text = data['text']
        return super(SelectableTaskItem, self).refresh_view_attrs(rv, index, data)

    
# Task list display (RecycleView)
class TaskListView(RecycleView):
    def __init__(self, **kwargs):
        super(TaskListView, self).__init__(**kwargs)
        # Use RecycleBoxLayout to allow dynamic height adjustment
        self.layout = RecycleBoxLayout(default_size=(None, 26),
                                       size_hint_y=None,
                                       orientation='horizontal')
        self.layout.bind(minimum_height=self.layout.setter('height'))
        self.add_widget(self.layout)

    def update_tasks(self, tasks):
        # Update task list and clear previous selection
        self.data = [{'text': task['name']} for task in tasks]
        self.refresh_from_data()

# Main app class
class TaskManagerApp(App):

    def build(self):
        # Set the path to the custom icon
        self.icon = '/home/ruddi/Downloads/task.png'  # Replace with the actual path to your icon

        # Main layout for the app
        self.layout = BoxLayout(orientation='vertical')

        # Input for new tasks
        self.new_task_input = TextInput(hint_text='Enter new task', size_hint=(1, 0.2))
        self.layout.add_widget(self.new_task_input)

        # Label to display all tasks
        self.display_label = Label(text='SYNC', size_hint=(1, 0.1), font_size='28sp')
        self.layout.add_widget(self.display_label)

        # Scrollable task list display
        scroll_view = ScrollView(size_hint=(1, 0.6))  # Adjust size_hint as needed
        self.task_list = TaskListView(size_hint_y=None)  # RecycleView will be added here
        scroll_view.add_widget(self.task_list)

        # Add the ScrollView to the main layout
        self.layout.add_widget(scroll_view)

        # Create a BoxLayout to center the buttons horizontally
        button_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), padding=[50, 0], spacing=20)

        # Button to add new task
        add_task_button = Button(text='Add Task', size_hint=(0.3, 1))
        add_task_button.bind(on_press=self.add_task)
        button_layout.add_widget(add_task_button)

        # Button to delete the most recent task
        delete_task_button = Button(text='Delete Task', size_hint=(0.3, 1))
        delete_task_button.bind(on_press=self.delete_task)
        button_layout.add_widget(delete_task_button)

        # Button to undo the most recent delete
        undo_delete_button = Button(text='Undo Delete', size_hint=(0.3, 1))
        undo_delete_button.bind(on_press=self.undo_delete)
        button_layout.add_widget(undo_delete_button)

        # Button to save changes to GitHub
        save_changes_button = Button(text='Save Changes', size_hint=(0.3, 1))
        save_changes_button.bind(on_press=self.save_changes)
        button_layout.add_widget(save_changes_button)

        # Add the button layout to the main layout
        self.layout.add_widget(button_layout)

        # Schedule the task loading after UI is ready (delayed by 1 second)
        Clock.schedule_once(self.load_tasks, 1)

        # List to store all deleted tasks
        self.deleted_tasks = []

        return self.layout

    def load_tasks(self, dt):
        """ Load tasks from GitHub """
        self.tasks = load_tasks_from_github()
        self.task_list.update_tasks(self.tasks)
        self.update_display_label()

    def add_task(self, instance):
        """ Add a new task """
        new_task = self.new_task_input.text.strip()
        if new_task:
            self.tasks.append({"name": new_task, "completed": False})
            print(f"Added task: {new_task}")  # Debug log
            self.task_list.update_tasks(self.tasks)
            self.update_display_label()
            self.new_task_input.text = ''
        else:
            print("Input is empty, no task added")  # Log if input is empty

    def update_display_label(self):
        """ Update the label to display all tasks """
        task_list_str = '\n'.join(task['name'] for task in self.tasks)
        self.display_label.text = task_list_str or 'Your tasks will appear here'

    def delete_task(self, instance):
        """ Delete the most recent task and store it in deleted_tasks list """
        if self.tasks:
            # Store the most recent task in the deleted_tasks list
            deleted_task = self.tasks.pop()
            self.deleted_tasks.append(deleted_task)
            print(f"Deleted task: {deleted_task['name']}")  # Debug log
            self.task_list.update_tasks(self.tasks)
            self.update_display_label()
        else:
            print("No tasks to delete")  # Log if no tasks available

    def undo_delete(self, instance):
        """ Restore all deleted tasks """
        if self.deleted_tasks:
            # Restore all tasks from the deleted_tasks list
            while self.deleted_tasks:
                restored_task = self.deleted_tasks.pop()
                self.tasks.append(restored_task)
                print(f"Restored task: {restored_task['name']}")  # Debug log
            self.task_list.update_tasks(self.tasks)
            self.update_display_label()
        else:
            print("No tasks to undo")  # Log if there are no tasks to undo

    def save_changes(self, instance):
        """ Save the current task list to GitHub """
        save_tasks_to_github(self.tasks)

if __name__ == '__main__':
    TaskManagerApp().run()
