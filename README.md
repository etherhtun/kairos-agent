# Kairos Agent

Kairos Agent is a menubar app for macOS and Windows that syncs your Tiger Brokers trades to the [Kairos portal](https://kairos-f3w.pages.dev) automatically. Once configured, it runs silently in the background and keeps your trading journal up to date.

---

## What It Does

- Connects to Tiger Brokers using your local API credentials
- Fetches trade history and classifies option strategies (Iron Condor, Bull Put Spread, etc.)
- Uploads analytics to your private Kairos portal profile
- Auto-syncs once daily at 4:30 PM on weekdays
- Lives in the menubar (macOS) or system tray (Windows) — no Dock icon, no windows

---

## Requirements

| Platform | Requirement |
|----------|-------------|
| macOS    | macOS 12 (Monterey) or later, Apple Silicon or Intel |
| Windows  | Windows 10 or Windows 11 (64-bit) |
| Both     | Tiger Brokers account with API access enabled |
| Both     | Kairos portal account (`kairos-f3w.pages.dev`) |

---

## Installation

### Step 1 — Download

Go to the [Connect page](https://kairos-f3w.pages.dev/connect-tiger) and download the app for your platform:

| Platform | File |
|----------|------|
| macOS    | `Kairos-v1.1.1-mac.dmg` |
| Windows  | `Kairos-v1.1.1-windows.zip` |

Or download directly from [GitHub Releases](https://github.com/etherhtun/kairos-agent/releases/latest).

---

### macOS Setup

1. Open the `.dmg` file
2. Drag **Kairos** into your **Applications** folder
3. Eject the disk image

**First launch — Gatekeeper bypass:**

Because Kairos is not yet signed with an Apple Developer certificate, macOS will block it on first open.

**Option A:**
1. Open **System Settings** → **Privacy & Security**
2. Scroll to Security section → click **Open Anyway**

**Option B:**
1. Right-click **Kairos** in Finder → **Open** → **Open**

---

### Windows Setup

1. Extract `Kairos-v1.1.1-windows.zip`
2. Move the `Kairos` folder to `C:\Program Files\Kairos` (or anywhere you prefer)
3. Run `Kairos.exe` inside the folder
4. **Windows Defender SmartScreen** may show a warning — click **More info → Run anyway**

To start Kairos automatically on login: right-click `Kairos.exe` → **Create shortcut** → move shortcut to:
```
C:\Users\<you>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
```

---

### Step 2 — Setup Wizard

On first launch, the setup wizard appears automatically:

**Step 1 — Upload token**
Get your token from [kairos-f3w.pages.dev/connect-tiger](https://kairos-f3w.pages.dev/connect-tiger) after logging in. Paste it into the wizard.

**Step 2 — Tiger config file**
Download `tiger_openapi_config.properties` from Tiger app → **API Management → Download Config**. Select the file when prompted.

Kairos stores both credentials locally only. Nothing is uploaded except your anonymised trade analytics.

---

## Usage

| Menu Item | Description |
|-----------|-------------|
| Last sync | Shows time of last successful sync |
| Sync now | Manually trigger a sync |
| Auto-sync at 4:30 PM | Toggle daily auto-sync on/off |
| Open portal | Open Kairos dashboard in browser |
| View logs | Open sync log file |
| Setup / reconfigure | Re-run setup wizard |
| Quit | Exit the app |

---

## Privacy & Data

| Data | Where it lives |
|------|---------------|
| Tiger API credentials | Local only — `~/.kairos-agent/tiger_openapi_config.properties` |
| Upload token | Local only — `~/.kairos-agent/credentials.json` |
| Trade analytics | Uploaded to your private R2 profile slot — accessible only to you |
| Sync logs | Local only — `~/.kairos-agent/logs/sync.log` |

Credentials are stored with restricted permissions (`chmod 600`). No broker keys are ever transmitted to any server.

---

## Disclaimer

> Kairos is a personal trading journal tool. It does not provide financial advice, investment recommendations, or trading signals. All data is for informational and record-keeping purposes only.
>
> You are solely responsible for your trading decisions. Past performance shown in the portal does not guarantee future results.
>
> Kairos is not affiliated with Tiger Brokers, Webull, MooMoo, or any other brokerage.

---

## Troubleshooting

**Setup wizard does not appear on first launch**
- Quit and reopen the app
- Delete `~/.kairos-agent/state.json` and relaunch

**Tiger connection error / Tiger ID empty**
- Re-run Setup and re-select your `tiger_openapi_config.properties` file
- Ensure API access is enabled in Tiger app → API Management

**Upload fails with 401 Unauthorized**
- Your token may have changed — visit `/connect-tiger` on the portal and copy the current token, then re-run Setup

**Portal shows "No data yet" after sync**
- Check **View logs** for errors
- Confirm the upload token in the wizard matches the one on the portal

**macOS: app blocked by Gatekeeper**
- See [macOS Setup → First launch](#macos-setup) above

**Windows: app blocked by Defender SmartScreen**
- Click **More info → Run anyway**

---

## Building from Source

```bash
git clone https://github.com/etherhtun/kairos-agent.git
cd kairos-agent

# macOS
pip install rumps pyinstaller
pip install -r sync/requirements.txt
python -m PyInstaller kairos.spec --noconfirm

# Windows
pip install pystray pillow plyer pyinstaller
pip install -r sync/requirements.txt
python -m PyInstaller kairos_win.spec --noconfirm
```

Automated builds run via [GitHub Actions](.github/workflows/release.yml) on every version tag.

---

## License

MIT — see [LICENSE](LICENSE)
