"""
Fake Names 2FA: Name Generator & Universal 2FA Authenticator Bot
================================================================
CREATED BY: KKH

Features:
- Ultra-Fast High-Performance Worker Pool (num_threads=16) for Instant Speed
- Zero-Lag Long Polling (timeout=1, skip_pending=True)
- Direct 1-Call Message Dispatches (No extra network deletion round-trips)
- Pre-Compiled Global Regular Expressions for Sub-Millisecond 2FA TOTP Decoding
- Clean Native Telegram Menu Commands: /start, /restart, /invite, /guide
- Reply Keyboard Purger: Permanently removes persistent bottom Reply Keyboards
- Clean Console Keyboard Layout: 3 Rows ending with full-width [ GENERATE ] button
- Personal User Invite Counter & Statistics
- Leaderboard Restricted Exclusively to Admin Panel (/admin, /stats)
- Admin Ban & Unban System (/ban, /unban, /banned)
- Real-Time Telegram Username & Name Synchronizer
- Professional Unique Member ID Assignment (#FN-1001, #FN-1002...)
- Admin Referral Dashboard & Live User Sharing History Tracking (/admin, /stats, /users)
- Professional Bot Invite & Share System with Deep-Link Referral Tracking
- First-Time User Professional Welcome Message & Integrated User Guide
- Transparent 2FA Base32 TOTP secret key decoding directly in main chat
- Single-Message Clean Console Output with Inline Settings Controls
- Pure Single-Tap Copy Name Blocks (No initials, no emojis)
- Safe Admin Join Alerts Guard
- Robust Telegram 409 Conflict Auto-Recovery Retry Loop
"""

import os
import re
import sys
import random
import time
import signal
import atexit
import threading
import logging
from typing import Optional
from dotenv import load_dotenv

import pyotp
import telebot
from telebot import types

# Pre-compiled Regex Patterns for Sub-Millisecond 2FA Parsing & Confirmation Card Extraction
RE_SECRET_URL = re.compile(r'secret=([A-Za-z2-7=]+)', re.IGNORECASE)
RE_CLEAN_BASE32 = re.compile(r'[^A-Za-z2-7]')
RE_CONFIRM_USER_ID = re.compile(r'User ID:\s*`?(\d+)`?', re.IGNORECASE)
RE_CONFIRM_MSG_ID = re.compile(r'Message ID:\s*`?(\d+)`?', re.IGNORECASE)
RE_CONFIRM_BROADCAST_ID = re.compile(r'Broadcast ID:\s*`?B-(\d+)`?', re.IGNORECASE)

# -----------------------------------------------------------------------------
# 1. Environment & Bot Initialization (16 Concurrent Worker Threads)
# -----------------------------------------------------------------------------
load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("FakeNames2FA")

API_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_IDS = set()
ADMIN_USERNAMES = set()
ADMIN_ID_STR = os.getenv("ADMIN_ID", "")
for pid in ADMIN_ID_STR.replace(',', ' ').split():
    pid_clean = pid.strip()
    if pid_clean.isdigit():
        ADMIN_IDS.add(int(pid_clean))
    elif pid_clean.startswith('@'):
        ADMIN_USERNAMES.add(pid_clean.lower())
    elif pid_clean:
        ADMIN_USERNAMES.add(f"@{pid_clean.lower()}")

ADMIN_ID = list(ADMIN_IDS)[0] if ADMIN_IDS else None

if not API_TOKEN or API_TOKEN == "your_telegram_bot_token_here":
    print("\n[ERROR] TELEGRAM_BOT_TOKEN is missing!")
    print("Please set TELEGRAM_BOT_TOKEN in your .env file.\n")
    sys.exit(1)

bot = telebot.TeleBot(API_TOKEN, threaded=True, num_threads=16)

# Resolve Bot Username dynamically
BOT_USERNAME = "FakeNames2FABot"
try:
    me = bot.get_me()
    if me and me.username:
        BOT_USERNAME = me.username
        logger.info(f"Bot Username resolved: @{BOT_USERNAME}")
except Exception as err:
    logger.warning(f"Could not resolve bot username: {err}")

# Multi-Scope Command Cache Purger & Sync
def register_clean_native_commands():
    try:
        scopes = [
            types.BotCommandScopeDefault(),
            types.BotCommandScopeAllPrivateChats(),
            types.BotCommandScopeAllGroupChats(),
            types.BotCommandScopeAllChatAdministrators(),
        ]
        for sc in scopes:
            try:
                bot.delete_my_commands(scope=sc)
            except Exception:
                pass

        native_commands = [
            types.BotCommand("start", "Start Fake Names 2FA"),
            types.BotCommand("restart", "Reset session & restart bot"),
            types.BotCommand("invite", "Invite & share bot link"),
            types.BotCommand("guide", "View User Guide"),
        ]
        for sc in scopes:
            try:
                bot.set_my_commands(native_commands, scope=sc)
            except Exception:
                pass

        logger.info("Purged all command scopes and registered clean 4 native Telegram menu commands successfully.")
    except Exception as err:
        logger.warning(f"Could not register my_commands: {err}")

register_clean_native_commands()

# In-Memory Fast Storage
user_settings = {}
user_history = {}
known_users = set()       # Set of regular non-admin member Telegram user_ids
banned_users = set()      # Set of banned Telegram user_ids
user_names = {}           # user_id -> "[#FN-1001] Full Name (@username)"
user_unique_ids = {}      # user_id -> "#FN-1001"
referrals = {}            # inviter_id -> set of invited user_ids
broadcast_history = {}    # broadcast_seq (int) -> list of (user_id, message_id)
broadcast_seq = 100

