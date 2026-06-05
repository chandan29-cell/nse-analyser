# Creates a desktop shortcut named 'nse analyser' that runs the bundled run_local.bat
$WshShell = New-Object -ComObject WScript.Shell
$ShortcutPath = "$env:USERPROFILE\Desktop\nse analyser.lnk"
$TargetPath = "${PWD}\run_local.bat"
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $TargetPath
$Shortcut.WindowStyle = 1
$Shortcut.Description = "Run NSE Analyser (backend)"
$Shortcut.Save()
Write-Output "Shortcut created at $ShortcutPath"