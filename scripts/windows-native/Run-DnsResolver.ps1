#Requires -Version 5.1
<#
.SYNOPSIS
  Run freebox-dns as a native Windows DNS resolver (dnsproxy.exe) — LAN only, no Docker.

.DESCRIPTION
  Binds to a private LAN IPv4 by default (never 0.0.0.0 / Internet).
  Downloads AdGuard dnsproxy if needed.

.EXAMPLE
  .\Run-DnsResolver.ps1
  .\Run-DnsResolver.ps1 -ListenAddr 192.168.1.50
  .\Run-DnsResolver.ps1 -Port 5353
#>
param(
  [string]$ListenAddr = "",
  [int]$Port = 53,
  [string]$DnsproxyVersion = "v0.84.1",
  # DANGEROUS — opens all interfaces (including public). Prefer LAN IP.
  [switch]$ForcePublicBind
)

$ErrorActionPreference = "Stop"
$NativeDir = $PSScriptRoot
$Root = (Resolve-Path (Join-Path $NativeDir "..\..")).Path
$BinDir = Join-Path $NativeDir "bin"
$Exe = Join-Path $BinDir "dnsproxy.exe"
$Tpl = Join-Path $Root "config\dnsproxy\windows-standalone.yaml.tpl"
$RuntimeYaml = Join-Path $BinDir "windows-runtime.yaml"

function Test-IsAdmin {
  $id = [Security.Principal.WindowsIdentity]::GetCurrent()
  $p = New-Object Security.Principal.WindowsPrincipal($id)
  return $p.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Test-IsPrivateIPv4([string]$ip) {
  try {
    $a = [System.Net.IPAddress]::Parse($ip)
  } catch { return $false }
  $b = $a.GetAddressBytes()
  if ($b[0] -eq 10) { return $true }
  if ($b[0] -eq 192 -and $b[1] -eq 168) { return $true }
  if ($b[0] -eq 172 -and $b[1] -ge 16 -and $b[1] -le 31) { return $true }
  if ($b[0] -eq 127) { return $true }
  return $false
}

function Get-PrimaryLanIPv4 {
  $candidates = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
    Where-Object {
      $_.IPAddress -and
      (Test-IsPrivateIPv4 $_.IPAddress) -and
      $_.IPAddress -notlike "169.254.*" -and
      $_.PrefixOrigin -ne "WellKnown"
    } |
    Sort-Object -Property InterfaceMetric
  if ($candidates) { return $candidates[0].IPAddress }
  return $null
}

if (-not $ListenAddr) {
  $ListenAddr = Get-PrimaryLanIPv4
  if (-not $ListenAddr) {
    Write-Error "No private LAN IPv4 found. Pass -ListenAddr 192.168.x.x explicitly."
  }
  Write-Host "Auto LAN bind: $ListenAddr"
}

if ($ListenAddr -eq "0.0.0.0" -or $ListenAddr -eq "::" -or $ListenAddr -eq "*") {
  if (-not $ForcePublicBind) {
    Write-Error "Refusing all-interfaces bind ($ListenAddr). Use a LAN IP, or -ForcePublicBind (DANGEROUS: open resolver on Internet)."
  }
  Write-Warning "ForcePublicBind: DNS may be reachable from the Internet — amplification risk."
} elseif (-not (Test-IsPrivateIPv4 $ListenAddr)) {
  if (-not $ForcePublicBind) {
    Write-Error "ListenAddr $ListenAddr is not a private LAN address. Refusing public bind (open resolver risk)."
  }
  Write-Warning "ForcePublicBind with non-private IP $ListenAddr"
}

if ($Port -eq 53 -and -not (Test-IsAdmin)) {
  Write-Error "Port 53 requires Administrator. Re-run elevated, or use -Port 5353 for lab."
}

New-Item -ItemType Directory -Force -Path $BinDir | Out-Null

if (-not (Test-Path $Exe)) {
  Write-Host "Downloading dnsproxy $DnsproxyVersion ..."
  $zipName = "dnsproxy-windows-amd64-$DnsproxyVersion.zip"
  $url = "https://github.com/AdguardTeam/dnsproxy/releases/download/$DnsproxyVersion/$zipName"
  $zip = Join-Path $BinDir "dnsproxy.zip"
  try {
    Invoke-WebRequest -Uri $url -OutFile $zip -UseBasicParsing
  } catch {
    Write-Error "Download failed ($url). Place dnsproxy.exe in $BinDir manually — https://github.com/AdguardTeam/dnsproxy/releases"
  }
  Expand-Archive -Path $zip -DestinationPath $BinDir -Force
  Remove-Item $zip -Force -ErrorAction SilentlyContinue
  $found = Get-ChildItem -Path $BinDir -Recurse -Filter "dnsproxy.exe" | Select-Object -First 1
  if (-not $found) { Write-Error "dnsproxy.exe not found after extract" }
  if ($found.FullName -ne $Exe) {
    Copy-Item $found.FullName $Exe -Force
  }
  Write-Host "OK dnsproxy -> $Exe"
}

$unc = Join-Path $Root "config\uncensor"
foreach ($f in @("hosts.critical", "hosts.local", "hosts.generated")) {
  $p = Join-Path $unc $f
  if (-not (Test-Path $p)) {
    if ($f -eq "hosts.local") {
      Set-Content -Path $p -Value "# manual pins`n" -Encoding utf8
    } else {
      Set-Content -Path $p -Value "# empty — run scripts\warm-local-cache.py / ooni-like-anti-lie.py`n" -Encoding utf8
    }
  }
}

$tplText = Get-Content -Path $Tpl -Raw -Encoding utf8
$yaml = $tplText `
  -replace '\{\{LISTEN_ADDR\}\}', $ListenAddr `
  -replace '\{\{LISTEN_PORT\}\}', "$Port" `
  -replace '\{\{HOSTS_CRITICAL\}\}', (($unc + "\hosts.critical") -replace '\\', '/') `
  -replace '\{\{HOSTS_LOCAL\}\}', (($unc + "\hosts.local") -replace '\\', '/') `
  -replace '\{\{HOSTS_GENERATED\}\}', (($unc + "\hosts.generated") -replace '\\', '/')
Set-Content -Path $RuntimeYaml -Value $yaml -Encoding utf8

# Firewall: Private profile only (never Public / Domain wide-open)
if (Test-IsAdmin) {
  $rule = "freebox-dns-dnsproxy-lan"
  Get-NetFirewallRule -DisplayName "$rule*" -ErrorAction SilentlyContinue | Remove-NetFirewallRule -ErrorAction SilentlyContinue
  try {
    New-NetFirewallRule -DisplayName $rule -Direction Inbound -Protocol UDP -LocalPort $Port `
      -LocalAddress $ListenAddr -Action Allow -Profile Private | Out-Null
    New-NetFirewallRule -DisplayName "$rule-tcp" -Direction Inbound -Protocol TCP -LocalPort $Port `
      -LocalAddress $ListenAddr -Action Allow -Profile Private | Out-Null
    Write-Host "Firewall: UDP/TCP $Port on $ListenAddr (Private profile only)"
  } catch {
    Write-Host "Firewall rule skipped: $($_.Exception.Message)"
  }
}

Write-Host ""
Write-Host "freebox-dns Windows lite — LAN ONLY"
Write-Host "  listen  ${ListenAddr}:${Port}"
Write-Host "  config  $RuntimeYaml"
Write-Host "  DNS1 on router/clients = $ListenAddr"
Write-Host "  Do NOT port-forward 53/853/443 on the router"
Write-Host "  Stop with Ctrl+C"
Write-Host ""

& $Exe -c $RuntimeYaml
