if ("$PWD" -ne "$PSScriptRoot") { exit 1 }

$zipName = "WirthMage.zip"
$baseDir = "WirthMage"
$tempDir = Join-Path $Env:TEMP "WirthMage_$(New-Guid)"
New-Item -ItemType Directory -Path "$tempDir\$baseDir" -Force | Out-Null
Set-Location $tempDir

Copy-Item "$PSScriptRoot\dist\WirthMage.exe" -Destination "$baseDir\WirthMage.exe"
Copy-Item "$PSScriptRoot\LICENSE" -Destination "$baseDir\LICENSE.txt"
Copy-Item "$PSScriptRoot\README.md" -Destination "$baseDir\README.txt"
Copy-Item "$PSScriptRoot\ChangeLog.txt" -Destination "$baseDir\ChangeLog.txt"
robocopy "$PSScriptRoot\lib" "$baseDir\lib" /E /NFL /NDL /NJH /NJS /NC /NS

Compress-Archive -Path $baseDir -DestinationPath "$PSScriptRoot\dist\$zipName" -Force -CompressionLevel Optimal
Set-Location $PSScriptRoot
Remove-Item $tempDir -Force -Recurse
