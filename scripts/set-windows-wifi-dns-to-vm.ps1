# Point this Windows Wi-Fi client at Freebox VM DNS (run PowerShell as Administrator).
# Production path for ALL devices: Freebox OS -> DHCP -> DNS1=9.9.9.10 DNS2=<VM_IP>
# This script only fixes ONE PC until Freebox DHCP is updated.

param(
  [string]$Interface = "WiFi 2",
  [string]$Sos = "9.9.9.10",
  [string]$VmDns = "192.168.1.71"
)

$ErrorActionPreference = "Stop"
Write-Host "Setting $Interface DNS -> $Sos (SOS), $VmDns (Freebox VM)"
Set-DnsClientServerAddress -InterfaceAlias $Interface -ServerAddresses @($Sos, $VmDns)
Clear-DnsClientCache
Get-DnsClientServerAddress -InterfaceAlias $Interface -AddressFamily IPv4 | Format-List
Write-Host "Verify: dig @$VmDns example.com   (or Resolve-DnsName example.com -Server $VmDns)"
Write-Host "Then set the same pair in Freebox OS DHCP so phones/TVs follow too."
