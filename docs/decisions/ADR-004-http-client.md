# ADR-004: curl_cffi for HTTP Client

## Status

Accepted

## Date

2024-07-18

## Context

The toolkit needs to fetch generator data from perchance.org. The site uses Cloudflare challenge protection that blocks standard HTTP clients (httpx, requests, aiohttp). Requests without browser-like TLS fingerprints and headers are rejected.

## Decision

Use `curl_cffi` with browser impersonation (`impersonate="chrome120"`). This library:
- Mimics Chrome's TLS fingerprint at the curl/FFI layer
- Sends realistic HTTP headers by default
- Handles Cloudflare's JavaScript challenges transparently
- Supports both sync and async interfaces

## Alternatives Considered

### httpx with custom headers
- Pros: Pure Python, async native
- Cons: Still blocked by Cloudflare — TLS fingerprint gives it away
- Rejected: Doesn't work

### playwright (headless browser)
- Pros: Full browser, will always work
- Cons: Heavy dependency (~400MB browser binary), slow startup
- Rejected: Too heavy for a CLI tool

### selenium
- Pros: Works with any site
- Cons: Even heavier than playwright, slower
- Rejected: Overkill

### cloudscraper
- Pros: Lightweight, Python-native
- Cons: Brittle, breaks when Cloudflare updates challenge
- Rejected: Maintenance concerns

## Consequences

- curl_cffi is a native extension (C/Rust FFI) — adds build complexity
- Browser impersonation may break if Cloudflare changes detection
- Requires libcurl on some platforms
- Significantly faster than headless browser approaches
