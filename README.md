
# Instagram Downloader Telegram Bot 🚀

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Contributors](https://img.shields.io/badge/contributors-1-lightgrey)

A lightning-fast Telegram bot that downloads **Instagram Reels, Posts & Profile Pictures** in one click.  
Built with **aiogram**, **SQLite**, **httpx** and **zero bloat**.

---

## ✨ Features
- 📥 **Reels / Posts / Profile Pics** – any public URL  
- ⚡ **Progress bar** – live % + ETA while downloading / uploading  
- 📊 **Admin commands** – `/stats` & `/bcast` (silent for non-admins)  
- 🗄️ **SQLite** – single file DB, no Redis headache  
- 🧘 **Minimal deps** – only `aiogram`, `httpx`, `aiosqlite`  
- 🌍 **Env-driven** – 100 % configurable via `.env`

---

## 🛠️ 1-Line Install
```bash
git clone https://github.com/Harshit-shrivastav/Instagram-Downloader-Bot.git insta-bot && cd insta-bot
python3 -m venv venv && source venv/bin/activate
pip install aiogram==3.1.1 httpx aiosqlite
```

---

⚙️ Configuration
Create `.env` in the root folder:

```ini
BOT_TOKEN=123456:ABC-DEF1234
ADMIN_IDS=123456789,987654321   # comma-separated Telegram user IDs
```

---

🚀 Run

```bash
python3 main.py
```

---

📲 How to Use
1. Start the bot → `/start`  
2. Send any Instagram link:  
   - `https://www.instagram.com/reel/ABCxyz/`  
   - `https://www.instagram.com/p/DEFuvw/`  
   - `https://www.instagram.com/username/`  

---

🤖 Commands

Command	Who	Description	
`/start`	everyone	registers user & shows welcome msg	
`/stats`	admin only	total users stored in DB	
`/bcast`	admin only	`<text>` – sends message to every user	

---

🗃️ Database
Single file `users.db` (SQLite) – auto-created on first run.

Schema: `user_id INTEGER PK, username TEXT, full_name TEXT`

---

📦 Requirements

```
aiogram==3.1.1
httpx
aiosqlite
```

(All latest stable versions work on Python 3.8+)

---

📝 Logging
Errors printed to console – no extra log file spam.

Run with `DEBUG=1 python3 main.py` for verbose output.

---

❤️ Support
Star ⭐ the repo if it saves your day!

Issues / PRs welcome.
