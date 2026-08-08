<#
.SYNOPSIS
    Installs Minikube and kubectl on Windows through Chocolatey.

.DESCRIPTION
    The script is idempotent: running it again on a machine that already has
    Chocolatey, Minikube and kubectl only re-prints the version output.
    Run it from an elevated PowerShell window, because both the Chocolatey
    bootstrap and the package installs write to machine-wide locations.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File .\install.ps1
#>

[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

function Write-Step {
    param([string] $Message)
    Write-Host ''
    Write-Host "==> $Message" -ForegroundColor Cyan
}

function Write-Ok {
    param([string] $Message)
    Write-Host "    $Message" -ForegroundColor Green
}

function Test-CommandExists {
    param([string] $Name)
    return [bool] (Get-Command $Name -ErrorAction SilentlyContinue)
}

function Update-SessionPath {
    # A freshly installed package adds itself to the machine or user PATH, but
    # this PowerShell session still holds the old value. Rebuild it here.
    $machine = [Environment]::GetEnvironmentVariable('Path', 'Machine')
    $user = [Environment]::GetEnvironmentVariable('Path', 'User')
    $env:Path = "$machine;$user"
}

# Fail early with a readable message instead of a permission error halfway in.
$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
$principal = New-Object Security.Principal.WindowsPrincipal($identity)
if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Warning 'This shell is not elevated. Installing Chocolatey and packages needs administrator rights.'
    Write-Warning 'Close this window, open PowerShell with "Run as administrator", and run the script again.'
    exit 1
}

Write-Host 'Minikube and kubectl setup for Windows' -ForegroundColor White
Write-Host "PowerShell $($PSVersionTable.PSVersion) on $([Environment]::OSVersion.VersionString)"

# --- Step 1: Chocolatey -----------------------------------------------------

Write-Step 'Checking for Chocolatey'
if (Test-CommandExists 'choco') {
    Write-Ok "Chocolatey is already installed ($((choco --version)))"
}
else {
    Write-Host '    Chocolatey was not found. Installing it now.'
    Write-Host '    The next command downloads the official install script from'
    Write-Host '    community.chocolatey.org and runs it in this elevated shell.'

    # Set-ExecutionPolicy Bypass is scoped to this process only, so the machine
    # policy is left untouched. An elevated shell is required: the installer
    # writes to C:\ProgramData\chocolatey and to the machine PATH.
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

    Update-SessionPath
    if (-not (Test-CommandExists 'choco')) {
        throw 'Chocolatey install finished but choco is still not on PATH. Open a new shell and run the script again.'
    }
    Write-Ok "Chocolatey installed ($((choco --version)))"
}

# --- Step 2: packages -------------------------------------------------------

$packages = @(
    @{ Name = 'minikube';       Command = 'minikube' },
    @{ Name = 'kubernetes-cli'; Command = 'kubectl' }
)

foreach ($package in $packages) {
    Write-Step "Checking for $($package.Name)"
    if (Test-CommandExists $package.Command) {
        Write-Ok "$($package.Command) is already installed, skipping the package install."
        continue
    }

    Write-Host "    Installing $($package.Name) with Chocolatey."
    choco install $package.Name --yes --no-progress
    if ($LASTEXITCODE -ne 0) {
        throw "choco install $($package.Name) failed with exit code $LASTEXITCODE."
    }

    Update-SessionPath
    if (-not (Test-CommandExists $package.Command)) {
        Write-Warning "$($package.Command) is installed but not on PATH in this session. Open a new shell to use it."
    }
    else {
        Write-Ok "$($package.Command) installed."
    }
}

# --- Step 3: versions -------------------------------------------------------

Write-Step 'minikube version'
minikube version

Write-Step 'kubectl version --client'
kubectl version --client

Write-Step 'Done'
Write-Host '    Next: minikube start --driver=docker' -ForegroundColor Green
Write-Host '    Then: minikube status' -ForegroundColor Green
Write-Host '    Then: kubectl get nodes' -ForegroundColor Green
