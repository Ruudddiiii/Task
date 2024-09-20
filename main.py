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

# GitHub settings
GITHUB_USERNAME = 'Ruudddiiii'
REPO_NAME = 'TaskTravelTime'
GITHUB_TOKEN = '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'
TASK_FILE = 'tasks.json'

# GitHub API URLs
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

# RecycleView item with selectable behavior
class SelectableTaskItem(RecycleDataViewBehavior, BoxLayout):
    text = StringProperty()  # Task text
    selected = BooleanProperty(False)  # Selection state

    def refresh_view_attrs(self, rv, index, data):
        """ Update the task item view with provided data """
        self.text = data['text']
        return super(SelectableTaskItem, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        """ Handle task selection on touch """
        if super(SelectableTaskItem, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos):
            # Toggle the selection state
            self.selected = not self.selected
            self.parent.select_task(self)
            return True
        return False

# Task list display (RecycleView)
class TaskListView(RecycleView):
    def __init__(self, **kwargs):
        super(TaskListView, self).__init__(**kwargs)
        self.data = []
        self.viewclass = 'SelectableTaskItem'
        self.selected_task = None  # Variable to store selected task

    def select_task(self, task):
        """ Store the selected task """
        # Deselect the previously selected task
        if self.selected_task and self.selected_task != task:
            self.selected_task.selected = False
        
        # Set the new task as selected
        self.selected_task = task

    def update_tasks(self, tasks):
        """ Update the RecycleView data """
        self.data = [{'text': task['name']} for task in tasks]
        self.refresh_from_data()

# Main app class
class TaskManagerApp(App):
    def build(self):
        # Set the path to the custom icon
        self.icon = '/home/ruddi/Downloads/task.png'  # Replace with the actual path to your icon

          # Main layout for the app
        self.layout = BoxLayout(orientation='vertical')

        # Label to display all tasks (Moved to the top)


        # Input for new tasks (Moved down)
        self.new_task_input = TextInput(hint_text='Enter new task', size_hint=(1, 0.2))
        self.layout.add_widget(self.new_task_input)

        self.display_label = Label(text='Your tasks will appear here', size_hint=(1, 0.2), font_size='28sp')
        self.layout.add_widget(self.display_label)

        # Task list display (RecycleView)
        self.task_list = TaskListView(size_hint=(1, 0.7))
        self.layout.add_widget(self.task_list)

        # Create a BoxLayout to center the buttons horizontally
        button_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1), padding=[50, 0], spacing=20)

        # Button to add new task
        add_task_button = Button(text='Add Task', size_hint=(0.3, 1))
        add_task_button.bind(on_press=self.add_task)
        button_layout.add_widget(add_task_button)

        # Button to delete selected task
        delete_task_button = Button(text='Delete Task', size_hint=(0.3, 1))
        delete_task_button.bind(on_press=self.delete_task)
        button_layout.add_widget(delete_task_button)

        # Button to save changes to GitHub
        save_changes_button = Button(text='Save Changes', size_hint=(0.3, 1))
        save_changes_button.bind(on_press=self.save_changes)
        button_layout.add_widget(save_changes_button)

        # Add the button layout to the main layout
        self.layout.add_widget(button_layout)

        # Schedule the task loading after UI is ready (delayed by 1 second)
        Clock.schedule_once(self.load_tasks, 1)

        return self.layout
    
    def load_tasks(self, dt):
        """ Load tasks from GitHub """
        self.tasks = load_tasks_from_github()
        self.task_list.update_tasks(self.tasks)
        self.update_display_label()

    def add_task(self, instance):
        """ Add a new task from the input field """
        new_task = self.new_task_input.text.strip()
        if new_task:
            self.tasks.append({"name": new_task, "completed": False})
            self.task_list.update_tasks(self.tasks)
            self.update_display_label()
            self.new_task_input.text = ''  # Clear input field after adding task

    def update_display_label(self):
        """ Update the label to display all tasks """
        task_list_str = '\n'.join(task['name'] for task in self.tasks)
        self.display_label.text = task_list_str or 'Your tasks will appear here'

    def delete_task(self, instance):
        """ Delete the selected task """
        if self.task_list.selected_task:
            task_name = self.task_list.selected_task.text
            self.tasks = [task for task in self.tasks if task['name'] != task_name]
            self.task_list.update_tasks(self.tasks)
            self.update_display_label()
            self.task_list.selected_task = None  # Reset selected task

    def save_changes(self, instance):
        """ Save the current task list to GitHub """
        save_tasks_to_github(self.tasks)

if __name__ == '__main__':
    TaskManagerApp().run()
