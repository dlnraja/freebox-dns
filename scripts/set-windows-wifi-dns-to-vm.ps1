# Point this Windows Wi-Fi client at your LAN DNS resolver (Admin).
# Prefer setting the same pair on the router DHCP so phones/TVs follow.
# DNS1 = resolver (Pi / VM / this Windows host) · DNS2 = SOS Quad9

param(
  [string]$Interface = "Wi-Fi",
  [string]$ResolverDns = "192.168.1.71",
  [string]$Sos = "9.9.9.10",
  # Legacy alias
  [Alias("VmDns")]
  [string]$VmDns = ""
)

$ErrorActionPreference = "Stop"
if ($VmDns) { $ResolverDns = $VmDns }

Write-Host "Setting $Interface DNS -> $ResolverDns (DNS1 resolver), $Sos (DNS2 SOS)"
Set-DnsClientServerAddress -InterfaceAlias $Interface -ServerAddresses @($ResolverDns, $Sos)
Clear-DnsClientCache
Get-DnsClientServerAddress -InterfaceAlias $Interface -AddressFamily IPv4 | Format-List
Write-Host "Verify: Resolve-DnsName example.com -Server $ResolverDns"
Write-Host "For the whole LAN: set the same pair on the router DHCP (docs/wifi-lan.md)."
