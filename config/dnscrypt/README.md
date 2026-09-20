# DNSCrypt in freebox-dns

Two complementary pieces (DHCP SOS untouched — still `9.9.9.10` + VM `:53`):

| Service | Role | Port |
| --- | --- | --- |
| **`dnscrypt-proxy`** | Client: LAN plain → **DNSCrypt → Quad9 nofilter** (`.10`) | `${DNSCRYPT_PROXY_PORT:-5359}` |
| **`dnscrypt-libre`** | Server: LAN **DNSCrypt protocol** → dns-libre → Unbound | `${DNSCRYPT_LIBRE_PORT:-8443}` |

Config proxy : `config/dnscrypt/proxy/dnscrypt-proxy.toml`

## Quick start

```bash
# 1) Always-on DNSCrypt *upstream* path (no key ceremony)
docker compose up -d dnscrypt-proxy
dig @${HOST_IP} -p 5359 example.com +short

# 2) Optional LAN DNSCrypt *server* (sdns:// for Nebulo / dnscrypt-proxy clients)
bash scripts/dnscrypt-server-init.sh
docker compose up -d dnscrypt-libre
cat config/clients/generated/dnscrypt-stamp.txt
```

## Client stamp (after init)

Paste `sdns://…` into:
- [dnscrypt-proxy](https://github.com/DNSCrypt/dnscrypt-proxy) `[static]`
- Nebulo / RethinkDNS / compatible apps

## Quad9 official stamps (nofilter = SOS spirit)

See `quad9-nofilter.stamps` and [quad9-resolvers.md](https://quad9.net/dnscrypt/quad9-resolvers.md).

**Never** put DNSCrypt Quad9 Secure (`.9`) in DHCP — filtering stays local on `dns-secure`.
