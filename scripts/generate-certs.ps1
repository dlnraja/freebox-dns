# Generate self-signed TLS certs for local DoH (LAN only).
# Usage: powershell -File scripts\generate-certs.ps1
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$CertDir = Join-Path $Root "certs"
New-Item -ItemType Directory -Force -Path $CertDir | Out-Null
$Crt = Join-Path $CertDir "server.crt"
$Key = Join-Path $CertDir "server.key"
$Cn = if ($env:DOH_CN) { $env:DOH_CN } else { "freebox-dns.local" }

if ((Test-Path $Crt) -and (Test-Path $Key)) {
  Write-Host "Certs already exist in $CertDir — skip (delete to regenerate)."
  exit 0
}

$openssl = Get-Command openssl -ErrorAction SilentlyContinue
if (-not $openssl) {
  Write-Host "openssl not found — trying Windows certificate export fallback..."
  $cert = New-SelfSignedCertificate -DnsName $Cn, "localhost" -CertStoreLocation "Cert:\CurrentUser\My" -NotAfter (Get-Date).AddYears(2) -KeyExportPolicy Exportable
  $pwd = ConvertTo-SecureString -String "freebox-dns" -Force -AsPlainText
  $pfx = Join-Path $CertDir "server.pfx"
  Export-PfxCertificate -Cert $cert -FilePath $pfx -Password $pwd | Out-Null
  # Prefer openssl if later installed; for now write PEM via .NET if possible
  Write-Host "Created PFX at $pfx. Install OpenSSL and re-run for PEM, or mount PFX-compatible tooling."
  Write-Host "Tip (WSL): wsl openssl req -x509 ..."
  exit 0
}

& openssl req -x509 -newkey rsa:2048 -sha256 -days 825 -nodes `
  -keyout $Key -out $Crt `
  -subj "/CN=$Cn/O=freebox-dns/OU=LAN" `
  -addext "subjectAltName=DNS:$Cn,DNS:localhost,IP:127.0.0.1"

Write-Host "Wrote $Crt and $Key"