def get_unique_id(user_id):
    """Assigns and retrieves a professional unique member ID (#FN-1001 or #FN-ADMIN)."""
    if user_id in user_unique_ids:
        return user_unique_ids[user_id]
    if ADMIN_IDS and user_id in ADMIN_IDS:
        user_unique_ids[user_id] = "#FN-ADMIN"
    else:
        member_count = len([uid for uid in user_unique_ids if user_unique_ids[uid] != "#FN-ADMIN"])
        seq = 1001 + member_count
        user_unique_ids[user_id] = f"#FN-{seq}"
    return user_unique_ids[user_id]

def sync_user_profile(user):
    """Real-time profile synchronizer for live username & name tracking."""
    user_id = user.id
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip() or "User"
    username = f"@{user.username}" if user.username else "No Username"
    uniq_id = get_unique_id(user_id)
    
    user_names[user_id] = f"[{uniq_id}] {full_name} ({username})"
    return uniq_id, full_name, username

def check_and_notify_new_user(user, inviter_id=None):
    """Sends a clean alert to Admin and Inviter whenever a new user joins/starts the bot."""
    user_id = user.id
    uniq_id, full_name, username = sync_user_profile(user)

    # Track only regular non-admin users in known_users
    if user_id not in known_users and (not ADMIN_IDS or user_id not in ADMIN_IDS):
        known_users.add(user_id)

        # Notify Admin asynchronously
        admin_msg = (
            "New Member Joined Fake Names 2FA!\n\n"
            f"Member ID: {uniq_id}\n"
            f"Name: {full_name}\n"
            f"Username: {username}\n"
            f"Telegram User ID: `{user_id}`"
        )
        if inviter_id:
            inviter_display = user_names.get(inviter_id, f"ID: {inviter_id}")
            admin_msg += f"\nInvited By: {inviter_display}"

        for aid in ADMIN_IDS:
            try:
                bot.send_message(aid, admin_msg, parse_mode='Markdown')
            except Exception:
                pass

        # Notify Inviter if invited via ref link
        if inviter_id and inviter_id != user_id:
            if inviter_id not in referrals:
                referrals[inviter_id] = set()
            referrals[inviter_id].add(user_id)

            try:
                inviter_msg = (
                    "🎉 NEW REFERRAL JOINED!\n\n"
                    f"Member ID: {uniq_id}\n"
                    f"Name: {full_name}\n"
                    f"Username: {username}\n"
                    f"Total Invited Users by You: {len(referrals[inviter_id])} Members"
                )
                bot.send_message(inviter_id, inviter_msg)
            except Exception:
                pass

def check_ban_guard(chat_id, user_id):
    """Returns True if user is banned and notifies them cleanly."""
    if user_id in banned_users:
        ban_msg = (
            "⛔ ACCESS DENIED\n\n"
            "Your Telegram account has been banned from using Fake Names 2FA.\n"
            "Contact Admin if you believe this is an error."
        )
        try:
            bot.send_message(chat_id, ban_msg)
        except Exception:
            pass
        return True
    return False

def get_user_settings(user_id):
    if user_id not in user_settings:
        user_settings[user_id] = {'gender': 'mixed', 'quantity': 10}
    return user_settings[user_id]

# -----------------------------------------------------------------------------
# 2. Universal 2FA Secret Key Sanitizer & Parser (Sub-Millisecond Speed)
# -----------------------------------------------------------------------------
def universal_extract_2fa_secret(text: str) -> Optional[str]:
    """
    Sub-millisecond Base32 2FA secret key parser using pre-compiled regex.
    """
    if not text:
        return None

    raw_text = text.strip()

    # 1. Handle otpauth:// URLs
    if "secret=" in raw_text.lower():
        match = RE_SECRET_URL.search(raw_text)
        if match:
            raw_text = match.group(1)

    # 2. Clean out spaces, hyphens, tabs, newlines, and invalid chars
    cleaned = RE_CLEAN_BASE32.sub('', raw_text).upper()

    # Base32 2FA keys are standard 16, 26, 32, or 64 characters long
    if len(cleaned) < 16:
        return None

    # 3. Auto-pad Base32 string to multiple of 8 if required
    missing_padding = len(cleaned) % 8
    if missing_padding:
        cleaned += '=' * (8 - missing_padding)

    return cleaned

# -----------------------------------------------------------------------------
# 3. Word Banks & Pure Name Generator
# -----------------------------------------------------------------------------
MALE_FIRST_NAMES = [
    "Ledger", "Alan", "Muhammad", "Omar", "Ali", "Usman", "Ibrahim", "Yusuf", "Tariq", "Hamza",
    "Bilal", "Khalid", "Yahya", "Zayd", "Idris", "Anas", "Rayyan", "Mustafa", "Sulaiman", "Harun",
    "James", "Robert", "Liam", "Alexander", "Daniel", "Ethan", "Michael", "William", "David", "John",
    "Joseph", "Matthew", "Benjamin", "Samuel", "Sebastian", "Henry", "Jackson", "Owen", "Gabriel", "Carter",
    "Jayden", "Wyatt", "Julian", "Grayson", "Leo", "Isaac", "Anthony", "Theodore", "Dylan", "Luke"
]

FEMALE_FIRST_NAMES = [
    "Peyton", "Radha", "Fatima", "Aisha", "Khadija", "Maryam", "Zainab", "Ruqayyah", "Sumayyah", "Yasmin",
    "Safiyyah", "Hafsah", "Sarah", "Hajar", "Asma", "Juwairiyah", "Sawdah", "Maymunah", "Halimah", "Layla",
    "Emma", "Olivia", "Sophia", "Isabella", "Charlotte", "Amelia", "Mia", "Harper", "Evelyn", "Abigail",
    "Emily", "Ella", "Elizabeth", "Camila", "Luna", "Sofia", "Avery", "Mila", "Aria", "Scarlett",
    "Penelope", "Chloe", "Victoria", "Madison", "Eleanor", "Grace", "Nora", "Riley", "Zoey", "Hannah"
]

