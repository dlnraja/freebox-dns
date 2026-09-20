# Runtime template for Windows-native dnsproxy (paths rewritten by Run-DnsResolver.ps1).
# Standalone: no Unbound, no Docker — hosts local-first then DoT catalogue.
---
bootstrap:
  - "9.9.9.10:53"
  - "194.242.2.2:53"
  - "94.140.14.140:53"

listen-addrs:
  - "{{LISTEN_ADDR}}"

listen-ports:
  - {{LISTEN_PORT}}

hosts-file-enabled: true
hosts-files:
  - "{{HOSTS_CRITICAL}}"
  - "{{HOSTS_LOCAL}}"
  - "{{HOSTS_GENERATED}}"

# DoT uncensoring (no local Unbound on Windows lite)
upstream:
  - "tls://dns.mullvad.net"
  - "tls://dns10.quad9.net"
  - "tls://dns-unfiltered.adguard.com"
  - "tls://open.dns0.eu"
  - "tls://dns.digitale-gesellschaft.ch"
  - "tls://anycast.uncensoreddns.org"
  - "tls://dot1.applied-privacy.net"
  - "tls://uncensored.freedns.controld.com"

fallback:
  - "9.9.9.10:53"
  - "194.242.2.2:53"
  - "94.140.14.140:53"

cache: true
cache-min-ttl: 60
cache-max-ttl: 86400
optimistic-cache: true
cache-optimistic: true

ratelimit: 0
verbose: false
