#collect all files - this is formatted the way that it is to handle
#filenames with spaces.  This script is intended only for use on Windows,
#but except for the optimization at the end, works fine in Powershell on Linux as well.
$files = (Get-ChildItem doc -File -Recurse -Exclude *.css | sort-object FullName | select-object -exp FullName)
$cssFiles = (Get-ChildItem doc -File -Recurse -Filter *.css | sort-object FullName | select-object -exp FullName)

$css = [System.Collections.Generic.List[string]]::new();

Write-Host '----'

Write-Host $files | Format-Table

foreach ($currentItemName in $cssFiles) {
    $css.Add('-c')
    $css.Add($currentItemName)
}

Write-Host '----'

Write-Host [String::Join](" ", $css) 

Write-Host '----'

# all the arguments that were passed to the script are forwarded to the command
$allArgs = $PsBoundParameters.Values + $args
Write-Host $allArgs

Write-Host '----'
Write-Host 'Starting PanDoc'
& "pandoc" -s --embed-resources  --template=template.html @($files) @($css) $allArgs -o out\Document.html
& "wkhtmltopdf" -s Letter --print-media-type -L 0 -R 0 -T 0 -B 0 .\out\Document.html .\out\Document.pdf

Write-Host '----'
Write-Host 'Starting PDFSizeOpt'
.\pdfsizeopt-win32\pdfsizeopt.exe out\Document.pdf