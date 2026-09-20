# Windows 11 DoH (Admin PowerShell) — uncensored by default
$doh = 'https://192.168.1.71:8453/dns-query'
Add-DnsClientDohServerAddress -ServerAddress '192.168.1.71' -DohTemplate $doh -AllowFallbackToUdp $true -AutoUpgrade $true
# Other modes: malware=https://192.168.1.71:8445/dns-query antipub=https://192.168.1.71:8446/dns-query secure=https://192.168.1.71:8444/dns-query
