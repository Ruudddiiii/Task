import subprocess
import json

def load_tasks_from_powershell():
    # Define the PowerShell script
    powershell_script = """
    $RAW_FILE_URL = "https://raw.githubusercontent.com/Ruudddiiii/TaskTravelTime/main/task1.json"

    function Load-TasksFromGitHub {
        try {
            $response = Invoke-RestMethod -Uri $RAW_FILE_URL -Method Get
            if ($response -and $response.tasks) {
                return $response.tasks
            } else {
                Write-Output "No tasks found in the response."
                return @()
            }
        } catch {
            Write-Output "Error loading tasks from GitHub: $_"
            return @()
        }
    }

    $tasks = Load-TasksFromGitHub
    $tasks | ConvertTo-Json -Depth 10
    """

    try:
        # Run the PowerShell script
        result = subprocess.run(
            ["powershell", "-Command", powershell_script],
            capture_output=True,
            text=True,
            check=True
        )
        # Parse the output as JSON
        tasks = json.loads(result.stdout)
        return tasks
    except subprocess.CalledProcessError as e:
        print(f"Error executing PowerShell script: {e.stderr}")
        return []

# Fetch tasks using the PowerShell script
tasks = load_tasks_from_powershell()

# Display the tasks
if tasks:
    print("Tasks loaded successfully:")
    for task in tasks:
        print(f" - {task.get('name')}")
else:
    print("No tasks to display.")