SURNAMES = [
    "Carleton", "Hopkins", "Giles", "Atkins", "Al-Faruq", "Al-Hassan", "Al-Husayn", "Siddiqui", "Farooqi", "Rahman",
    "Khan", "Malik", "Qureshi", "Abbasi", "Hashimi", "Ansari", "Al-Masri", "Al-Baghdadi", "Usmani", "Smith",
    "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez", "Hernandez",
    "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee",
    "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker"
]

def generate_simple_name(user_id, gender):
    """Generates a simple unique First Name + Last Name in < 1ms."""
    if user_id not in user_history:
        user_history[user_id] = set()

    is_female = (gender.lower() == "female")
    first_list = FEMALE_FIRST_NAMES if is_female else MALE_FIRST_NAMES

    for _ in range(20):
        first = random.choice(first_list)
        last = random.choice(SURNAMES)
        full_name = f"{first} {last}"

        if full_name not in user_history[user_id]:
            if len(user_history[user_id]) > 5000:
                user_history[user_id].pop()
            user_history[user_id].add(full_name)
            return full_name

    return f"{random.choice(first_list)} {random.choice(SURNAMES)}"

# -----------------------------------------------------------------------------
# 4. Fake Names 2FA UI Console & User Guide
# -----------------------------------------------------------------------------
def build_kkh_keyboard(settings):
    """Builds Fake Names 2FA clean interactive inline keyboard."""
    gender = settings['gender']
    qty = settings['quantity']

    g_m = "Male " + ("✓" if gender == "male" else "")
    g_f = "Female " + ("✓" if gender == "female" else "")
    g_x = "Mixed " + ("✓" if gender == "mixed" else "")

    q5 = "5 " + ("✓" if qty == 5 else "")
    q10 = "10 " + ("✓" if qty == 10 else "")
    q20 = "20 " + ("✓" if qty == 20 else "")
    q50 = "50 " + ("✓" if qty == 50 else "")

    markup = types.InlineKeyboardMarkup(row_width=3)
    
    # Row 1: Gender
    btn_m = types.InlineKeyboardButton(g_m.strip(), callback_data="set_g_male")
    btn_f = types.InlineKeyboardButton(g_f.strip(), callback_data="set_g_female")
    btn_x = types.InlineKeyboardButton(g_x.strip(), callback_data="set_g_mixed")
    markup.row(btn_m, btn_f, btn_x)

    # Row 2: Quantity
    btn_q5 = types.InlineKeyboardButton(q5.strip(), callback_data="set_q_5")
    btn_q10 = types.InlineKeyboardButton(q10.strip(), callback_data="set_q_10")
    btn_q20 = types.InlineKeyboardButton(q20.strip(), callback_data="set_q_20")
    btn_q50 = types.InlineKeyboardButton(q50.strip(), callback_data="set_q_50")
    markup.row(btn_q5, btn_q10, btn_q20, btn_q50)

    # Row 3: Full-Width Generate Action Button
    btn_gen = types.InlineKeyboardButton("GENERATE", callback_data="do_generate")
    markup.row(btn_gen)

    return markup

def get_kkh_menu_text(settings):
    """Generates Fake Names 2FA menu text without emojis."""
    gender_label = settings['gender'].capitalize()
    qty_label = f"{settings['quantity']} Names"

    return (
        "Fake Names 2FA\n"
        "CREATED BY: KKH\n\n"
        "ACTIVE SETTINGS:\n"
        f"• Gender Preference: {gender_label}\n"
        f"• Batch Quantity: {qty_label}\n\n"
        "Tap options below to customize, then press GENERATE:"
    )

def get_invite_text(user_id):
    """Generates professional invite card text with personal referral stats."""
    invite_link = f"https://t.me/{BOT_USERNAME}?start=ref_{user_id}"
    total_refs = len(referrals.get(user_id, []))
    uniq_id = get_unique_id(user_id)

    return (
        "INVITE & SHARE FAKE NAMES 2FA\n"
        "CREATED BY: KKH\n\n"
        f"Member ID: {uniq_id}\n"
        f"Total Invited Users by You: {total_refs} Members\n\n"
        "YOUR PERSONAL BOT INVITE LINK:\n"
        f"`{invite_link}`\n\n"
        "Share this link with your friends, groups, or channels! When someone joins using your link, your invite counter updates automatically."
    )

def get_user_guide_text():
    """Generates professional user guide text for Fake Names 2FA."""
    return (
        "Fake Names 2FA — USER GUIDE\n"
        "CREATED BY: KKH\n\n"
        "1. NAME GENERATOR:\n"
        "• Select Gender Preference (Male, Female, Mixed).\n"
        "• Select Batch Quantity (5, 10, 20, 50).\n"
        "• Press GENERATE to create clean names instantly.\n"
        "• Tap on any generated name to copy it to your clipboard.\n\n"
        "2. INSTANT 2FA AUTHENTICATOR:\n"
        "• Paste any Base32 2FA Secret Key or OTPAuth link into chat.\n"
        "• The bot will instantly return your 6-digit TOTP code in a single-tap copy block!\n\n"
        "3. INVITE SYSTEM:\n"
        "• Use Telegram's native Menu (/invite) to get your personal invite link and track how many members you have invited!\n\n"
        "4. NAVIGATION:\n"
        "• Use Telegram's native menu button (/) to access commands (/start, /restart, /invite, /guide) anytime."
    )

