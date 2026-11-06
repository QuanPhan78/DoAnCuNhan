# Portable official Windows release; no system-wide installation or PATH changes.
$ErrorActionPreference = 'Stop'
$taskRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$version = '5.0.1'
$checksum = 'b12a2c4ee8be317422451fc7dcf8ee20a71b5ea7ef9ad73ddd825a25316227a5'
$folder = Join-Path $taskRoot 'outputs\demo\tools\scrcpy'
New-Item -ItemType Directory -Path $folder -Force | Out-Null
$archive = Join-Path $folder "scrcpy-win64-v$version.zip"
$url = "https://github.com/Genymobile/scrcpy/releases/download/v$version/scrcpy-win64-v$version.zip"
if (-not (Test-Path -LiteralPath $archive)) {
    Invoke-WebRequest -Uri $url -OutFile $archive -UseBasicParsing
}
if ((Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash.ToLowerInvariant() -ne $checksum) {
    throw "SHA256 mismatch for $archive. Refusing to extract or execute."
}
Expand-Archive -LiteralPath $archive -DestinationPath $folder -Force
$executable = Join-Path $folder "scrcpy-win64-v$version\scrcpy.exe"
& $executable --version
if ($LASTEXITCODE -ne 0) { throw 'scrcpy version check failed.' }
[ordered]@{ version=$version; source=$url; sha256=$checksum; executable=$executable } |
    ConvertTo-Json | Set-Content -LiteralPath (Join-Path $folder 'installation.json') -Encoding utf8
