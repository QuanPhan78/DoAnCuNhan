[CmdletBinding()]
param(
    [ValidateSet('Prepare','Reset','Check','Snapshot','Web','Mobile','Install','Mirror','Record','Sessions','Verify')]
    [string]$Action = 'Check',
    [ValidateSet('RentalSystemDB_V2')]
    [string]$Database = 'RentalSystemDB_V2',
    [string]$Serial,
    [string]$ScrcpyPath = 'scrcpy',
    [ValidatePattern('^[a-zA-Z0-9_-]+$')][string]$Clip = 'mobile-full'
)
$ErrorActionPreference = 'Stop'
$taskRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$taskOutput = Join-Path $taskRoot 'outputs\demo-check'
$phoneAssets = Join-Path $taskRoot 'outputs\demo'
$taskPort = 5001
$harness = Join-Path $PSScriptRoot 'bin\Debug\net9.0\DemoHarness.dll'

function Invoke-Checked([string]$Executable, [string[]]$Arguments) {
    & $Executable @Arguments
    if ($LASTEXITCODE -ne 0) { throw "$Executable exited with code $LASTEXITCODE" }
}
function Assert-PortFree {
    $client = [Net.Sockets.TcpClient]::new()
    try {
        $pending = $client.ConnectAsync('localhost', $taskPort)
        if ($pending.Wait(700) -and $client.Connected) {
            throw "Port $taskPort is in use. Stop its backend before preparing/resetting data."
        }
    } catch [AggregateException] {
        # A refused connection means the port is free.
    } finally { $client.Dispose() }
}
function Get-Adb {
    $found = Get-Command adb -ErrorAction SilentlyContinue
    if ($found) { return $found.Source }
    foreach ($candidate in @(
        "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe",
        "$env:ANDROID_HOME\platform-tools\adb.exe",
        "$env:ANDROID_SDK_ROOT\platform-tools\adb.exe"
    )) { if (Test-Path -LiteralPath $candidate) { return $candidate } }
    throw 'ADB not found. Install Android SDK platform-tools or add adb to PATH.'
}
function Get-UsbDevice([string]$Adb) {
    $lines = & $Adb devices -l
    if ($LASTEXITCODE -ne 0) { throw 'ADB unavailable.' }
    $devices = @($lines | Where-Object { $_ -match '^\S+\s+device(?:\s|$)' } | ForEach-Object { ($_ -split '\s+')[0] })
    if ($Serial) {
        if ($Serial -notin $devices) { throw "USB device $Serial is not authorized/connected. Unlock it and accept USB debugging." }
        return $Serial
    }
    $usbSerial = (& $Adb -d get-serialno 2>$null | Select-Object -First 1)
    if ($LASTEXITCODE -ne 0 -or -not $usbSerial -or $usbSerial.Trim() -notin $devices) {
        throw 'Expected one authorized USB phone. Connect/unlock it, accept USB debugging, or use -Serial when several are connected.'
    }
    return $usbSerial.Trim()
}

