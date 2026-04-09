# Kairos Agent

Kairos Agent is a macOS menubar app that syncs your Tiger Brokers trades to the Kairos portal automatically. Once set up, it runs silently in the background and keeps your trading journal up to date.

---

## What It Does

- Connects to your Tiger Brokers account using your API credentials
- Fetches your trade history and classifies option strategies (Iron Condor, Bull Put Spread, etc.)
- Uploads encrypted analytics to your private Kairos portal profile
- Auto-syncs once daily at 4:30 PM on weekdays
- Lives in your macOS menubar — no windows, no Dock icon

---

## Requirements

- macOS 12 (Monterey) or later
- Apple Silicon or Intel Mac
- A Tiger Brokers account with API access enabled
- A Kairos portal account

---

## Installation

### Step 1 — Download

Download the latest release:

**[Kairos-1.0.0.dmg](https://github.com/etherhtun/kairos-agent/releases/download/v1.0.0/Kairos-1.0.0.dmg)**

### Step 2 — Install

1. Open the `.dmg` file
2. Drag **Kairos** into your **Applications** folder
3. Eject the disk image

### Step 3 — First Launch (Gatekeeper)

Because Kairos is not yet signed with an Apple Developer certificate, macOS will block it on first open.

To allow it:

**Option A (recommended):**
1. Open **System Settings** → **Privacy & Security**
2. Scroll down to the Security section
3. Click **Open Anyway** next to the Kairos message

**Option B:**
1. Right-click **Kairos** in Finder
2. Select **Open**
3. Click **Open** in the dialog that appears

### Step 4 — Setup Wizard

On first launch, a setup wizard will appear automatically:

1. **Upload token** — get this from [kairos-f3w.pages.dev/connect](https://kairos-f3w.pages.dev/connect) after logging in
2. **Tiger config file** — download `tiger_openapi_config.properties` from Tiger app → **API Management → Download Config**

Kairos stores both locally on your Mac only. Nothing is uploaded to any server except your anonymised trade analytics.

---

## Usage

Kairos appears as `Kairos` in your menubar.

| Menu Item | Description |
|-----------|-------------|
| Last sync | Shows when data was last synced |
| Sync now | Manually trigger a sync |
| Auto-sync at 4:30 PM | Toggle daily auto-sync on/off |
| Open portal | Open the Kairos dashboard in your browser |
| View logs | Open sync log file |
| Setup / reconfigure | Re-run the setup wizard |
| Quit | Exit the app |

---

## Privacy & Data

- **Tiger credentials** are stored locally at `~/.kairos-agent/tiger_openapi_config.properties` and never leave your Mac
- **Your upload token** is stored locally at `~/.kairos-agent/credentials.json`
- **Trade data** (`~/.kairos-agent/data.json`) is uploaded to your private profile slot on Cloudflare R2 — accessible only to you
- **No personal information** beyond your trade history is collected or stored on any server
- Sync logs are stored locally at `~/.kairos-agent/logs/sync.log`

---

## Disclaimer

> Kairos is a personal trading journal tool. It does not provide financial advice, investment recommendations, or trading signals. All data displayed is for informational and record-keeping purposes only.
>
> By using Kairos Agent, you acknowledge that you are solely responsible for your trading decisions. Past performance shown in the portal does not guarantee future results.
>
> Kairos is not affiliated with Tiger Brokers, Webull, or any other brokerage.

---

## Troubleshooting

**Setup wizard does not appear**
- Quit and reopen the app
- If `~/.kairos-agent/state.json` exists, delete it and relaunch

**Sync fails with "Tiger ID empty" or connection error**
- Re-run Setup / reconfigure and re-select your `tiger_openapi_config.properties` file
- Ensure API access is enabled in Tiger app → API Management

**Upload fails with 401 Unauthorized**
- Your upload token may have changed — go to the portal `/connect` page and copy the current token, then re-run Setup

**Portal shows "No data yet"**
- Run a manual sync from the menubar
- Check logs via View logs

---

## Building from Source

```bash
git clone https://github.com/etherhtun/kairos-agent.git
cd kairos-agent
pip install rumps pyinstaller
pip install -r sync/requirements.txt
pyinstaller kairos.spec --noconfirm
# Output: dist/Kairos.app
```

---

## License

MIT — see [LICENSE](LICENSE)