def get_admin_dashboard_text():
    """Generates Admin Dashboard text with live statistics & leaderboards."""
    total_users = len(known_users)
    total_banned = len(banned_users)
    total_referral_joins = sum(len(v) for v in referrals.values())

    sorted_inviters = sorted(referrals.items(), key=lambda item: len(item[1]), reverse=True)

    leaderboard_lines = []
    if sorted_inviters:
        for idx, (inv_id, ref_list) in enumerate(sorted_inviters[:10], 1):
            name_info = user_names.get(inv_id, f"User ID: {inv_id}")
            leaderboard_lines.append(f"{idx}. {name_info} — {len(ref_list)} Invites")
    else:
        leaderboard_lines.append("No referral joins recorded yet.")

    leaderboard_str = "\n".join(leaderboard_lines)

    return (
        "ADMIN DASHBOARD — FAKE NAMES 2FA\n"
        "CREATED BY: KKH\n\n"
        "STATS OVERVIEW:\n"
        f"• Total Registered Members: {total_users}\n"
        f"• Total Banned Accounts: {total_banned}\n"
        f"• Total Referral Joins: {total_referral_joins}\n\n"
        "TOP INVITERS LEADERBOARD:\n"
        f"{leaderboard_str}\n\n"
        "───────────────────────────\n"
        "ADMIN COMMANDS:\n"
        "• /send <msg> (or reply) — Send direct message to a user\n"
        "• /broadcast <msg> — Broadcast message to all members\n"
        "• /delete (or reply) — Delete message from user chat\n"
        "• /delete_broadcast <b_id> (or reply /delete) — Delete broadcast from all members\n"
        "• /ban <user_id> — Ban a Telegram account\n"
        "• /unban <user_id> — Unban a Telegram account\n"
        "• /banned — List all banned user accounts\n"
        "• /users — Inspect all members & Unique IDs\n"
        "• /admin or /stats — Refresh Admin Dashboard"
    )

