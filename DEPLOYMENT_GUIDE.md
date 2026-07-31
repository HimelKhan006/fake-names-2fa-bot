# 🚀 COMPLETE A-TO-Z TELEGRAM BOT SETUP & DEPLOYMENT GUIDE

**Bot Name**: Fake Names 2FA Generator & Authenticator  
**Created By**: KKH  
**GitHub Repository**: `https://github.com/HimelKhan006/fake-names-2fa-bot.git`  

---

## 📑 TABLE OF CONTENTS

1. [Telegram Bot Creation via BotFather](#1-telegram-bot-creation-via-botfather)
2. [Exact Files to Upload to Hosting / GitHub](#2-exact-files-to-upload-to-hosting--github)
3. [PowerShell, CMD & Linux Terminal Commands](#3-powershell-cmd--linux-terminal-commands)
4. [GitHub Repository Setup & Push Commands](#4-github-repository-setup--push-commands)
5. [24/7 Hosting Setup Instructions on Render.com](#5-247-hosting-setup-instructions-on-rendercom)
6. [24/7 Continuous Uptime Pinger (UptimeRobot)](#6-247-continuous-uptime-pinger-uptimerobot)
7. [Admin & User Commands Master Reference Guide](#7-admin--user-commands-master-reference-guide)

---

## 1. Telegram Bot Creation via BotFather

Follow these step-by-step instructions in Telegram:

1. Open Telegram and search for **[@BotFather](https://t.me/BotFather)**.
2. Start chat and send:

   ```text
   /newbot
   ```

3. Enter your **Bot Name**:

   ```text
   Fake Names 2FA
   ```

4. Enter your **Bot Username** (must end in `bot`):

   ```text
   Fake_Names_2FA_Bot
   ```

5. Copy your **HTTP API Token** (Format: `8772394606:AAFbBND_6i1Cxg7mRn0CeoMZhZlRU4LNA0Y`).
6. Set Bot Description (Optional):

   ```text
   /setdescription
   ```

   *Select your bot and paste*:

   ```text
   Instant Fake Name Generator & 2FA Authenticator Bot created by KKH.
   ```

---

## 2. Exact Files to Upload to Hosting / GitHub

### ✅ FILES YOU MUST UPLOAD (Essential Project Files)

| File Name | Purpose | Upload Status |
| :--- | :--- | :--- |
| `main.py` | Complete bot source code (16-worker threads, 2FA decoder, name generator, HTTP health server) | **MUST UPLOAD ✅** |
| `requirements.txt` | Python dependencies (`pyTelegramBotAPI`, `pyotp`, `python-dotenv`) | **MUST UPLOAD ✅** |
| `Procfile` | Render Web Service process startup instruction (`web: python main.py`) | **MUST UPLOAD ✅** |
| `.gitignore` | Protects private secret files from leaking to GitHub | **MUST UPLOAD ✅** |
| `README.md` & `DEPLOYMENT_GUIDE.md` | Complete documentation and setup manuals | **MUST UPLOAD ✅** |

### ❌ FILES YOU MUST NEVER UPLOAD TO PUBLIC GITHUB

| File Name | Reason | Where to Put Secrets Instead? |
| :--- | :--- | :--- |
| `.env` | Contains private `TELEGRAM_BOT_TOKEN` | Enter secrets safely inside Render's **Environment Variables** tab! |

---

## 3. PowerShell, CMD & Linux Terminal Commands

Choose your terminal environment below and execute these exact copy-paste commands:

### 3.1 Windows PowerShell Commands

Open PowerShell and run:

```powershell
# 1. Navigate to project directory
Set-Location -Path "c:\new tele bot"

# 2. Create .env configuration file
@'
TELEGRAM_BOT_TOKEN=8772394606:AAFbBND_6i1Cxg7mRn0CeoMZhZlRU4LNA0Y
ADMIN_ID=6798979733,@MegalodonKKH
'@ | Set-Content -Path ".env" -Encoding UTF8

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Verify Python code syntax compilation
python -m py_compile main.py

# 5. Run bot locally for testing
python main.py
```

---

### 3.2 Windows Command Prompt (CMD) Commands

Open CMD (`cmd.exe`) and run:

```cmd
:: 1. Navigate to project directory
cd /d "c:\new tele bot"

:: 2. Create .env file
echo TELEGRAM_BOT_TOKEN=8772394606:AAFbBND_6i1Cxg7mRn0CeoMZhZlRU4LNA0Y > .env
echo ADMIN_ID=6798979733,@MegalodonKKH >> .env

:: 3. Install Python dependencies
pip install -r requirements.txt

:: 4. Verify Python code syntax compilation
python -m py_compile main.py

:: 5. Run bot locally for testing
python main.py
```

---

### 3.3 Linux / Ubuntu VPS Server Setup Commands

If hosting on a Linux / Ubuntu VPS server:

```bash
# 1. Update system packages
sudo apt update && sudo apt upgrade -y

# 2. Install Python 3, Pip and Git
sudo apt install python3 python3-pip git -y

# 3. Clone repository
git clone https://github.com/HimelKhan006/fake-names-2fa-bot.git
cd fake-names-2fa-bot

# 4. Create .env configuration file
cat << 'EOF' > .env
TELEGRAM_BOT_TOKEN=8772394606:AAFbBND_6i1Cxg7mRn0CeoMZhZlRU4LNA0Y
ADMIN_ID=6798979733,@MegalodonKKH
EOF

# 5. Install dependencies
pip3 install -r requirements.txt

# 6. Run bot in 24/7 background mode
nohup python3 main.py > bot.log 2>&1 &
```

---

## 4. GitHub Repository Setup & Push Commands

Run these terminal commands in PowerShell or CMD to push your code:

```bash
# 1. Initialize Git repository
git init

# 2. Add core files
git add main.py requirements.txt Procfile .gitignore README.md DEPLOYMENT_GUIDE.md

# 3. Commit changes
git commit -m "Complete Fake Names 2FA bot implementation"

# 4. Connect to remote GitHub repo
git remote add origin https://github.com/HimelKhan006/fake-names-2fa-bot.git

# 5. Push code to main branch
git branch -M main
git push -u origin main --force
```

---

## 5. 24/7 Hosting Setup Instructions on Render.com

Follow these step-by-step instructions to host your bot 24/7 for free:

1. Log in to **[Render.com](https://render.com)**.
2. Click **New +** ➔ **Web Service**.
3. Select **Build and deploy from a Git repository** and connect `fake-names-2fa-bot`.
4. Enter the following exact settings:
   - **Name**: `fake-names-2fa-bot`
   - **Region**: `Oregon (US West)` or `Frankfurt (EU Central)`
   - **Branch**: `main`
   - **Root Directory**: *(Leave blank)*
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Instance Type**: `Free`
5. Click **Advanced** ➔ **Add Environment Variable**:
   - `TELEGRAM_BOT_TOKEN` = `8772394606:AAFbBND_6i1Cxg7mRn0CeoMZhZlRU4LNA0Y`
   - `ADMIN_ID` = `6798979733,@MegalodonKKH`
   - `PORT` = `10000`
6. Click **Create Web Service**. Render will build the image, deploy the application, and assign your Web Service URL (e.g. `https://fake-names-2fa-bot.onrender.com`).

---

## 6. 24/7 Continuous Uptime Pinger (UptimeRobot)

Render Free Tier puts Web Services to sleep after 15 minutes of HTTP inactivity. Keep it awake 24/7 for FREE:

1. Create a free account at **[UptimeRobot.com](https://uptimerobot.com)**.
2. Click **Add New Monitor** button.
3. Configure settings:
   - **Monitor Type**: `HTTP(s)`
   - **Friendly Name**: `Fake Names 2FA Bot`
   - **URL / IP**: `https://fake-names-2fa-bot.onrender.com`
   - **Monitoring Interval**: `5 minutes`
4. Click **Create Monitor**. UptimeRobot will ping your Render Web Service every 5 minutes 24/7, keeping your Telegram bot active continuously without sleeping!

---

## 7. Admin & User Commands Master Reference Guide

### 👑 Admin Management Commands

| Command Syntax | Action Description & Example Usage |
| :--- | :--- |
| `/admin` or `/stats` | Open live Admin Panel Dashboard with stats & top inviters leaderboard |
| `/users` | Inspect all registered bot members with Member IDs (`#FN-1001`) |
| `/send <user_id> <msg>` | Send direct message to a user (Example: `/send 6798979733 Hello!`) |
| `/broadcast <msg>` | Broadcast announcement to all members (Example: `/broadcast System Update!`) |
| `/delete_broadcast B-101` | Delete broadcast message from all member chats (or reply `/delete` to summary card) |
| `/delete <chat_id> <msg_id>` | Remotely delete any message sent by the bot (or reply `/delete` to message) |
| `/ban <user_id>` | Suspend a user's bot access (Example: `/ban 123456789`) |
| `/unban <user_id>` | Restore a banned user's access (Example: `/unban 123456789`) |
| `/banned` | View list of all currently suspended user accounts |

### 👤 General User Commands (Native Menu Bar)

| Command Syntax | Action Description |
| :--- | :--- |
| `/start` | Start / Restart bot and open clean Console Menu |
| `/invite` | Get personal deep-link referral URL & view live invite count |
| `/guide` | View complete User Guide manual |
| `/id` | Inspect your Telegram User ID, Member ID (`#FN-1001`), and account status |
| *Paste Base32 Key* | Paste Base32 Secret or OTPAuth URL to generate instant 6-digit TOTP code |
