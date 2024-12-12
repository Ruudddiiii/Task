# GitHub settings
$GITHUB_USERNAME = "Ruudddiiii"
$REPO_NAME = "TaskTravelTime"
$GITHUB_TOKEN = "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"
$TASK_FILE = "task1.json"

# GitHub API URL for the contents API
$REPO_API_URL = "https://api.github.com/repos/$GITHUB_USERNAME/$REPO_NAME/contents/$TASK_FILE"

# Function to load tasks from GitHub
function Load-TasksFromGitHub {
    try {
        # Create the headers for authentication
        $headers = @{
            Authorization = "Bearer $GITHUB_TOKEN"
        }

        # Make the GET request
        $response = Invoke-RestMethod -Uri $REPO_API_URL -Headers $headers -Method Get

        # Decode the Base64 content
        if ($response.content) {
            $fileContent = [System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String($response.content))
            $data = $fileContent | ConvertFrom-Json
            return $data.tasks
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
