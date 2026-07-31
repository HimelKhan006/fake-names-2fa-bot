# 🚀 COMPLETE A-TO-Z TELEGRAM BOT SETUP & DEPLOYMENT GUIDE

**Bot Name**: Fake Names 2FA Generator & Authenticator  
**Created By**: KKH  
**GitHub Repository**: `https://github.com/HimelKhan006/fake-names-2fa-bot.git`  

---

## 📑 TABLE OF CONTENTS

1. [Telegram Bot Creation via BotFather](#1-telegram-bot-creation-via-botfather)
2. [Project Files & Architecture](#2-project-files--architecture)
3. [Local Configuration & Testing](#3-local-configuration--testing)
4. [GitHub Repository Setup & Push](#4-github-repository-setup--push)
5. [24/7 Hosting on Render.com](#5-247-hosting-on-rendercom)
6. [24/7 Continuous Uptime Pinger (UptimeRobot)](#6-247-continuous-uptime-pinger-uptimerobot)
7. [Admin Control Panel & Commands Master List](#7-admin-control-panel--commands-master-list)

---

## 1. Telegram Bot Creation via BotFather

1. Open Telegram and search for **[@BotFather](https://t.me/BotFather)**.
2. Send `/newbot` to create a new bot.
3. Choose a Name (e.g. `Fake Names 2FA`).
4. Choose a Username ending in `bot` (e.g. `Fake_Names_2FA_Bot`).
5. Copy your **HTTP API Token** (e.g. `8772394606:AAFbBND_6i...`).

---

## 2. Project Files & Architecture

For safe long-term backup, store these **6 core files**:

| File Name | Purpose |
| :--- | :--- |
| `main.py` | Complete bot source code with 16-worker thread polling, 2FA decoder, name generator, HTTP health check, and admin system |
| `requirements.txt` | Python library dependencies (`pyTelegramBotAPI`, `pyotp`, `python-dotenv`) |
| `Procfile` | Render Web Service deployment command (`web: python main.py`) |
| `.gitignore` | Prevents private `.env` and `__pycache__` from leaking to public GitHub |
| `README.md` | Feature overview and quickstart instructions |
| `DEPLOYMENT_GUIDE.md` | Full A-to-Z deployment and maintenance manual |

---

## 3. Local Configuration & Testing

1. Create a `.env` file in the project folder with:

   ```env
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   ADMIN_ID=6798979733,@MegalodonKKH
   ```

2. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the bot locally:

   ```bash
   python main.py
   ```

*Note: Before running on Render live server, ALWAYS close local `python main.py` so only 1 instance connects to Telegram.*

---

## 4. GitHub Repository Setup & Push

1. Initialize Git repository and commit code:

   ```bash
   git init
   git add .
   git commit -m "Initial commit for Fake Names 2FA bot"
   ```

2. Link to your GitHub repo and push:

   ```bash
   git remote add origin https://github.com/HimelKhan006/fake-names-2fa-bot.git
   git branch -M main
   git push -u origin main --force
   ```

---

## 5. 24/7 Hosting on Render.com

1. Sign up/Log in to **[Render.com](https://render.com)**.
2. Click **New +** ➔ **Web Service**.
3. Connect your GitHub Repository `fake-names-2fa-bot`.
4. Configure Web Service Settings:
   - **Name**: `fake-names-2fa-bot`
   - **Environment**: `Python 3`
   - **Region**: Any (e.g. Oregon / Frankfurt)
   - **Branch**: `main`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python main.py`
   - **Instance Type**: `Free`
5. Add Environment Variables under **Environment**:
   - `TELEGRAM_BOT_TOKEN`: `your_bot_token`
   - `ADMIN_ID`: `6798979733,@MegalodonKKH`
   - `PORT`: `10000`
6. Click **Create Web Service**. Render will deploy your bot and expose your HTTP health URL (e.g. `https://fake-names-2fa-bot.onrender.com`).

---

## 6. 24/7 Continuous Uptime Pinger (UptimeRobot)

Render free tier Web Services sleep after 15 minutes of inactivity. Keep it awake 24/7 for FREE:

1. Sign up on **[UptimeRobot.com](https://uptimerobot.com)**.
2. Click **Add New Monitor**.
3. Select **Monitor Type**: `HTTP(s)`.
4. Set **Friendly Name**: `Fake Names 2FA Bot`.
5. Enter **URL**: `https://fake-names-2fa-bot.onrender.com`.
6. Set **Monitoring Interval**: `5 minutes`.
7. Click **Create Monitor**. UptimeRobot will ping your server every 5 minutes 24/7!

---

## 7. Admin Control Panel & Commands Master List

Only users listed in `ADMIN_ID` can access Admin commands.

### 👑 Admin Commands

- `/admin` or `/stats` — Open live Admin Dashboard & Invites Leaderboard
- `/users` — Inspect all registered members & Unique IDs (`#FN-1001`)
- `/send <user_id> <message>` (or reply) — Direct message any member via the bot
- `/broadcast <message>` — Send mass broadcast to all members (returns Broadcast ID `B-101`)
- `/delete_broadcast B-101` (or reply `/delete`) — Delete broadcast from all member chats
- `/delete <chat_id> <message_id>` (or reply `/delete`) — Remotely delete any bot message in user chat
- `/ban <user_id>` (or reply) — Ban user account from bot access
- `/unban <user_id>` (or reply) — Unban user account
- `/banned` — List all banned user accounts

### 👤 General User Commands (Native Menu Bar)

- `/start` — Start / Restart bot & open Console Menu
- `/invite` — Get personal referral deep-link & view invite count
- `/guide` — View complete User Guide
- `/id` — Inspect Telegram User ID & Account Info
- *Paste Base32 Key / OTPAuth Link* — Generate instant 6-digit TOTP code
