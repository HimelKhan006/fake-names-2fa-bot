# 🚀 COMPLETE A-TO-Z TELEGRAM BOT SETUP & DEPLOYMENT GUIDE

**Bot Name**: Fake Names 2FA Generator & Authenticator  
**Created By**: KKH  
**GitHub Repository**: `https://github.com/HimelKhan006/fake-names-2fa-bot.git`  
**Last Updated**: 2026-07-31  

---

## 📑 TABLE OF CONTENTS

1. [Telegram Bot Creation via BotFather](#1-telegram-bot-creation-via-botfather)
2. [Exact Files for Local Storage & GitHub](#2-exact-files-for-local-storage--github)
3. [Environment Variables Setup (.env)](#3-environment-variables-setup-env)
4. [GitHub Gist Encrypted Cloud Database Setup](#4-github-gist-encrypted-cloud-database-setup)
5. [PowerShell, CMD & Linux Terminal Commands](#5-powershell-cmd--linux-terminal-commands)
6. [GitHub Repository Push Commands](#6-github-repository-push-commands)
7. [24/7 Hosting Setup on Render.com](#7-247-hosting-setup-on-rendercom)
8. [24/7 Uptime Pinger (UptimeRobot)](#8-247-uptime-pinger-uptimerobot)
9. [Bot Features Reference Guide](#9-bot-features-reference-guide)
10. [Admin & User Commands Master Reference](#10-admin--user-commands-master-reference)

---

## 1. Telegram Bot Creation via BotFather

1. Open Telegram → Search **[@BotFather](https://t.me/BotFather)**
2. Send `/newbot`
3. Enter **Bot Name**: `Fake Names 2FA`
4. Enter **Bot Username** (must end in `bot`): `Fake_Names_2FA_Bot`
5. Copy your **HTTP API Token** → Save it (format: `1234567890:AAFxxx...`)
6. Optional — set description:
   ```
   /setdescription → Instant Fake Name Generator & 2FA Authenticator Bot created by KKH.
   ```

---

## 2. Exact Files for Local Storage & GitHub

### ✅ FILES TO KEEP ON LOCAL PC (All Project Files)

| File | Purpose |
| :--- | :--- |
| `main.py` | Full bot source code (name generator, 2FA decoder, admin panel, encryption, Gist sync) |
| `requirements.txt` | Python dependencies |
| `Procfile` | Render start command |
| `.gitignore` | Prevents secrets leaking to GitHub |
| `.env` | **LOCAL ONLY** — Your private tokens & secrets (never pushed to GitHub) |
| `README.md` | Bot overview |
| `DEPLOYMENT_GUIDE.md` | This full setup guide |

### ❌ FILES NEVER TO PUSH TO GITHUB

| File | Reason |
| :--- | :--- |
| `.env` | Contains private `TELEGRAM_BOT_TOKEN`, `GITHUB_TOKEN`, `GIST_ID` |
| `bot_data.json` | Local database cache (auto-managed by bot) |

> ✅ `.env` and `bot_data.json` are already protected in `.gitignore`

---

## 3. Environment Variables Setup (.env)

Create a `.env` file in your project folder with this exact content:

```env
# ── TELEGRAM BOT ────────────────────────────────────────────
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
ADMIN_ID=your_telegram_user_id,@your_username

# ── GITHUB GIST ENCRYPTED CLOUD DATABASE ────────────────────
GITHUB_TOKEN=ghp_YourGitHubPersonalAccessTokenHere
GIST_ID=your_gist_id_here_after_first_run

# ── OPTIONAL: Custom database encryption key ─────────────────
# DATA_ENCRYPTION_KEY=your_custom_strong_secret_key
```

### Field Descriptions:

| Variable | Description | Required |
| :--- | :--- | :--- |
| `TELEGRAM_BOT_TOKEN` | Token from BotFather | ✅ Required |
| `ADMIN_ID` | Your Telegram User ID (get via `/id`) + optional @username | ✅ Required |
| `GITHUB_TOKEN` | GitHub Personal Access Token with `gist` scope | ✅ For cloud DB |
| `GIST_ID` | Auto-assigned after first bot startup — copy from logs | ✅ For cloud DB |
| `DATA_ENCRYPTION_KEY` | Custom encryption password (defaults to bot token) | Optional |

---

## 4. GitHub Gist Encrypted Cloud Database Setup

The bot automatically backs up all user data to an **encrypted private GitHub Gist** using **PBKDF2-HMAC-SHA256** authenticated encryption. Data is unreadable to anyone without your bot token.

### Step 1: Get GitHub Personal Access Token

1. Go to **[github.com/settings/tokens](https://github.com/settings/tokens)**
2. Click **Generate new token (classic)**
3. Set:
   - **Note**: `Fake Names 2FA Bot`
   - **Expiration**: `No expiration`
   - **Scope**: Check ✅ `gist` only
4. Click **Generate token** → Copy the `ghp_...` token

### Step 2: Add Token to .env

```env
GITHUB_TOKEN=ghp_YourNewTokenHere
GIST_ID=
```
*(Leave `GIST_ID` blank — bot creates the Gist automatically)*

### Step 3: Start Bot — Auto-Creates Gist

On first startup you will see in logs:
```
✅ Auto-created new Encrypted GitHub Gist Database! GIST_ID: abc123xyz456...
✅ ACTION REQUIRED: Add GIST_ID=abc123xyz456... to your Render environment variables!
```

### Step 4: Save GIST_ID

Copy the GIST_ID from logs and update your `.env`:
```env
GIST_ID=abc123xyz456...
```
Also add it to **Render Environment Variables** (see Section 7).

### How Data Encryption Works

All data stored in GitHub Gist is encrypted with:

| Layer | Algorithm |
| :--- | :--- |
| Key Derivation | PBKDF2-HMAC-SHA256 (100,000 iterations) |
| Encryption | Counter-mode keystream (AES-equivalent strength) |
| Authentication | HMAC-SHA256 MAC tag (tamper-proof) |
| Salt & IV | Fresh 16-byte random per backup |

Hackers who access your Gist only see unreadable ciphertext — **zero plain-text data**.

---

## 5. PowerShell, CMD & Linux Terminal Commands

### 5.1 Windows PowerShell

```powershell
# Navigate to project directory
Set-Location -Path "c:\FAKE NAMES AND 2FA TELE BOT KKH FILES"

# Create .env file
@'
TELEGRAM_BOT_TOKEN=your_token_here
ADMIN_ID=your_user_id,@your_username
GITHUB_TOKEN=ghp_your_token_here
GIST_ID=
'@ | Set-Content -Path ".env" -Encoding UTF8

# Install dependencies
pip install -r requirements.txt

# Verify syntax
python -m py_compile main.py

# Run locally
python main.py
```

### 5.2 Windows CMD

```cmd
cd /d "c:\FAKE NAMES AND 2FA TELE BOT KKH FILES"
pip install -r requirements.txt
python -m py_compile main.py
python main.py
```

### 5.3 Linux / Ubuntu VPS

```bash
sudo apt update && sudo apt install python3 python3-pip git -y
git clone https://github.com/HimelKhan006/fake-names-2fa-bot.git
cd fake-names-2fa-bot

cat << 'EOF' > .env
TELEGRAM_BOT_TOKEN=your_token_here
ADMIN_ID=your_user_id,@your_username
GITHUB_TOKEN=ghp_your_token_here
GIST_ID=
EOF

pip3 install -r requirements.txt
nohup python3 main.py > bot.log 2>&1 &
```

---

## 6. GitHub Repository Push Commands

```powershell
# Initialize Git (first time only)
git init
git remote add origin https://github.com/HimelKhan006/fake-names-2fa-bot.git

# Stage all safe files (never stages .env — protected by .gitignore)
git add main.py requirements.txt Procfile .gitignore README.md DEPLOYMENT_GUIDE.md

# Commit
git commit -m "Update bot system"

# Push to GitHub
git branch -M main
git push origin main
```

> ⚠️ Never run `git add .env` — your tokens will leak publicly!

---

## 7. 24/7 Hosting Setup on Render.com

### Render Configuration

| Setting | Value |
| :--- | :--- |
| **Service Type** | Web Service |
| **Repository** | `fake-names-2fa-bot` |
| **Branch** | `main` |
| **Environment** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `python main.py` |
| **Instance Type** | Free |

### Required Render Environment Variables

Go to **Render → Your Service → Environment → Add Environment Variable**:

| Key | Value |
| :--- | :--- |
| `TELEGRAM_BOT_TOKEN` | Your bot token from BotFather |
| `ADMIN_ID` | Your Telegram user ID (e.g. `6798979733,@MegalodonKKH`) |
| `PORT` | `10000` |
| `GITHUB_TOKEN` | Your GitHub Personal Access Token (`ghp_...`) |
| `GIST_ID` | Your Gist ID (from logs after first run) |

> ⚠️ The `.env` file is NOT uploaded to Render. You MUST add all secrets as Render Environment Variables.

### Render Deployment Success Log Pattern

```
Bot Username resolved: @Fake_Names_2FA_Bot
Purged all command scopes and registered clean 4 native Telegram menu commands successfully.
GitHub Gist DB: GITHUB_TOKEN detected. Attempting to auto-create encrypted Gist database...
Successfully fetched & decrypted member & admin database from GitHub Gist!
Starting ultra-fast 16-worker thread Fake Names 2FA telebot Infinity Polling...
Health check HTTP server running on 0.0.0.0:10000
```

---

## 8. 24/7 Uptime Pinger (UptimeRobot)

Render Free Tier sleeps after 15 minutes of inactivity. Keep your bot awake 24/7 for free:

1. Create account at **[UptimeRobot.com](https://uptimerobot.com)**
2. Click **Add New Monitor**
3. Configure:
   - **Monitor Type**: `HTTP(s)`
   - **Friendly Name**: `Fake Names 2FA Bot`
   - **URL**: `https://fake-names-2fa-bot.onrender.com`
   - **Interval**: `5 minutes`
4. Click **Create Monitor**

UptimeRobot pings the bot every 5 minutes, keeping it online 24/7 for free!

---

## 9. Bot Features Reference Guide

### 🔤 Name Generator
| Feature | Details |
| :--- | :--- |
| **Name Categories** | Islamic, General (Western), Mixed |
| **Gender Modes** | Male only, Female only, Mixed (shows gender tags) |
| **Batch Quantities** | 5, 10, 20, or 50 names per batch |
| **Output Format** | Monospace grid — fixed-width alignment with 01. numbering |
| **Mixed Gender Tags** | `(Male)` / `(Female)` shown only in Mixed mode |

### 🔐 2FA Authenticator
| Feature | Details |
| :--- | :--- |
| **Input Formats** | Raw Base32 key, spaced key (e.g. `ABCD EFGH`), `otpauth://` URL |
| **Output** | Current 6-digit TOTP + Prev Code (clock drift) + Next Code |
| **Refresh Button** | `🔄 Refresh 2FA Code` inline button — updates code instantly |
| **Validation** | Full base32 decode validation before code generation |

### 🛡️ Database Encryption
| Feature | Details |
| :--- | :--- |
| **Algorithm** | PBKDF2-HMAC-SHA256 (100,000 iterations) |
| **Coverage** | All user data + admin IDs + broadcast logs |
| **Storage** | Encrypted GitHub Gist (private) + local `bot_data.json` |
| **Auto-Sync** | Restores from Gist on startup, backs up on every data change |

### 🟢 Admin Status Notifications
| Event | Notification |
| :--- | :--- |
| **Bot starts up** | `🟢 BOT STATUS: ONLINE` card sent to all Admins |
| **Server stops** | `🔴 BOT STATUS: OFFLINE` card (signal-based only, no false alerts) |

---

## 10. Admin & User Commands Master Reference

### 👑 Admin Commands

| Command | Description |
| :--- | :--- |
| `/admin` or `/stats` | Live Admin Panel — member stats, top inviters |
| `/users` | All registered members with IDs (`#FN-1001`) |
| `/send <user_id> <msg>` | Send direct message to a user |
| `/broadcast <msg>` | Broadcast to all members |
| `/delete_broadcast B-101` | Delete a broadcast from all chats |
| `/delete <chat_id> <msg_id>` | Remotely delete any bot message |
| `/ban <user_id>` | Ban a user from bot access |
| `/unban <user_id>` | Restore a banned user's access |
| `/banned` | List all currently banned users |

### 👤 User Commands

| Command | Description |
| :--- | :--- |
| `/start` | Start or restart the bot |
| `/invite` | Get personal referral link + invite count |
| `/guide` | View full User Guide |
| `/id` | Check your Telegram ID, Member ID, account info |
| *Paste Base32 Key* | Auto-generates 6-digit TOTP 2FA code instantly |
| *Open Menu* | Access Name Generator with category & gender settings |

---

*Guide maintained by KKH — Fake Names 2FA Bot System*
