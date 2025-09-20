import asyncio
import os
import sqlite3
import time
from contextlib import closing
from typing import List

import httpx
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, BufferedInputFile
from aiogram.filters import CommandStart, Command
from aiogram.enums.parse_mode import ParseMode
from aiogram.client.default import DefaultBotProperties

from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_IDS = list(map(int, os.getenv("ADMIN_IDS", "").split(",")))
API_URL = "https://vkrdownloader.xyz/server/"
API_KEY = "vkrdownloader"

DB_FILE = "users.db"

def init_db():
    with closing(sqlite3.connect(DB_FILE)) as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY, username TEXT, full_name TEXT)"
        )
        conn.commit()

async def add_user(user_id: int, username: str | None, full_name: str):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        lambda: sqlite3.connect(DB_FILE)
        .execute(
            "INSERT OR IGNORE INTO users(user_id,username,full_name) VALUES(?,?,?)",
            (user_id, username, full_name),
        )
        .connection.commit(),
    )

async def get_all_users() -> List[int]:
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        lambda: [
            row[0]
            for row in sqlite3.connect(DB_FILE)
            .execute("SELECT user_id FROM users")
            .fetchall()
        ],
    )

async def fetch_insta_media(link: str) -> dict | None:
    params = {"api_key": API_KEY, "vkr": link}
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(API_URL, params=params)
            if resp.status_code != 200:
                return None
            data = resp.json()
            if not data.get("data") or not data["data"].get("downloads"):
                return None
            return data
    except Exception:
        return None

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await add_user(
        message.from_user.id,
        message.from_user.username,
        message.from_user.full_name or "",
    )
    await message.answer("👋 Welcome! Send me any Instagram link and I'll return the media.")

@dp.message(Command("stats"))
async def cmd_stats(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    users = await get_all_users()
    await message.answer(f"📊 Total users: <b>{len(users)}</b>")

@dp.message(Command("bcast"))
async def cmd_bcast(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    text = message.text.partition(" ")[2]
    if not text:
        await message.answer("Usage: <code>/bcast your message</code>")
        return
    users = await get_all_users()
    sent = 0
    for uid in users:
        try:
            await bot.send_message(uid, text)
            sent += 1
            await asyncio.sleep(0.05)
        except Exception:
            pass
    await message.answer(f"✅ Broadcast sent to <b>{sent}</b> users.")

async def download_with_progress(url: str, msg: Message, label: str) -> bytes | None:
    try:
        async with httpx.AsyncClient(timeout=120) as client:
            async with client.stream("GET", url) as resp:
                if resp.status_code != 200:
                    return None
                total = int(resp.headers.get("content-length", 0))
                if total == 0:
                    return None
                chunks = b""
                start = time.time()
                last_update = 0
                done = 0
                async for chunk in resp.aiter_bytes(1024 * 64):
                    chunks += chunk
                    done += len(chunk)
                    now = time.time()
                    if now - last_update >= 2:
                        last_update = now
                        pct = int(done * 100 / total)
                        elapsed = now - start
                        eta = (total - done) * elapsed / done if done else 0
                        eta_str = f"{int(eta)}s" if eta < 3600 else f"{int(eta//60)}m"
                        try:
                            await msg.edit_text(f"{label} {pct}%  ETA: {eta_str}")
                        except Exception:
                            pass
                return chunks
    except Exception:
        return None

@dp.message(F.text.contains("instagram.com"))
async def download_insta(message: Message):
    link = message.text.strip()
    wait = await message.reply("⏳ Fetching media…")
    data = await fetch_insta_media(link)
    if not data:
        return await wait.edit_text("❌ Could not retrieve media.")
    downloads = data["data"]["downloads"]
    best_video = None
    for item in downloads:
        url = item.get("url")
        if not url:
            continue
        ext = (item.get("ext") or "mp4").lower()
        if ext in {"mp4", "webm"}:
            best_video = url
            break
    if not best_video:
        return await wait.edit_text("❌ No video found.")
    await wait.edit_text("📥 Downloading…")
    media_bytes = await download_with_progress(best_video, wait, "📥")
    if not media_bytes:
        return await wait.edit_text("❌ Download failed.")
    await wait.edit_text("📤 Uploading…")
    filename = f"insta_{message.message_id}.mp4"
    file_obj = BufferedInputFile(media_bytes, filename=filename)
    await message.reply_video(file_obj)
    await wait.delete()

async def main():
    init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
