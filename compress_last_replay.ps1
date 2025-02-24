# Define the base path to the Men of War profiles directory
$basePath = "$HOME\Documents\My Games\men of war - assault squad 2\profiles"

# Get the profile directory (assuming there's only one)
$profileDir = Get-ChildItem -Path $basePath | Where-Object { $_.PSIsContainer } | Select-Object -First 1

# Define the replays path
$replaysPath = Join-Path -Path $profileDir.FullName -ChildPath "replays"

# Check if the replays folder exists
if (Test-Path -Path $replaysPath) {
    # Get the most recently modified directory inside the replays folder
    $mostRecentDirectory = Get-ChildItem -Path $replaysPath -Directory | Sort-Object LastWriteTime -Descending | Select-Object -First 1

    if ($mostRecentDirectory) {
        # Get the name of the most recent directory
        $folderName = $mostRecentDirectory.Name

        # Generate a hash of the contents of the most recent directory
        $fileHash = Get-ChildItem -Path $mostRecentDirectory.FullName -File | Get-FileHash | Sort-Object Hash | ForEach-Object { $_.Hash } | Out-String
        $fileHash = ($fileHash -replace '\s+', '') -replace '[^0-9a-fA-F]', ''

        # Trim the hash to 55 characters
        $trimmedHash = $fileHash.Substring(0, [Math]::Min(55, $fileHash.Length))

        # Define the path for the output zip file with the new naming convention
        $zipFileName = "${folderName}_${trimmedHash}.zip"
        $zipFilePath = Join-Path -Path $mostRecentDirectory.FullName -ChildPath $zipFileName

        # Load the necessary .NET assembly
        Add-Type -AssemblyName System.IO.Compression.FileSystem

        # Remove the zip file if it exists
        if (Test-Path $zipFilePath) {
            Remove-Item -Path $zipFilePath -Force
        }

        # Create the zip file using System.IO.Compression.ZipFile
        [System.IO.Compression.ZipFile]::CreateFromDirectory($mostRecentDirectory.FullName, $zipFilePath)

        # Define the new destination path
        $destinationPath = "C:\Users\emile\Documents\Code\MoW_analizer\replays"

        # Check if the destination directory exists
        if (-Not (Test-Path -Path $destinationPath)) {
            # If it does not exist, move to the desktop instead
            $destinationPath = [System.Environment]::GetFolderPath('Desktop')
            Write-Host "Destination path does not exist. Defaulting to desktop."
        }

        # Define the final destination path for the zip file
        $destinationZipFilePath = Join-Path -Path $destinationPath -ChildPath $zipFileName

        # Move the zip file to the destination (cut, not copy)
        Move-Item -Path $zipFilePath -Destination $destinationZipFilePath

        Write-Host "Moved compressed file: $zipFilePath to: $destinationZipFilePath"
    } else {
        Write-Host "No directories found inside the replays folder."
    }
} else {
    Write-Host "Replays folder not found."
}