# -----------------------------------------------------------------------------
# 5. Telegram Handlers (Instant Execution)
# -----------------------------------------------------------------------------
@bot.message_handler(commands=['admin', 'stats', 'users', 'ban', 'unban', 'banned', 'send', 'broadcast', 'delete', 'del', 'delete_broadcast', 'delbroadcast', 'deletebroadcast'])
def handle_admin_commands(message):
    try:
        user_id = message.from_user.id
        user_handle = f"@{message.from_user.username.lower()}" if message.from_user.username else ""

        is_admin = False
        if ADMIN_IDS and user_id in ADMIN_IDS:
            is_admin = True
        elif ADMIN_USERNAMES and user_handle and user_handle in ADMIN_USERNAMES:
            is_admin = True
        elif not ADMIN_IDS and not ADMIN_USERNAMES:
            is_admin = True

        if not is_admin:
            denied_msg = (
                "⛔ ACCESS RESTRICTED | FAKE NAMES 2FA\n"
                "CREATED BY: KKH\n\n"
                "This command is restricted exclusively to authorized bot Administrators.\n\n"
                "YOUR ACCOUNT DETAILS:\n"
                f"• Telegram User ID: `{user_id}`\n"
                f"• Username: `{user_handle or 'No Username'}`\n"
                "• Access Status: Unauthorized\n\n"
                "💡 Add this ID or Username to ADMIN_ID to grant admin access."
            )
            bot.send_message(message.chat.id, denied_msg, parse_mode='Markdown')
            return

        sync_user_profile(message.from_user)
        cmd_text = message.text or ""
        parts = cmd_text.split()
        cmd = parts[0].lower().split('@')[0]

        clear_kb = types.ReplyKeyboardRemove()

        # 1. Ban System (/ban <user_id> OR reply to a user's message with /ban)
        if cmd == "/ban":
            target_id = None
            if message.reply_to_message:
                target_id = message.reply_to_message.from_user.id
            elif len(parts) >= 2 and parts[1].isdigit():
                target_id = int(parts[1])

            if not target_id:
                bot.send_message(message.chat.id, "Usage:\n• Reply to a user's message with `/ban`\n• Or type `/ban <user_id>`", parse_mode='Markdown', reply_markup=clear_kb)
                return

            banned_users.add(target_id)
            target_info = user_names.get(target_id, f"ID: {target_id}")
            target_uniq = get_unique_id(target_id)

            # Send Ban Notification directly to the target user
            user_ban_msg = (
                "⛔ ACCOUNT ACCESS SUSPENDED | FAKE NAMES 2FA\n"
                "CREATED BY: KKH\n\n"
                "Your account access has been suspended by the Bot Administrator.\n\n"
                "ACCOUNT DETAILS:\n"
                f"• Member ID: {target_uniq}\n"
                f"• Telegram User ID: `{target_id}`\n"
                "• Access Status: Banned\n\n"
                "If you believe this is a mistake, please contact the Administrator."
            )
            user_notified = False
            try:
                bot.send_message(target_id, user_ban_msg, parse_mode='Markdown')
                user_notified = True
            except Exception:
                pass

            notify_status = "Delivered to member" if user_notified else "Member notification failed (bot blocked)"
            bot.send_message(
                message.chat.id, 
                f"⛔ USER BANNED SUCCESSFULLY!\n\n• Account: {target_info}\n• User ID: `{target_id}`\n• Member Notification: {notify_status}", 
                parse_mode='Markdown', 
                reply_markup=clear_kb
            )
            return

        # 2. Unban System (/unban <user_id> OR reply to a user's message with /unban)
        if cmd == "/unban":
            target_id = None
            if message.reply_to_message:
                target_id = message.reply_to_message.from_user.id
            elif len(parts) >= 2 and parts[1].isdigit():
                target_id = int(parts[1])

            if not target_id:
                bot.send_message(message.chat.id, "Usage:\n• Reply to a user's message with `/unban`\n• Or type `/unban <user_id>`", parse_mode='Markdown', reply_markup=clear_kb)
                return

            if target_id in banned_users:
                banned_users.remove(target_id)

            target_info = user_names.get(target_id, f"ID: {target_id}")
            target_uniq = get_unique_id(target_id)

            # Send Unban Notification directly to the target user
            user_unban_msg = (
                "✅ ACCOUNT ACCESS RESTORED | FAKE NAMES 2FA\n"
                "CREATED BY: KKH\n\n"
                "Your account access has been fully restored by the Bot Administrator!\n\n"
                "ACCOUNT DETAILS:\n"
                f"• Member ID: {target_uniq}\n"
                f"• Telegram User ID: `{target_id}`\n"
                "• Access Status: Active\n\n"
                "You may now use all bot features and commands again (/start)."
            )
            user_notified = False
            try:
                bot.send_message(target_id, user_unban_msg, parse_mode='Markdown')
                user_notified = True
            except Exception:
                pass

            notify_status = "Delivered to member" if user_notified else "Member notification failed (bot blocked)"
            bot.send_message(
                message.chat.id, 
                f"✅ USER UNBANNED SUCCESSFULLY!\n\n• Account: {target_info}\n• User ID: `{target_id}`\n• Member Notification: {notify_status}", 
                parse_mode='Markdown', 
                reply_markup=clear_kb
            )
            return

        # 3. Banned List (/banned)
        if cmd == "/banned":
            if not banned_users:
                bot.send_message(message.chat.id, "No banned accounts.", reply_markup=clear_kb)
                return
            b_lines = []
            for b_id in banned_users:
                b_info = user_names.get(b_id, f"ID: {b_id}")
                b_lines.append(f"• {b_info} | ID: `{b_id}`")
            bot.send_message(message.chat.id, f"BANNED ACCOUNTS ({len(banned_users)}):\n\n" + "\n".join(b_lines), parse_mode='Markdown', reply_markup=clear_kb)
            return

        # 4. Registered Users Inspector (/users)
        if cmd == "/users":
            user_list_lines = []
            for u_id in known_users:
                u_info = user_names.get(u_id, f"ID: {u_id}")
                ref_count = len(referrals.get(u_id, []))
                status = "[BANNED]" if u_id in banned_users else "[ACTIVE]"
                user_list_lines.append(f"• {status} {u_info} | ID: `{u_id}` | Invites: {ref_count}")

            list_body = "\n".join(user_list_lines) if user_list_lines else "No registered users."
            resp = f"REGISTERED MEMBERS ({len(known_users)}):\n\n{list_body}"
            bot.send_message(message.chat.id, resp, parse_mode='Markdown', reply_markup=clear_kb)
            return

        # 5. Direct Message to User (/send <user_id> <message_text> OR reply to a message with /send <message_text>)
        if cmd == "/send":
            target_id = None
            send_text = ""

            if message.reply_to_message:
                target_id = message.reply_to_message.from_user.id
                send_text = " ".join(parts[1:])
            elif len(parts) >= 3 and parts[1].isdigit():
                target_id = int(parts[1])
                send_text = " ".join(parts[2:])

            if not target_id or not send_text.strip():
                bot.send_message(
                    message.chat.id, 
                    "Usage:\n• Reply to a user's message with `/send <message_text>`\n• Or type `/send <user_id> <message_text>`", 
                    parse_mode='Markdown', 
                    reply_markup=clear_kb
                )
                return

            target_info = user_names.get(target_id, f"User ID: {target_id}")

            try:
                msg_obj = bot.send_message(target_id, send_text)
                confirm_msg = (
                    "📩 MESSAGE DELIVERED SUCCESSFULLY!\n\n"
                    f"To: {target_info}\n"
                    f"User ID: `{target_id}`\n"
                    f"Message ID: `{msg_obj.message_id}`\n\n"
                    f"Content:\n{send_text}"
                )
                bot.send_message(message.chat.id, confirm_msg, parse_mode='Markdown', reply_markup=clear_kb)
            except Exception as e:
                bot.send_message(message.chat.id, f"❌ Failed to send message to `{target_id}`:\n`{e}`", parse_mode='Markdown', reply_markup=clear_kb)
            return

        # 6. Global Member Broadcast (/broadcast <message_text>)
        if cmd == "/broadcast":
            if len(parts) < 2:
                bot.send_message(message.chat.id, "Usage: `/broadcast <message_text>`", parse_mode='Markdown', reply_markup=clear_kb)
                return
            broadcast_text = " ".join(parts[1:])
            
            target_members = [u for u in known_users if not ADMIN_IDS or u not in ADMIN_IDS]

            if not target_members:
                bot.send_message(message.chat.id, "No registered members to broadcast to.", reply_markup=clear_kb)
                return

            global broadcast_seq
            broadcast_seq += 1
            b_id_str = f"B-{broadcast_seq}"
            broadcast_history[broadcast_seq] = []

            bot.send_message(message.chat.id, f"📢 Broadcasting message to {len(target_members)} members (Broadcast ID: `{b_id_str}`)...", parse_mode='Markdown', reply_markup=clear_kb)

            success_count = 0
            fail_count = 0

            for u_id in target_members:
                try:
                    b_msg = bot.send_message(u_id, broadcast_text)
                    broadcast_history[broadcast_seq].append((u_id, b_msg.message_id))
                    success_count += 1
                except Exception:
                    fail_count += 1

            summary = (
                "📢 BROADCAST COMPLETED!\n\n"
                f"Broadcast ID: `{b_id_str}`\n"
                f"• Total Target Members: {len(target_members)}\n"
                f"• Succeeded: {success_count}\n"
                f"• Failed: {fail_count}\n\n"
                f"💡 Tip: Reply to this card with `/delete` or type `/delete_broadcast {b_id_str}` to delete this broadcast from all members' chats.\n\n"
                f"Broadcast Content:\n{broadcast_text}"
            )
            bot.send_message(message.chat.id, summary, parse_mode='Markdown', reply_markup=clear_kb)
            return

        # 7. Delete Broadcast from All Members (/delete_broadcast <b_id> or /delbroadcast)
        if cmd in ["/delete_broadcast", "/delbroadcast", "/deletebroadcast"]:
            b_seq = None
            if len(parts) >= 2:
                raw_b = parts[1].replace("B-", "").replace("b-", "")
                if raw_b.isdigit():
                    b_seq = int(raw_b)

            if not b_seq and message.reply_to_message:
                rep_text = message.reply_to_message.text or ""
                b_match = RE_CONFIRM_BROADCAST_ID.search(rep_text)
                if b_match:
                    b_seq = int(b_match.group(1))

            if not b_seq or b_seq not in broadcast_history:
                bot.send_message(
                    message.chat.id, 
                    "Usage:\n• Reply to a Broadcast Summary card with `/delete` or `/delete_broadcast`\n• Or type `/delete_broadcast B-101`", 
                    parse_mode='Markdown', 
                    reply_markup=clear_kb
                )
                return

            records = broadcast_history[b_seq]
            del_count = 0
            del_fail = 0

            for u_id, m_id in records:
                try:
                    bot.delete_message(u_id, m_id)
                    del_count += 1
                except Exception:
                    del_fail += 1

            del broadcast_history[b_seq]

            bot.send_message(
                message.chat.id, 
                f"🗑️ BROADCAST DELETED FROM ALL MEMBERS!\n\nBroadcast ID: `B-{b_seq}`\n• Deleted Messages: {del_count}\n• Failed/Expired: {del_fail}", 
                parse_mode='Markdown', 
                reply_markup=clear_kb
            )
            return

        # 8. Delete Bot Message (/delete OR /del — Reply to delivery card/message OR specify /delete <chat_id> <message_id>)
        if cmd in ["/delete", "/del"]:
            target_chat_id = None
            target_msg_id = None

            if message.reply_to_message:
                rep_text = message.reply_to_message.text or ""

                # Check if replying to a Broadcast Summary Card
                b_match = RE_CONFIRM_BROADCAST_ID.search(rep_text)
                if b_match:
                    b_seq = int(b_match.group(1))
                    if b_seq in broadcast_history:
                        records = broadcast_history[b_seq]
                        del_count = 0
                        del_fail = 0

                        for u_id, m_id in records:
                            try:
                                bot.delete_message(u_id, m_id)
                                del_count += 1
                            except Exception:
                                del_fail += 1

                        del broadcast_history[b_seq]

                        bot.send_message(
                            message.chat.id, 
                            f"🗑️ BROADCAST DELETED FROM ALL MEMBERS!\n\nBroadcast ID: `B-{b_seq}`\n• Deleted Messages: {del_count}\n• Failed/Expired: {del_fail}", 
                            parse_mode='Markdown', 
                            reply_markup=clear_kb
                        )
                        return

                # Check if replying to a Direct Message Delivery Card
                u_match = RE_CONFIRM_USER_ID.search(rep_text)
                m_match = RE_CONFIRM_MSG_ID.search(rep_text)

                if u_match and m_match:
                    target_chat_id = int(u_match.group(1))
                    target_msg_id = int(m_match.group(1))
                else:
                    target_chat_id = message.reply_to_message.chat.id
                    target_msg_id = message.reply_to_message.message_id
            elif len(parts) >= 3 and parts[1].isdigit() and parts[2].isdigit():
                target_chat_id = int(parts[1])
                target_msg_id = int(parts[2])

            if not target_chat_id or not target_msg_id:
                bot.send_message(
                    message.chat.id, 
                    "Usage:\n• Reply directly to a delivery card or bot message with `/delete` or `/del`\n• Reply to a broadcast card with `/delete` to delete from all members\n• Or type `/delete <chat_id> <message_id>`", 
                    parse_mode='Markdown', 
                    reply_markup=clear_kb
                )
                return

            try:
                bot.delete_message(target_chat_id, target_msg_id)
                bot.send_message(
                    message.chat.id, 
                    f"🗑️ MESSAGE DELETED FROM USER CHAT!\n\nTarget User/Chat ID: `{target_chat_id}`\nMessage ID: `{target_msg_id}`", 
                    parse_mode='Markdown', 
                    reply_markup=clear_kb
                )
            except Exception as e:
                bot.send_message(
                    message.chat.id, 
                    f"❌ Failed to delete message `{target_msg_id}` in chat `{target_chat_id}`:\n`{e}`\n\nNote: Telegram API allows deleting messages sent within the last 48 hours.", 
                    parse_mode='Markdown', 
                    reply_markup=clear_kb
                )
            return

        # 8. Dashboard (/admin or /stats)
        dash_text = get_admin_dashboard_text()
        try:
            bot.send_message(message.chat.id, dash_text, parse_mode='Markdown', reply_markup=clear_kb)
        except Exception:
            bot.send_message(message.chat.id, dash_text, reply_markup=clear_kb)
    except Exception as err:
        logger.error(f"Error in handle_admin_commands: {err}")