if ($Action -in @('Prepare','Reset','Check','Snapshot','Web','Verify')) {
    Invoke-Checked 'dotnet' @('build', (Join-Path $PSScriptRoot 'DemoHarness.csproj'), '--nologo', '-v:q', '-p:NuGetAudit=false')
}
switch ($Action) {
    { $_ -in @('Prepare','Reset','Check','Snapshot') } {
        if ($Action -in @('Prepare','Reset','Snapshot')) { Assert-PortFree }
        Invoke-Checked 'dotnet' @($harness, $Action.ToLowerInvariant(), $Database)
    }
    'Web' {
        Assert-PortFree
        Invoke-Checked 'dotnet' @($harness, 'check', $Database)
        $oldConnection = $env:ConnectionStrings__DefaultConnection
        $oldEnvironment = $env:ASPNETCORE_ENVIRONMENT
        try {
            $env:ConnectionStrings__DefaultConnection = "Server=localhost;Database=$Database;Trusted_Connection=True;TrustServerCertificate=True;"
            $env:ASPNETCORE_ENVIRONMENT = 'Development'
            Write-Host "DEMO DATABASE: $Database | http://localhost:$taskPort | Ctrl+C to stop"
            Invoke-Checked 'dotnet' @((Join-Path $taskRoot 'RentalSystem\bin\Debug\net9.0\RentalSystem.dll'), '--contentRoot', (Join-Path $taskRoot 'RentalSystem'), '--webroot', (Join-Path $taskOutput 'wwwroot'), '--urls', "http://localhost:$taskPort")
        } finally {
            $env:ConnectionStrings__DefaultConnection = $oldConnection
            $env:ASPNETCORE_ENVIRONMENT = $oldEnvironment
        }
    }
    { $_ -in @('Mobile','Install','Mirror','Record') } {
        $adb = Get-Adb
        $device = Get-UsbDevice $adb
        if ($Action -in @('Mobile','Install')) {
            $response = Invoke-WebRequest "http://localhost:$taskPort/api/devices" -UseBasicParsing
            if (-not (($response.Content | ConvertFrom-Json) | Where-Object { $_.name -eq 'Laptop Demo Dell Latitude 5430' })) {
                throw "Port $taskPort is not serving the rehearsal fixture."
            }
            Invoke-Checked $adb @('-s', $device, 'reverse', 'tcp:5000', "tcp:$taskPort")
        }
        if ($Action -eq 'Install') {
            $apk = Join-Path $phoneAssets 'android\RentalSystem-demo-debug.apk'
            if (-not (Test-Path -LiteralPath $apk)) { throw 'Demo APK missing. Use -Action Mobile to build/run from Flutter, or follow the APK build command in README.' }
            Invoke-Checked $adb @('-s', $device, 'install', '-r', $apk)
            Invoke-Checked $adb @('-s', $device, 'shell', 'am', 'start', '-n', 'com.example.quan_ly_cho_thue_thiet_bi/.MainActivity')
        } elseif ($Action -eq 'Mobile') {
            Push-Location (Join-Path $taskRoot 'MobileApp')
            try { Invoke-Checked 'flutter' @('run', '-d', $device, '--debug', '--dart-define=API_BASE_URL=http://127.0.0.1:5000/api') }
            finally { Pop-Location }
        } else {
            if ($ScrcpyPath -eq 'scrcpy' -and -not (Get-Command $ScrcpyPath -ErrorAction SilentlyContinue)) {
                $portable = Join-Path $phoneAssets 'tools\scrcpy\scrcpy-win64-v5.0.1\scrcpy.exe'
                if (Test-Path -LiteralPath $portable) { $ScrcpyPath = $portable }
            }
            if (-not (Get-Command $ScrcpyPath -ErrorAction SilentlyContinue)) {
                throw 'scrcpy not found. See docs/demo/README.md for the official installation source; or pass -ScrcpyPath.'
            }
            $mirrorArgs = @('--serial', $device, '--window-title', 'RentalSystem - Khach hang Mobile', '--stay-awake', '--no-audio')
            if ($Action -eq 'Record') {
                $videos = Join-Path $taskOutput 'videos'
                New-Item -ItemType Directory -Path $videos -Force | Out-Null
                $mirrorArgs += "--record=$(Join-Path $videos ($Clip + '-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.mp4'))"
            }
            Invoke-Checked $ScrcpyPath $mirrorArgs
        }
    }
    'Sessions' {
        # Dedicated browser profiles isolate authentication cookies for each role.
        $browser = @(
            "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe",
            "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
            "$env:ProgramFiles\Google\Chrome\Application\chrome.exe"
        ) | Where-Object { Test-Path -LiteralPath $_ } | Select-Object -First 1
        if (-not $browser) { throw 'Edge/Chrome not found. Open three separate browser profiles manually.' }
        foreach ($role in @('sale','tech','admin')) {
            $profile = Join-Path $taskOutput "browser-$role"
            # Visible interactive browser windows are the requested presentation surfaces.
            Start-Process -FilePath $browser -ArgumentList @("--user-data-dir=`"$profile`"", '--no-first-run', '--new-window', "http://localhost:$taskPort/Account/Login")
        }
        Write-Host 'Log in: sale@demo.invalid / tech@demo.invalid / admin@demo.invalid. Password: Demo@123. Keep the three profiles open.'
    }
    'Verify' {
        $previousDatabase = $env:RENTALSYSTEM_VERIFY_DATABASE
        try {
            $env:RENTALSYSTEM_VERIFY_DATABASE = $Database
            Invoke-Checked 'python' @((Join-Path $PSScriptRoot 'verify_demo.py'))
        } finally { $env:RENTALSYSTEM_VERIFY_DATABASE = $previousDatabase }
    }
}
