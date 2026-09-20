# Windows 11 DoH (Admin PowerShell) — uncensored by default
$doh = 'https://192.168.1.15:8453/dns-query'
Add-DnsClientDohServerAddress -ServerAddress '192.168.1.15' -DohTemplate $doh -AllowFallbackToUdp $true -AutoUpgrade $true
# Other modes: malware=https://192.168.1.15:8445/dns-query antipub=https://192.168.1.15:8446/dns-query secure=https://192.168.1.15:8444/dns-query