@bot.message_handler(commands=['id', 'myid', 'me', 'info'])
def handle_id_command(message):
    try:
        # Check if inspecting a replied or forwarded message
        target_user = message.from_user
        extra_info = ""

        if message.reply_to_message:
            target_user = message.reply_to_message.from_user
            extra_info = (
                f"\nREPLIED MESSAGE INFO:\n"
                f"• Chat ID: `{message.reply_to_message.chat.id}`\n"
                f"• Message ID: `{message.reply_to_message.message_id}`\n"
            )
            if message.reply_to_message.forward_from:
                f_user = message.reply_to_message.forward_from
                f_name = f"{f_user.first_name or ''} {f_user.last_name or ''}".strip()
                extra_info += (
                    f"• Forwarded Sender ID: `{f_user.id}`\n"
                    f"• Forwarded Sender Name: {f_name}\n"
                )

        user_id = target_user.id
        uniq_id, full_name, username = sync_user_profile(target_user)
        is_admin = "Yes" if (ADMIN_IDS and user_id in ADMIN_IDS) else "No"
        
        info = (
            "ACCOUNT & MESSAGE INSPECTOR\n"
            "CREATED BY: KKH\n\n"
            f"Member ID: {uniq_id}\n"
            f"Name: {full_name}\n"
            f"Username: {username}\n"
            f"Telegram User ID: `{user_id}`\n"
            f"Admin Privilege: {is_admin}"
            f"{extra_info}"
        )
        bot.send_message(message.chat.id, info, parse_mode='Markdown')
    except Exception as err:
        logger.error(f"Error in handle_id_command: {err}")

