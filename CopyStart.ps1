// From https://gist.github.com/YR-ZR0/d88a9f88d0052d835aeda2700ff2f05e
// Script to Copy shortcuts to Startup Folder
[System.Reflection.Assembly]::LoadWithPartialName("System.windows.forms") | Out-Null
 $OpenFileDialog = New-Object System.Windows.Forms.OpenFileDialog
 $OpenFileDialog.ShowDialog()|Out-Null
$File = $OpenFileDialog.filename
$startup = [environment]::getfolderpath("Startup")
Copy-Item $File $startup