# Windows 11 DoH (Admin PowerShell) — libre personality
# Requires trusting certs/server.crt in "Trusted Root" for the LAN IP.
$doh = 'https://192.168.1.15:8453/dns-query'
Add-DnsClientDohServerAddress -ServerAddress '192.168.1.15' -DohTemplate $doh -AllowFallbackToUdp $true -AutoUpgrade $true
Set-DnsClientServerAddress -InterfaceAlias (Get-NetAdapter | ? Status -eq 'Up' | select -First 1 -ExpandProperty Name) -ServerAddresses '192.168.1.15'
# Secure personality template: https://192.168.1.15:8444/dns-query
