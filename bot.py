import asyncio
import json
import os
from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from yt_dlp import YoutubeDL

# --- अपनी डिटेल्स यहाँ भरें ---
API_ID = 34801155
API_HASH = "d7846c4d0f2c343dd5b67c80d45409e8"
BOT_TOKEN = "8781839976:AAGDkmLDvjlaXDnTtJw2KdD9i6gCyjnHGL4"
SESSION_STRING = "BQITBgMAfqYnHd4mqGD19Dds6izs_XwprSuXJ1l2wPLFtLKver_F9m92V1mtHiTVAUSAuwlj4bl0NzIVG-vGwIRF0wk9WalgR1b2maJZzJbWrBkTIbMK9LjWJJn-cxP6w2Aw_jAi1Nxx7a7fUM5oykm3-cgyOhZmZrQJfHpJmeWrOCqnv40MJtwdcDxxSiwhwLDmV4mlXZQFq_A8qkTw5Je2hW3SQB1g8zhhiu6z4IvKh3li0wtXiDUs5I-OtaFeTJvpObSI3zk-3ydLFj9XwNUOlN7qDwTldc8h9ukdsi6RVZX7EcqAuu2__VYxaiqmCuCXfC7aUe5a5EX3F45uQUUpFpAIDAAAAAGJTBUgAA"

bot = Client("MusicBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user = Client("UserAssistant", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)
call_py = PyTgCalls(user)

QUEUE_FILE = "queue.json"

def load_queue():
    if os.path.exists(QUEUE_FILE):
        try:
            with open(QUEUE_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_queue(data):
    with open(QUEUE_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_yt_audio(query):
    ydl_opts = {'format': 'bestaudio/best', 'quiet': True, 'default_search': 'ytsearch'}
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=False)
        if 'entries' in info:
            info = info['entries'][0]
        return info['url'], info['title']

@bot.on_message(filters.command("play") & filters.group)
async def play_command(_, message):
    if len(message.command) < 2:
        return await message.reply("❌ **गाने का नाम लिखें!**\nउदा: `/play Kesariya`")
    
    query = message.text.split(None, 1)[1]
    chat_id = str(message.chat.id)
    msg = await message.reply("🔎 **गाना खोजा जा रहा है...**")
    
    try:
        audio_url, title = get_yt_audio(query)
        
        queue_data = load_queue()
        queue_data[chat_id] = {"url": audio_url, "title": title}
        save_queue(queue_data)

        await call_py.play(
            message.chat.id,
            MediaStream(audio_url)
        )
        await msg.edit(f"▶️ **प्ले हो रहा है:** `{title}`\n*(डेटा JSON में सुरक्षित है)*")
    except Exception as e:
        await msg.edit(f"❌ **Error:** {str(e)}")

@bot.on_message(filters.command("pause") & filters.group)
async def pause_command(_, message):
    try:
        await call_py.pause_stream(message.chat.id)
        await message.reply("⏸️ **गाना पॉज़ कर दिया गया है।**")
    except Exception as e:
        await message.reply(f"❌ **Error:** {str(e)}")

@bot.on_message(filters.command("resume") & filters.group)
async def resume_command(_, message):
    try:
        await call_py.resume_stream(message.chat.id)
        await message.reply("▶️ **गाना फिर से शुरू हो गया।**")
    except Exception as e:
        await message.reply(f"❌ **Error:** {str(e)}")

@bot.on_message(filters.command("stop") & filters.group)
async def stop_command(_, message):
    chat_id = str(message.chat.id)
    try:
        await call_py.leave_call(message.chat.id)
        
        queue_data = load_queue()
        if chat_id in queue_data:
            del queue_data[chat_id]
            save_queue(queue_data)

        await message.reply("⏹️ **गाना बंद कर दिया गया और सभी डेटा साफ़ कर दिया गया।**")
    except Exception as e:
        await message.reply(f"❌ **Error:** {str(e)}")

async def start_bot():
    await bot.start()
    await user.start()
    await call_py.start()
    print("✅ Music Bot सफलतापूर्वक चालू हो गया है!")
    
    queue_data = load_queue()
    for chat_id, data in queue_data.items():
        try:
            await call_py.play(int(chat_id), MediaStream(data["url"]))
            print(f"🔄 पुराना गाना रीस्टोर हुआ: {data['title']} (Chat: {chat_id})")
        except Exception as e:
            print(f"⚠️ चैट {chat_id} पर गाना रीस्टोर करने में समस्या: {e}")

    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(start_bot())
    
