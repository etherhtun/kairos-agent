# Kairos — System Design & Admin Guide

This document covers the full architecture, infrastructure setup, and release process for Kairos.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                  USER'S MAC                         │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │  Kairos.app (menubar)                       │   │
│  │  app.py → jobs/upload_sync.py               │   │
│  │                                             │   │
│  │  sync/sync.py ──► classifier.py             │   │
│  │       │                                     │   │
│  │  brokers/tiger.py ◄── tiger_openapi_        │   │
│  │       │               config.properties     │   │
│  │       ▼                                     │   │
│  │  ~/.kairos-agent/data.json                  │   │
│  └───────────────┬─────────────────────────────┘   │
│                  │ POST /api/upload                 │
│                  │ Bearer {upload_token}            │
└──────────────────┼──────────────────────────────────┘
                   │
          ┌────────▼────────────────────────────┐
          │     Cloudflare Pages + Workers       │
          │                                     │
          │  /api/upload (bypass CF Access)      │
          │       │                             │
          │       ▼                             │
          │  KV: token:{uuid} → {sub, email}    │
          │       │                             │
          │       ▼                             │
          │  R2: profiles/{sub}/data.json       │
          │       │                             │
          │  /api/trades (CF Zero Trust auth)   │
          │       │                             │
          └───────┼─────────────────────────────┘
                  │
         ┌────────▼──────────────┐
         │   Browser (portal)    │
         │   kairos-f3w.pages.dev│
         └───────────────────────┘
```

---

## Components

### 1. Kairos Agent (macOS App)

| File | Purpose |
|------|---------|
| `app.py` | Menubar app, state management, auto-sync timer |
| `jobs/setup.py` | GUI setup wizard (token + Tiger config) |
| `jobs/upload_sync.py` | Sync orchestration, upload to R2 |
| `jobs/creds.py` | Local credential store (`~/.kairos-agent/`) |
| `sync/sync.py` | Trade fetch, merge, analytics generation |
| `sync/classifier.py` | Options strategy classification |
| `sync/brokers/tiger.py` | Tiger Brokers API client |
| `kairos.spec` | PyInstaller build config |

**Key design decisions:**
- Sync runs **in-process** (not subprocess) to avoid spawning a second menubar icon
- `BUNDLE_VERSION` in `upload_sync.py` triggers force-update of `~/.kairos-agent/sync/` on app update
- No `keyring` dependency — credentials stored in plain JSON with `chmod 600`
- Tiger credentials parsed manually from `.properties` file (TigerOpenClientConfig API does not support `config_file_path`)

### 2. Cloudflare Pages (Portal + API)

| Endpoint | Auth | Purpose |
|----------|------|---------|
| `GET /api/setup-token` | CF Zero Trust JWT | Generate/return upload token for logged-in user |
| `POST /api/upload` | Bearer token (KV) | Receive `data.json` from agent, write to R2 |
| `GET /api/trades` | CF Zero Trust JWT | Return user's `data.json` from R2 |
| `GET /api/prices` | None | Live market data + technical indicators |
| `GET /api/history` | None | OHLC data from Yahoo Finance |

### 3. Cloudflare Infrastructure

| Resource | Name / ID | Purpose |
|----------|-----------|---------|
| R2 Bucket | `kairos-profiles` | Per-user `data.json` storage |
| KV Namespace | `TOKENS` (`755904cd9183434bbd6acfa45933dc11`) | Token ↔ sub mapping |
| CF Access App | Kairos Portal | Protects all portal routes |
| CF Access Policy | Bypass `/api/upload` | Allows agent to upload without browser cookie |

---

## Data Flow

### First-Time Setup
1. User logs into portal (CF Zero Trust)
2. `GET /api/setup-token` — decodes JWT `sub`, generates UUID token, stores in KV:
   - `token:{uuid}` → `{ sub, email, created }`
   - `profile:{sub}` → `{ token, email, created }`
3. User copies token into Kairos Agent setup wizard
4. Token saved to `~/.kairos-agent/credentials.json`

### Sync & Upload
1. Agent loads Tiger credentials from `~/.kairos-agent/tiger_openapi_config.properties`
2. Fetches trade history (incremental: last 30 days; first run: 3 years)
3. Classifies strategies, rebuilds analytics
4. Writes `~/.kairos-agent/data.json`
5. `POST /api/upload` with `Authorization: Bearer {token}`
6. Worker validates token via KV, writes to `R2: profiles/{sub}/data.json`

### Portal Data Load
1. User browser makes `GET /api/trades`
2. Worker decodes CF Access JWT → gets `sub`
3. Reads `R2: profiles/{sub}/data.json` → returns to browser

---

## Cloudflare Setup (from scratch)

### Prerequisites
- Cloudflare account with Pages project (`kairos-f3w`)
- R2 enabled on your account

### Step 1 — R2 Bucket
```
Cloudflare Dashboard → R2 → Create bucket → kairos-profiles
```

### Step 2 — KV Namespace
```
Workers & Pages → KV → Create namespace → TOKENS
```
Copy the KV namespace ID into `wrangler.toml`.

### Step 3 — wrangler.toml
```toml
name = "kairos"
pages_build_output_dir = "."

