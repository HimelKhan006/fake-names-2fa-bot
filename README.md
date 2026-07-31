# Fake Names 2FA: Name Generator & Universal 2FA Authenticator Bot

A professional Telegram bot written in Python using `pyTelegramBotAPI` (`telebot`), `pyotp`, and `python-dotenv`.

CREATED BY: KKH

---

## Key Features

1. **Admin Direct Messaging & Mass Broadcast**:
   - `/send <user_id> <message>` — Send custom direct messages to any member via the bot.
   - `/broadcast <message>` — Broadcast announcements to all registered bot members with live completion stats.

2. **Admin Remote Message Deletion**:
   - `/delete <chat_id> <message_id>` (or `/del`) — Remotely delete any message sent by the bot in a user's chat.

3. **Full Bot & Cache Reset on `/restart`**:
   - Sending `/restart` wipes user session memory, resets active settings to default (`Mixed`, `10 Names`), purges persistent bottom Reply Keyboards, and triggers an immediate command cache re-sync across Telegram servers.

4. **Complete Removal of `/hub` and `/help`**:
   - `/hub` and `/help` removed completely from code, decorators, and multi-scope Telegram API registrations.

5. **Deduplicated Native Telegram Menu**:
   - Clean 4-command list (`/start`, `/restart`, `/invite`, `/guide`) registered across `BotCommandScopeDefault` and `BotCommandScopeAllPrivateChats`.

6. **Persistent Reply Keyboard Removal**:
   - Sends `ReplyKeyboardRemove()` to permanently collapse and purge any persistent bottom Reply Keyboard grid (`Start Bot`, `Restart Bot`, `Open KKH Names Hub`, `User Guide`).

7. **Clean Console Keyboard**:
   - Clean 3-row layout ending with full-width `[ GENERATE ]` button on the main console keyboard.

8. **Native Menu Bar Exclusive Invite Access**:
   - Invite system accessible exclusively via Telegram's native blue **Menu** bar (`/invite`).

9. **Personal Invite Statistics**:
   - Every user can view their Member ID (`#FN-1001`) and exact live count of `Total Invited Users by You: X Members`.

10. **Admin Panel Only Leaderboard**:
    - Global Top Inviters Leaderboard restricted exclusively to the Admin Dashboard (`/admin`, `/stats`).

11. **Admin Ban & Unban System**:
    - `/ban <user_id>` — Instantly blocks a user from accessing the bot.
    - `/unban <user_id>` — Restores user access.
    - `/banned` — View list of all banned user accounts.

12. **Real-Time Username Synchronizer**:
    - Automatically tracks and updates live `@username` and first name changes across the Admin Panel.

13. **Professional Unique Member IDs**:
    - Assigns a unique serial Member ID (`#FN-1001`, `#FN-1002`) to every member.

14. **First-Time User Professional Welcome & Guide**:
    - New users starting the bot are greeted with a personalized Welcome Banner, full User Guide, and active settings console in **strictly 1 clean message bubble**.

15. **Transparent 2FA Secret Key Decoding**:
    - Paste any Base32 2FA Secret Key or `otpauth://` link into chat to get a live 6-digit TOTP code instantly in a single-tap copy block.

16. **Ultra-Fast Multi-Threaded Speed**:
    - Multi-threaded worker pool (`num_threads=16`) processes concurrent commands in < 20ms.
    - `skip_pending=True` eliminates startup lag.

17. **Automatic 409 Conflict Recovery**:
    - Built-in polling auto-retry loop seamlessly handles Telegram 409 Conflict errors when restarting instances.

---

## Quick Setup & Execution Guide

### 1. Install Dependencies

```bash
pip install pyTelegramBotAPI pyotp python-dotenv
```

### 2. Configure Environment

Ensure `.env` contains your token and admin ID:

```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
ADMIN_ID=8772394606
```

### 3. Run the Bot

```bash
python main.py
```
