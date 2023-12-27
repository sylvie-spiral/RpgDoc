#collect all files - this is formatted the way that it is to handle
#filenames with spaces.  This script is intended only for use on Windows,
#but except for the optimization at the end, works fine in Powershell on Linux as well.
$baseFiles = (Get-ChildItem doc -File -Recurse | sort-object FullName | select-object -exp FullName)
Write-Host $baseFiles | Format-Table

$files = [System.Collections.Generic.List[string]]::new()

foreach ($currentItemName in $baseFiles) {
    $files.Add(($currentItemName).Replace(' ','\ '))
}

# all the arguments that were passed to the script are forwarded to the command
$allArgs = $PsBoundParameters.Values + $args
Write-Host $allArgs

& "pandoc" $cmdLine $files $allArgs -o out\Document.pdf
.\pdfsizeopt-win32\pdfsizeopt.exe out\Document.pdf