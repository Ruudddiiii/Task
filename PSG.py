# Define the raw file URL
$RAW_FILE_URL = "https://raw.githubusercontent.com/Ruudddiiii/TaskTravelTime/main/task1.json"

# Function to load tasks from GitHub
function Load-TasksFromGitHub {
    try {
        # Make a GET request to the URL
        $response = Invoke-RestMethod -Uri $RAW_FILE_URL -Method Get

        # Parse the JSON content
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

# Call the function to load tasks
$tasks = Load-TasksFromGitHub

# Output the tasks
if ($tasks.Count -gt 0) {
    Write-Output "Tasks loaded successfully:"
    $tasks | ForEach-Object { Write-Output " - $_.name" }
} else {
    Write-Output "No tasks to display."
}
