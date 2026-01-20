if ("$PWD" -ne "$PSScriptRoot") { exit 1 }

$zipName = "WirthMage.zip"
$baseDirName = "WirthMage"
$tempDir = Join-Path $Env:TEMP "WirthMage_$(New-Guid)"
$distBaseDir = New-Item -ItemType Directory -Path "$tempDir\$baseDirName" -Force
Set-Location $tempDir

Copy-Item "$PSScriptRoot\dist\app.dist\*" -Destination "$distBaseDir" -Recurse -Exclude @(
	"compare.exe"
	"composite.exe"
	"conjure.exe"
	"identify.exe"
	"mogrify.exe"
	"montage.exe"
	"stream.exe"
)
Copy-Item "$PSScriptRoot\LICENSE" -Destination "$distBaseDir\LICENSE.txt"
Copy-Item "$PSScriptRoot\README.md" -Destination "$distBaseDir\README.txt"
Copy-Item "$PSScriptRoot\ChangeLog.txt" -Destination "$distBaseDir\ChangeLog.txt"

Get-ChildItem $distBaseDir -Recurse -File | Sort-Object Directory, {
	if ($_.Extension -eq ".exe") { 1 }
	elseif ($_.Extension -in ".txt", ".md") { 2 }
	else { 3 }
}, Extension, Name | ForEach-Object {
	"- " + ($_.FullName -replace "^$([regex]::Escape($distBaseDir.FullName))\\?", "")
} | Out-File "$PSScriptRoot\dist\$zipName.files.txt" -Encoding utf8

Compress-Archive -Path $distBaseDir -DestinationPath "$PSScriptRoot\dist\$zipName" -Force -CompressionLevel Optimal

Set-Location $PSScriptRoot
Remove-Item $tempDir -Force -Recurse