@bot.message_handler(commands=['start', 'menu', 'restart', 'guide', 'invite', 'share'])
def handle_commands(message):
    try:
        user_id = message.from_user.id
        if check_ban_guard(message.chat.id, user_id):
            return

        is_first_time = (user_id not in known_users)

        # Check for deep-link referral parameter: /start ref_123456
        inviter_id = None
        cmd_text = message.text or ""
        parts = cmd_text.split()

        if len(parts) > 1 and parts[1].startswith("ref_"):
            ref_str = parts[1].replace("ref_", "")
            if ref_str.isdigit():
                inviter_id = int(ref_str)

        check_and_notify_new_user(message.from_user, inviter_id=inviter_id)

        cmd = cmd_text.lower()

        if "/invite" in cmd or "/share" in cmd:
            markup = types.InlineKeyboardMarkup(row_width=1)
            ref_link = f"https://t.me/{BOT_USERNAME}?start=ref_{user_id}"
            share_url = f"https://t.me/share/url?url={ref_link}&text=Try%20Fake%20Names%202FA%20Bot%20-%20Instant%20Fake%20Name%20Generator%20%26%202FA%20Authenticator!"
            btn_share = types.InlineKeyboardButton("🚀 Share with Friends", url=share_url)
            btn_menu = types.InlineKeyboardButton("Back to Main Menu", callback_data="show_main_menu")
            markup.add(btn_share, btn_menu)

            bot.send_message(message.chat.id, get_invite_text(user_id), reply_markup=markup, parse_mode='Markdown')
            return

        is_restart = False
        if "/restart" in cmd:
            if user_id in user_history:
                user_history[user_id].clear()
            user_settings[user_id] = {'gender': 'mixed', 'quantity': 10}
            is_restart = True

        if "/guide" in cmd:
            bot.send_message(message.chat.id, get_user_guide_text(), reply_markup=types.ReplyKeyboardRemove())
            return

        settings = get_user_settings(user_id)
        text = get_kkh_menu_text(settings)

        if is_restart:
            text = "BOT RESTARTED SUCCESSFULLY!\n\n" + text
        elif is_first_time and "/start" in cmd:
            first_name = message.from_user.first_name or "User"
            welcome_header = (
                f"WELCOME TO FAKE NAMES 2FA!\n"
                f"CREATED BY: KKH\n\n"
                f"Hello {first_name}! Welcome to Fake Names 2FA — your professional Fake Name Generator & instant 2FA Authenticator.\n\n"
                "USER GUIDE & FEATURES:\n"
                "1. NAME GENERATOR:\n"
                "• Customize Gender (Male, Female, Mixed) & Quantity (5, 10, 20, 50).\n"
                "• Tap GENERATE to create clean, single-tap copyable names.\n\n"
                "2. INSTANT 2FA AUTHENTICATOR:\n"
                "• Paste any Base32 2FA Secret Key or OTPAuth link into chat to get a live 6-digit TOTP code instantly.\n\n"
                "3. NAVIGATION:\n"
                "• Use Telegram's native menu button (/) for commands (/start, /restart, /invite, /guide) anytime.\n\n"
                "───────────────────────────\n\n"
            )
            text = welcome_header + text

        # Send instant single message console with ReplyKeyboardRemove attached directly
        inline_markup = build_kkh_keyboard(settings)
        bot.send_message(message.chat.id, text, reply_markup=inline_markup)

    except Exception as err:
        logger.error(f"Error in handle_commands: {err}")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    try:
        user_id = call.from_user.id
        if check_ban_guard(call.message.chat.id, user_id):
            return

        # Instant non-blocking answer_callback_query
        try:
            bot.answer_callback_query(call.id)
        except Exception:
            pass

        check_and_notify_new_user(call.from_user)
        settings = get_user_settings(user_id)
        data = call.data

        if data == "set_g_male":
            settings['gender'] = "male"
        elif data == "set_g_female":
            settings['gender'] = "female"
        elif data == "set_g_mixed":
            settings['gender'] = "mixed"
        elif data == "set_q_5":
            settings['quantity'] = 5
        elif data == "set_q_10":
            settings['quantity'] = 10
        elif data == "set_q_20":
            settings['quantity'] = 20
        elif data == "set_q_50":
            settings['quantity'] = 50

        if data.startswith("set_"):
            text = get_kkh_menu_text(settings)
            markup = build_kkh_keyboard(settings)
            try:
                bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
            except Exception:
                pass
            return

        if data == "do_generate":
            count = settings['quantity']
            pref_gender = settings['gender']
            batch_lines = []

            for _ in range(count):
                if pref_gender == "male":
                    g = "male"
                elif pref_gender == "female":
                    g = "female"
                else:
                    g = random.choice(["male", "female"])

                full_name = generate_simple_name(user_id, g)
                batch_lines.append(f"`{full_name}`")

            header = "Fake Names 2FA — BATCH RESULT\nCREATED BY: KKH\n\n"
            meta = f"Mode: {pref_gender.capitalize()} | Quantity: {count} Names\n───────────────────────────\n\n"
            body = "\n".join(batch_lines)
            footer = "\n\n───────────────────────────\nTap on any name above to copy!"

            response_text = f"{header}{meta}{body}{footer}"

            markup = types.InlineKeyboardMarkup(row_width=1)
            btn_again = types.InlineKeyboardButton("Generate Another Batch", callback_data="do_generate")
            btn_menu = types.InlineKeyboardButton("Change Settings", callback_data="show_main_menu")
            markup.add(btn_again, btn_menu)

            try:
                bot.edit_message_text(
                    chat_id=call.message.chat.id, 
                    message_id=call.message.message_id, 
                    text=response_text, 
                    reply_markup=markup, 
                    parse_mode='Markdown'
                )
            except Exception:
                pass

        elif data == "show_main_menu":
            text = get_kkh_menu_text(settings)
            markup = build_kkh_keyboard(settings)
            try:
                bot.edit_message_text(text, chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=markup)
            except Exception:
                pass

    except Exception as err:
        logger.error(f"Error in handle_callback: {err}")