[[r2_buckets]]
binding = "PROFILES"
bucket_name = "kairos-profiles"

[[kv_namespaces]]
binding = "TOKENS"
id = "755904cd9183434bbd6acfa45933dc11"
```

### Step 4 — Bind Resources to Pages Project
```
Workers & Pages → kairos-f3w → Settings → Functions
→ R2 bucket bindings: PROFILES → kairos-profiles
→ KV namespace bindings: TOKENS → TOKENS
```

### Step 5 — CF Zero Trust (Access)
```
Zero Trust → Access → Applications → Add application → Self-hosted
  Name: Kairos Portal
  Domain: kairos-f3w.pages.dev
  Policy: Allow (your email or Google auth)

Add bypass policy:
  Action: Bypass
  Path: /api/upload
  (allows agent to POST without browser session)
```

---

## Local Development

```bash
# Portal (CF Pages dev server)
cd kairos/
npx wrangler pages dev . --r2=PROFILES --kv=TOKENS

# Agent (run directly)
cd kairos-agent/
pip install rumps tigeropen pandas python-dotenv
python3 app.py
```

---

## Building a New Release

### 1. Update version
In `jobs/upload_sync.py`, bump `BUNDLE_VERSION`:
```python
BUNDLE_VERSION = '1.5'  # increment each release
```

In `kairos.spec`, update `CFBundleShortVersionString`:
```python
'CFBundleShortVersionString': '1.1.0',
```

### 2. Build the app
```bash
cd kairos-agent/
python3 -m PyInstaller kairos.spec --noconfirm
```

### 3. Create the DMG
```bash
hdiutil create \
  -volname "Kairos Agent" \
  -srcfolder dist/Kairos.app \
  -ov -format UDZO \
  dist/Kairos-1.1.0.dmg
```

### 4. Publish GitHub Release
1. Go to `https://github.com/etherhtun/kairos-agent/releases/new`
2. Tag: `v1.1.0`, Title: `Kairos Agent v1.1.0`
3. Upload `dist/Kairos-1.1.0.dmg`
4. Publish

### 5. Update download link
In `kairos/connect.html`, update the DMG URL:
```html
<a href="https://github.com/etherhtun/kairos-agent/releases/download/v1.1.0/Kairos-1.1.0.dmg">
```

Commit and push to trigger CF Pages deploy.

---

## User Profile Management

User profiles are stored in R2 under `profiles/{sub}/data.json` where `sub` is the CF Access JWT subject (unique per Google account).

### View all profiles
```
Cloudflare Dashboard → R2 → kairos-profiles → Browse
```

### Delete a user's data
```
R2 → kairos-profiles → profiles/{sub}/data.json → Delete
```

### Revoke a user's token
```
Workers & Pages → KV → TOKENS
→ Delete key: token:{uuid}
→ Delete key: profile:{sub}
```

The user will need to re-run Setup from the portal `/connect` page to get a new token.

---

## Security Notes

- Upload tokens are UUIDs — unguessable, 1 per user
- Tiger credentials never leave the user's Mac
- R2 data is isolated per user by `sub` — users cannot access each other's data
- CF Zero Trust enforces authentication on all portal routes
- The `/api/upload` bypass is scoped only to that path — portal pages remain protected

---

## Logs & Debugging

Agent sync logs: `~/.kairos-agent/logs/sync.log`

Common error codes returned by `run_sync()`:

| Code | Step | Meaning |
|------|------|---------|
| -2 | sync | Sync threw an exception (see tail) |
| -3 | upload | `data.json` missing after sync |
| -4 | upload | `upload_token` not set |
| -5 | upload_failed | HTTP error from `/api/upload` |
