import asyncio
from logs import logging
from pyrogram import Client
from vars import API_ID, API_HASH, BOT_TOKEN



loop = asyncio.get_event_loop()





bot = Client(
    ":Uploader:",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    sleep_threshold=120,
    workers=10
)
async def info_bot():
    global BOT_ID, BOT_NAME, BOT_USERNAME
    await bot.start()
    getme = await bot.get_me()
    BOT_ID = getme.id
    BOT_USERNAME = getme.username
    if getme.last_name:
        BOT_NAME = getme.first_name + " " + getme.last_name
    else:
        BOT_NAME = getme.first_name


loop.run_until_complete(info_bot())