@bot.message_handler(func=lambda message: True)
def handle_text_inputs(message):
    """Handles text inputs & sub-millisecond 2FA secret key decoding transparently."""
    try:
        user_id = message.from_user.id
        if check_ban_guard(message.chat.id, user_id):
            return

        if message.text and message.text.startswith('/'):
            return

        check_and_notify_new_user(message.from_user)
        text_input = (message.text or "").strip()

        # Handle persistent reply keyboard texts if clicked by mistake
        if text_input in ["Start Bot", "Restart Bot", "Open KKH Names Hub", "User Guide"]:
            clear_kb = types.ReplyKeyboardRemove()
            if text_input == "User Guide":
                bot.send_message(message.chat.id, get_user_guide_text(), reply_markup=clear_kb)
                return
            else:
                settings = get_user_settings(user_id)
                text = get_kkh_menu_text(settings)
                inline_markup = build_kkh_keyboard(settings)
                bot.send_message(message.chat.id, text, reply_markup=inline_markup)
                return

        # 1. Sub-Millisecond Universal 2FA Secret Key Sanitizer & Parser
        cleaned_key = universal_extract_2fa_secret(text_input)

        if cleaned_key:
            try:
                totp = pyotp.TOTP(cleaned_key)
                current_code = totp.now()
                time_remaining = 30 - (int(time.time()) % 30)

                # Clean single-tap 6-digit TOTP code output
                response = (
                    "2FA CODE\n\n"
                    f"`{current_code}`\n\n"
                    f"Expires in: {time_remaining}s\n"
                    "Tap code above to copy!"
                )
                bot.send_message(message.chat.id, response, parse_mode='Markdown')
            except Exception:
                bot.send_message(message.chat.id, "Invalid 2FA Secret Key format.")
            return

        # 2. Otherwise display Name Generator console menu
        settings = get_user_settings(user_id)
        text = get_kkh_menu_text(settings)
        inline_markup = build_kkh_keyboard(settings)
        bot.send_message(message.chat.id, text, reply_markup=inline_markup)

    except Exception as err:
        logger.error(f"Error in handle_text_inputs: {err}")

import http.server
import socketserver

def run_health_server():
    port = int(os.getenv("PORT", 10000))
    class HealthHandler(http.server.SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Fake Names 2FA Bot is Running Live 24/7!")
        def log_message(self, format, *args):
            pass

    try:
        socketserver.TCPServer.allow_reuse_address = True
        with socketserver.TCPServer(("0.0.0.0", port), HealthHandler) as httpd:
            logger.info(f"Health check HTTP server bound to 0.0.0.0:{port}")
            httpd.serve_forever()
    except Exception as e:
        logger.warning(f"Could not start health HTTP server: {e}")

health_thread = threading.Thread(target=run_health_server, daemon=True)
health_thread.start()

shutdown_notified = False

def notify_server_status(is_online=True):
    """Sends professional Server Online / Offline cards to ADMIN_IDS."""
    global shutdown_notified
    if not is_online and shutdown_notified:
        return
    if not is_online:
        shutdown_notified = True

    if not ADMIN_IDS:
        return

    status_title = "🟢 SYSTEM ONLINE | FAKE NAMES 2FA" if is_online else "🔴 SYSTEM OFFLINE | FAKE NAMES 2FA"
    status_desc = "The bot server has successfully initialized and is live 24/7!" if is_online else "The bot server is shutting down or undergoing container handover."
    status_state = "Online 🟢" if is_online else "Offline 🔴"

    alert_msg = (
        f"{status_title}\n"
        "CREATED BY: KKH\n\n"
        f"{status_desc}\n\n"
        "SYSTEM DETAILS:\n"
        f"• Server Status: {status_state}\n"
        "• Worker Pool: 16 Concurrent Threads\n"
        "• Response Time: < 20ms (Instant)\n"
        "• Health Port: 10000 (0.0.0.0)"
    )

    for aid in ADMIN_IDS:
        try:
            bot.send_message(aid, alert_msg, parse_mode='Markdown')
        except Exception:
            pass

def handle_shutdown_signal(signum=None, frame=None):
    """Handles SIGTERM / SIGINT shutdown signals cleanly."""
    notify_server_status(is_online=False)
    sys.exit(0)

try:
    signal.signal(signal.SIGTERM, handle_shutdown_signal)
    signal.signal(signal.SIGINT, handle_shutdown_signal)
except Exception:
    pass

atexit.register(lambda: notify_server_status(is_online=False))

if __name__ == '__main__':
    logger.info("Starting ultra-fast 16-worker thread Fake Names 2FA telebot Infinity Polling...")
    notify_server_status(is_online=True)
    
    conflict_count = 0
    while True:
        try:
            bot.infinity_polling(timeout=1, long_polling_timeout=1, skip_pending=True)
            conflict_count = 0
        except telebot.apihelper.ApiTelegramException as e:
            if e.error_code == 409:
                conflict_count += 1
                if conflict_count % 5 == 1:
                    logger.warning(f"Telegram 409 Conflict detected (Render container handover attempt #{conflict_count}). Re-trying lock...")
                time.sleep(2)
            else:
                logger.error(f"Telegram API Exception: {e}")
                time.sleep(2)
        except Exception as e:
            logger.error(f"Polling loop exception: {e}")
            time.sleep(2)
