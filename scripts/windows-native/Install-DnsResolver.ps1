#Requires -Version 5.1
<#
.SYNOPSIS
  Register a Scheduled Task to start the Windows DNS resolver at logon (LAN only).
#>
param(
  [string]$ListenAddr = "",
  [int]$Port = 53,
  [string]$TaskName = "freebox-dns-resolver"
)

$ErrorActionPreference = "Stop"
$id = [Security.Principal.WindowsIdentity]::GetCurrent()
$p = New-Object Security.Principal.WindowsPrincipal($id)
if (-not $p.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
  Write-Error "Run as Administrator to create the scheduled task."
}

$script = Join-Path $PSScriptRoot "Run-DnsResolver.ps1"
$listenArg = if ($ListenAddr) { " -ListenAddr $ListenAddr" } else { "" }
$arg = "-NoProfile -ExecutionPolicy Bypass -File `"$script`"$listenArg -Port $Port"
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument $arg
$trigger = New-ScheduledTaskTrigger -AtLogOn
$principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -RunLevel Highest -LogonType Interactive
Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Principal $principal -Force | Out-Null
Write-Host "Scheduled task '$TaskName' registered (at logon, elevated, LAN bind)."
Write-Host "Start now:  Start-ScheduledTask -TaskName '$TaskName'"
Write-Host "Remove:     Unregister-ScheduledTask -TaskName '$TaskName' -Confirm:`$false"
Write-Host "Never open router port-forward for UDP/TCP 53 — docs/lan-only.md"
