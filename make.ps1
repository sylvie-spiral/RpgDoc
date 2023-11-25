#collect all files
$baseFiles = (Get-ChildItem doc -File -Recurse | sort-object FullName | select-object -exp FullName)
Write-Host $baseFiles | Format-Table

$files = [System.Collections.Generic.List[string]]::new()

foreach ($currentItemName in $baseFiles) {
    $files.Add(($currentItemName).Replace(' ','\ '))
}

$allArgs = $PsBoundParameters.Values + $args
Write-Host $allArgs

$cmdLine = "--from=markdown " + $files + " " + $allArgs
Write-Host $cmdLine

& "pandoc" $cmdLine.Split(" ")

# cmd.exe /c "pandoc.exe" $cmdLine
Write-Host "Complete."