import os
import asyncio
import yt_dlp

from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream

API_ID = 34801155
API_HASH = "d7846c4d0f2c343dd5b67c80d45409e8"

BOT_TOKEN = "8781839976:AAGDkmLDvjlaXDnTtJw2KdD9i6gCyjnHGL4"

# Music account ki session
SESSION_NAME = "BQITBgMAfqYnHd4mqGD19Dds6izs_XwprSuXJ1l2wPLFtLKver_F9m92V1mtHiTVAUSAuwlj4bl0NzIVG-vGwIRF0wk9WalgR1b2maJZzJbWrBkTIbMK9LjWJJn-cxP6w2Aw_jAi1Nxx7a7fUM5oykm3-cgyOhZmZrQJfHpJmeWrOCqnv40MJtwdcDxxSiwhwLDmV4mlXZQFq_A8qkTw5Je2hW3SQB1g8zhhiu6z4IvKh3li0wtXiDUs5I-OtaFeTJvpObSI3zk-3ydLFj9XwNUOlN7qDwTldc8h9ukdsi6RVZX7EcqAuu2__VYxaiqmCuCXfC7aUe5a5EX3F45uQUUpFpAIDAAAAAGJTBUgAA"

app = Client(
    "music_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# Voice chat ke liye MTProto user account
user = Client(
    SESSION_NAME,
    api_id=API_ID,
    api_hash=API_HASH
)

call = PyTgCalls(user)

queues = {}


def get_audio(query):
    """
    YouTube/search se audio URL nikalega.
    """

    options = {
        "format": "bestaudio/best",
        "noplaylist": True,
        "quiet": True,
        "default_search": "ytsearch1",
        "outtmpl": "downloads/%(id)s.%(ext)s",
    }

    os.makedirs("downloads", exist_ok=True)

    with yt_dlp.YoutubeDL(options) as ydl:
        info = ydl.extract_info(query, download=True)

        if "entries" in info:
            info = info["entries"][0]

        return info["title"], ydl.prepare_filename(info)


@app.on_message(filters.command("start"))
async def start(_, message: Message):

    await message.reply_text(
        "🎵 **Music Bot Ready**\n\n"
        "/play Song Name\n"
        "/pause\n"
        "/resume\n"
        "/skip\n"
        "/stop\n"
        "/queue"
    )


@app.on_message(filters.command("play"))
async def play(_, message: Message):

    if len(message.command) < 2:
        await message.reply_text(
            "❌ Song name ya YouTube link bhejo.\n\n"
            "Example:\n"
            "`/play Arijit Singh Tum Hi Ho`"
        )
        return

    chat_id = message.chat.id
    query = " ".join(message.command[1:])

    msg = await message.reply_text("🔎 Song search ho raha hai...")

    try:
        title, filename = await asyncio.to_thread(
            get_audio,
            query
        )

        if chat_id not in queues:
            queues[chat_id] = []

        queues[chat_id].append(
            {
                "title": title,
                "file": filename
            }
        )

        # Voice Chat join/play
        if len(queues[chat_id]) == 1:

            await call.play(
                chat_id,
                MediaStream(filename)
            )

            await msg.edit_text(
                f"▶️ **Playing Now**\n\n🎵 {title}"
            )

        else:

            position = len(queues[chat_id])

            await msg.edit_text(
                f"✅ **Queue mein add ho gaya**\n\n"
                f"🎵 {title}\n"
                f"📌 Position: {position}"
            )

    except Exception as e:

        await msg.edit_text(
            f"❌ Error:\n`{e}`"
        )


@app.on_message(filters.command("pause"))
async def pause(_, message):

    try:
        await call.pause(message.chat.id)

        await message.reply_text(
            "⏸️ Music paused."
        )

    except Exception as e:

        await message.reply_text(
            f"❌ {e}"
        )


@app.on_message(filters.command("resume"))
async def resume(_, message):

    try:
        await call.resume(message.chat.id)

        await message.reply_text(
            "▶️ Music resumed."
        )

    except Exception as e:

        await message.reply_text(
            f"❌ {e}"
        )


@app.on_message(filters.command("stop"))
async def stop(_, message):

    chat_id = message.chat.id

    try:

        await call.leave_call(chat_id)

        queues.pop(chat_id, None)

        await message.reply_text(
            "⏹️ Music stopped.\n"
            "Bot voice chat se leave ho gaya."
        )

    except Exception as e:

        await message.reply_text(
            f"❌ {e}"
        )


@app.on_message(filters.command("queue"))
async def queue(_, message):

    chat_id = message.chat.id

    if chat_id not in queues or not queues[chat_id]:

        await message.reply_text(
            "📭 Queue empty hai."
        )
        return

    text = "🎵 **Music Queue**\n\n"

    for i, song in enumerate(queues[chat_id], 1):

        text += f"{i}. {song['title']}\n"

    await message.reply_text(text)


async def main():

    await app.start()
    await user.start()

    await call.start()

    print("🤖 Music Bot Started")

    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
