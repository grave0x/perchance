# ADR-004: curl_cffi for HTTP Client

**Status:** Accepted | **Date:** 2024-07-18

## Context
The toolkit fetches generator data from perchance.org. The site uses Cloudflare challenge protection blocking standard HTTP clients (httpx, requests, aiohttp).

## Decision
Use `curl_cffi` with browser impersonation (`impersonate="chrome120"`). Mimics Chrome's TLS fingerprint at the curl/FFI layer, sends realistic headers, handles Cloudflare challenges.

## Alternatives Considered
- **httpx**: Blocked by Cloudflare TLS fingerprint
- **playwright**: Heavy (~400MB), slow startup
- **cloudscraper**: Brittle, breaks on Cloudflare updates

## Consequences
- Native extension (C/Rust FFI) — adds build complexity
- May break if Cloudflare changes detection
- Significantly faster than headless browser approaches