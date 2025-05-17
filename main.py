import os
import re
import sys
import json
import time
import asyncio
import aiohttp
import aiofiles
import requests
import subprocess
import hashlib
import os
from pymongo import MongoClient
import core as helper
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64decode
import yt_dlp
from utils import progress_bar
from vars import API_ID, API_HASH, BOT_TOKEN, OWNER
from init import bot 
from aiohttp import ClientSession
from subprocess import getstatusoutput
import shutil
from PIL import Image
from io import BytesIO
from pyrogram import Client, filters
import mmap
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from pyrogram.errors.exceptions.bad_request_400 import StickerEmojiInvalid
from pyrogram.types.messages_and_media import message
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# MongoDB setup
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://abcd:abcdeas@cluster0.flillxf.mongodb.net/?retryWrites=true&w=majority")
DUMP_CHAT =  -1002649840760 # e.g., '@dump_channel'

mongo_client = MongoClient(MONGO_URI)
db = mongo_client["video_bot"]
collection = db["videos"]
collection_doc= db["documents"]

async def compute_sha256(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            sha256.update(chunk)
    return sha256.hexdigest()

async def cw_pdf_store(bot, m, url, cc1, name, helper):
    try:
        # 1. Check by filename
        existing = collection_doc.find_one({"name": name})
        if existing:
            await bot.get_chat(DUMP_CHAT)
            await bot.copy_message(
                chat_id=m.chat.id,
                caption = cc1,
                from_chat_id=DUMP_CHAT,
                message_id=existing["dump_msg_id"]
            )
            print(f"✅ Document '{name}' matched by name. Forwarded from dump.")
            return

        # 2. Show download message
        show = f"<blockquote>Ｄｏｗｎｌｏａｄｉｎｇ Document... »\n\nName: {name}</blockquote>"
        prog = await m.reply_text(show)

        # 3. Download document
        filename = await helper.download(url, name)
        
        # Step 4: Hash and check by hash
        file_hash = await compute_sha256(filename)
        hash_entry = collection_doc.find_one({"hash": file_hash})
        if hash_entry:
            await prog.delete(True)
            await bot.get_chat(DUMP_CHAT)
            await bot.copy_message(
                chat_id=m.chat.id,
                caption = cc1,
                from_chat_id=DUMP_CHAT,
                message_id=hash_entry["dump_msg_id"]
            )
            os.remove(filename)
            print(f"✅ File '{name}' matched by hash. Forwarded from dump.")
            return

        

        # 5. Send document to user
        await prog.delete(True)
        sent_msg = await bot.send_document(chat_id=m.chat.id, document=filename, caption=cc1)
        if sent_msg is None:
            await m.reply_text("❌ Upload failed.")
            os.remove(filename)
            return

        # 6. Forward to dump
        await bot.get_chat(DUMP_CHAT)
        dump_msg = await bot.copy_message(
            chat_id=DUMP_CHAT,
            from_chat_id=m.chat.id,
            message_id=sent_msg.id
        )

        # 7. Store in DB
        collection_doc.insert_one({
            "name": name,
            "hash": file_hash,
            "dump_msg_id": dump_msg.id
        })

        os.remove(filename)
        print(f"🆕 Document '{name}' uploaded and stored.")
    
    except Exception as e:
        await m.reply_text(f"❌ Error: {e}")
        print(f"[ERROR - DOC] {e}")
async def encrypted_video(bot, m, url, key, cmd, name, raw_text2, cc, thumb, helper):
    try:
        # Step 1: Check by filename (fast deduplication)
        existing = collection.find_one({"name": name})
        if existing:
            await bot.get_chat(DUMP_CHAT)  # Make sure bot knows the peer
            await bot.copy_message(
                chat_id=m.chat.id,
                caption=cc,
                from_chat_id=DUMP_CHAT,
                message_id=existing["dump_msg_id"]
            )
            print(f"✅ File '{name}' matched by name. Forwarded from dump.")
            return

        # Step 2: Show progress message
        show = f"<blockquote>Ｄｏｗｎｌｏａｄｉｎｇ... »\n\nName: {name}\nQuality » {raw_text2}</blockquote>"
        prog = await m.reply_text(show)

        # Step 3: Download video
        file_path = await helper.download_file(url, name)
        copy = helper.decrypt_file(file_path, key)
        filename = file_path

        # Step 4: Hash and check by hash
        file_hash = await compute_sha256(filename)
        hash_entry = collection.find_one({"hash": file_hash})
        if hash_entry:
            await prog.delete(True)
            await bot.get_chat(DUMP_CHAT)
            await bot.copy_message(
                chat_id=m.chat.id,
                caption = cc,
                from_chat_id=DUMP_CHAT,
                message_id=hash_entry["dump_msg_id"]
            )
            os.remove(filename)
            print(f"✅ File '{name}' matched by hash. Forwarded from dump.")
            return

        # Step 5: Send to user
        await prog.delete(True)
        sent_msg = await helper.send_vid(bot, m, cc, filename, thumb, name, prog)
        if sent_msg is None:
            await m.reply_text("❌ Upload failed.")
            os.remove(filename)
            return

        # Step 6: Copy to dump
        await bot.get_chat(DUMP_CHAT)
        dump_msg = await bot.copy_message(
            chat_id=DUMP_CHAT,
            from_chat_id=m.chat.id,
            message_id=sent_msg.id
        )

        # Step 7: Store metadata in DB
        collection.insert_one({
            "name": name,
            "hash": file_hash,
            "dump_msg_id": dump_msg.id
        })

        os.remove(filename)
        print(f"🆕 Uploaded '{name}' to user and dump. Hash saved.")
    
    except Exception as e:
        await m.reply_text(f"❌ Error: {e}")
        print(f"[ERROR] {e}")
async def download_and_send(bot, m, url, cmd, name, raw_text2, cc, thumb, helper):
    try:
        # Step 1: Check by filename (fast deduplication)
        existing = collection.find_one({"name": name})
        if existing:
            await bot.get_chat(DUMP_CHAT)  # Make sure bot knows the peer
            await bot.copy_message(
                chat_id=m.chat.id,
                caption=cc,
                from_chat_id=DUMP_CHAT,
                message_id=existing["dump_msg_id"]
            )
            print(f"✅ File '{name}' matched by name. Forwarded from dump.")
            return

        # Step 2: Show progress message
        show = f"<blockquote>Ｄｏｗｎｌｏａｄｉｎｇ... »\n\nName: {name}\nQuality » {raw_text2}</blockquote>"
        prog = await m.reply_text(show)

        # Step 3: Download video
        filename = await helper.download_video(url, cmd, name)

        # Step 4: Hash and check by hash
        file_hash = await compute_sha256(filename)
        hash_entry = collection.find_one({"hash": file_hash})
        if hash_entry:
            await prog.delete(True)
            await bot.get_chat(DUMP_CHAT)
            await bot.copy_message(
                chat_id=m.chat.id,
                from_chat_id=DUMP_CHAT,
                message_id=hash_entry["dump_msg_id"]
            )
            os.remove(filename)
            print(f"✅ File '{name}' matched by hash. Forwarded from dump.")
            await prog.delete(True)
            return

        # Step 5: Send to user
        await prog.delete(True)
        sent_msg = await helper.send_vid(bot, m, cc, filename, thumb, name, prog)
        if sent_msg is None:
            await m.reply_text("❌ Upload failed.")
            os.remove(filename)
            return

        # Step 6: Copy to dump
        await bot.get_chat(DUMP_CHAT)
        dump_msg = await bot.copy_message(
            chat_id=DUMP_CHAT,
            from_chat_id=m.chat.id,
            message_id=sent_msg.id
        )

        # Step 7: Store metadata in DB
        collection.insert_one({
            "name": name,
            "hash": file_hash,
            "dump_msg_id": dump_msg.id
        })

        os.remove(filename)
        print(f"🆕 Uploaded '{name}' to user and dump. Hash saved.")
    
    except Exception as e:
        await m.reply_text(f"❌ Error: {e}")
        print(f"[ERROR] {e}")

async def encrypted_pdf_store(bot, m, url, cc1, name, helper, key):
    try:
        # 1. Check by filename
        existing = collection_doc.find_one({"name": name})
        if existing:
            await bot.get_chat(DUMP_CHAT)
            await bot.copy_message(
                chat_id=m.chat.id,
                caption = cc1,
                from_chat_id=DUMP_CHAT,
                message_id=existing["dump_msg_id"]
            )
            print(f"✅ Document '{name}' matched by name. Forwarded from dump.")
            return

        # 2. Show download message
        show = f"<blockquote>Ｄｏｗｎｌｏａｄｉｎｇ Document... »\n\nName: {name}</blockquote>"
        prog = await m.reply_text(show)

        # 3. Download document
        
        file_path = await helper.download_file(url, name)
        copy = helper.decrypt_file(file_path, key)
        filename = file_path
        

        # 4. Compute hash
        file_hash = compute_sha256(filename)
        hash_entry = collection_doc.find_one({"hash": file_hash})
        if hash_entry:
            await prog.delete(True)
            await bot.get_chat(DUMP_CHAT)
            await bot.copy_message(
                chat_id=m.chat.id,
                from_chat_id=DUMP_CHAT,
                message_id=hash_entry["dump_msg_id"]
            )
            os.remove(filename)
            print(f"✅ Document '{name}' matched by hash. Forwarded from dump.")
            await prog.delete(True)
            return

        # 5. Send document to user
        await prog.delete(True)
        sent_msg = await bot.send_document(chat_id=m.chat.id, document=filename, caption=cc1)
        if sent_msg is None:
            await m.reply_text("❌ Upload failed.")
            os.remove(filename)
            return

        # 6. Forward to dump
        await bot.get_chat(DUMP_CHAT)
        dump_msg = await bot.copy_message(
            chat_id=DUMP_CHAT,
            from_chat_id=m.chat.id,
            message_id=sent_msg.id
        )

        # 7. Store in DB
        collection_doc.insert_one({
            "name": name,
            "hash": file_hash,
            "dump_msg_id": dump_msg.id
        })

        os.remove(filename)
        print(f"🆕 Document '{name}' uploaded and stored.")
    
    except Exception as e:
        await m.reply_text(f"❌ Error: {e}")
        print(f"[ERROR - DOC] {e}")
async def pdf_store(bot, m, url, cc1, name):
    try:
        # 1. Check by filename
        existing = collection_doc.find_one({"name": name})
        if existing:
            await bot.get_chat(DUMP_CHAT)
            await bot.copy_message(
                chat_id=m.chat.id,
                caption = cc,
                from_chat_id=DUMP_CHAT,
                message_id=existing["dump_msg_id"]
            )
            print(f"✅ Document '{name}' matched by name. Forwarded from dump.")
            
            return

        # 2. Show download message
        show = f"<blockquote>Ｄｏｗｎｌｏａｄｉｎｇ Document... »\n\nName: {name}</blockquote>"
        prog = await m.reply_text(show)

        # 3. Download document
        filename = await helper.download_file(url, name)
        

        
        # Step 4: Hash and check by hash
        file_hash = await compute_sha256(filename)
        hash_entry = collection.find_one({"hash": file_hash})
        if hash_entry:
            await prog.delete(True)
            await bot.get_chat(DUMP_CHAT)
            await bot.copy_message(
                chat_id=m.chat.id,
                from_chat_id=DUMP_CHAT,
                caption = cc1,
                message_id=hash_entry["dump_msg_id"]
            )
            os.remove(filename)
            print(f"✅ File '{name}' matched by hash. Forwarded from dump.")
            await prog.delete(True)
            return
        

        # 5. Send document to user
        await prog.delete(True)
        sent_msg = await bot.send_document(chat_id=m.chat.id, document= filename, caption=cc1)
        if sent_msg is None:
            await m.reply_text("❌ Upload failed.")
            os.remove(filename)
            return

        # 6. Forward to dump
        await bot.get_chat(DUMP_CHAT)
        dump_msg = await bot.copy_message(
            chat_id=DUMP_CHAT,
            caption = cc1,
            from_chat_id=m.chat.id,
            message_id=sent_msg.id
        )

        # 7. Store in DB
        collection_doc.insert_one({
            "name": name,
            "hash": file_hash,
            "dump_msg_id": dump_msg.id
        })

        os.remove(filename)
        print(f"🆕 Document '{name}' uploaded and stored.")
    
    except Exception as e:
        await m.reply_text(f"❌ Error: {e}")
        print(f"[ERROR - DOC] {e}")
async def abcdefg_pdf_decrypt2(url, key, name, cc1, bot, m):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    await m.reply_text(f"❌ Failed to download file: {response.status}")
                    return
                encrypted_data = await response.read()

        key_bytes = key.encode("utf-8")
        encrypted_data = base64.b64decode(encrypted_data)
        iv = encrypted_data[:16]
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
        decrypted_data = unpad(cipher.decrypt(encrypted_data[16:]), AES.block_size)

        file_path = f"{name}.pdf"

        async with aiofiles.open(file_path, "wb") as f:
            await f.write(decrypted_data)

        
        
        

    except Exception as e:
        print("Error")


async def new_encryptedpdf(bot, m, url, cc1, name, key):
    try:
        # 1. Check by filename
        existing = collection_doc.find_one({"name": name})
        if existing:
            await bot.get_chat(DUMP_CHAT)
            await bot.copy_message(
                chat_id=m.chat.id,
                from_chat_id=DUMP_CHAT,
                message_id=existing["dump_msg_id"]
            )
            print(f"✅ Document '{name}' matched by name. Forwarded from dump.")
            return

        # 2. Show download message
        show = f"<blockquote>Ｄｏｗｎｌｏａｄｉｎｇ Document... »\n\nName: {name}</blockquote>"
        prog = await m.reply_text(show)

        # 3. Download document
        filename = await abcdefg_pdf_decrypt2(url, key, name, cc1, bot, m)
        
        	
        	
        

        # 4. Compute hash
        file_hash = await compute_sha256(filename)
        hash_entry = collection_doc.find_one({"hash": file_hash})
        if hash_entry:
            await prog.delete()
            await bot.get_chat(DUMP_CHAT)
            await bot.copy_message(
                chat_id=m.chat.id,
                from_chat_id=DUMP_CHAT,
                message_id=hash_entry["dump_msg_id"]
            )
            os.remove(filename)
            print(f"✅ Document '{name}' matched by hash. Forwarded from dump.")
            return

        # 5. Send document to user
        await prog.delete()
        sent_msg = await bot.send_document(chat_id=m.chat.id, document=filename, caption=cc1)
        if sent_msg is None:
            await m.reply_text("❌ Upload failed.")
            os.remove(filename)
            return

        # 6. Forward to dump
        await bot.get_chat(DUMP_CHAT)
        dump_msg = await bot.copy_message(
            chat_id=DUMP_CHAT,
            from_chat_id=m.chat.id,
            message_id=sent_msg.id
        )

        # 7. Store in DB
        collection_doc.insert_one({
            "name": name,
            "hash": file_hash,
            "dump_msg_id": dump_msg.id
        })

        os.remove(filename)
        print(f"🆕 Document '{name}' uploaded and stored.")
    
    except Exception as e:
        await m.reply_text(f"❌ Error: {e}")
        print(f"[ERROR - DOC] {e}")
@bot.on_message(filters.command(["start"]) & filters.user(OWNER))
async def start(bot: Client, m: Message):
    await m.reply_text(f"<blockquote>Hello 👋\n\n I Am A Bot For Download Links From Your **.TXT** File And Then Upload That File On Telegram So Basically If You Want To Use Me First Send Me /txt Command And Then Follow Few Steps..\n\nUse /stop to stop any ongoing task.</blockquote>")


@bot.on_message(filters.command("stop"))
async def restart_handler(_, m):
    await m.reply_text("<blockquote>**Stopped**</blockquote>", True)
    os.execl(sys.executable, sys.executable, *sys.argv)



@bot.on_message(filters.command(["pa"]))
async def upload(bot: Client, m: Message):
    editable = await m.reply_text('<blockquote>Send text</blockquote>')
    input: Message = await bot.listen(editable.chat.id)
    x = await input.download()
    await input.delete(True)
    file_name, ext = os.path.splitext(os.path.basename(x))

    path = f"./downloads/{m.chat.id}"

    try:
       with open(x, "r") as f:
           content = f.read()
       content = content.split("\n")
       links = []
       
       for i in content:
           links.append(i.split("://", 1))
       os.remove(x)
            # print(len(links)
    except:
           await m.reply_text("**Invalid file input.**")
           os.remove(x)
           return
    
   
    await editable.edit(f"Total Index  - {len(links)}\nStart From \nResolution \nCaption")
    input0: Message = await bot.listen(editable.chat.id)
    appx = input0.text
    raw_text = appx.split("\n")[0]
    await input0.delete(True)

    
    raw_text0 = "d"
    
    if raw_text0 == 'd':
        b_name = file_name
    else:
        b_name = raw_text0
    

    
    raw_text2 = appx.split("\n")[1]
    
    try:
        if raw_text2 == "144":
            res = "256x144"
        elif raw_text2 == "240":
            res = "426x240"
        elif raw_text2 == "360":
            res = "640x360"
        elif raw_text2 == "480":
            res = "854x480"
        elif raw_text2 == "720":
            res = "1280x720"
        elif raw_text2 == "1080":
            res = "1920x1080" 
        else: 
            res = "UN"
    except Exception:
            res = "UN"
    
    

    
    raw_text3 = appx.split("\n")[2]
    
    highlighter  = "️<blockquote>DildaarYaara💚⁪⁬</blockquote>⁮⁮⁮"
    if raw_text3 == '0':
        MR = highlighter 
    else:
        MR = raw_text3
   
    
    
    
    

    thumb = "no"
    if thumb.startswith("http://") or thumb.startswith("https://"):
        getstatusoutput(f"wget '{thumb}' -O 'thumb.jpg'")
        thumb = "thumb.jpg"
    else:
        thumb == "no"

    
    
    
    
    await editable.delete()
        
        
        
            
                
                
                
                    
                
                    
                    
    
    
    batch_message = await bot.send_message(
    chat_id=editable.chat.id,
    text=f"**Batch Name:** <blockquote>{b_name}</blockquote>\n\n **Total links :** <blockquote>`{len(links)}`</blockquote> "
    )
    await bot.pin_chat_message(chat_id=editable.chat.id, message_id=batch_message.id, both_sides=True)
        
      
            
            
    
        
        
    
    
    if len(links) == 1:
        count = 1
    else:
        count = int(raw_text)

    try:
        for i in range(count - 1, len(links)):

            V = links[i][1].replace("file/d/","uc?export=download&id=").replace("www.youtube-nocookie.com/embed", "youtu.be").replace("?modestbranding=1", "").replace("/view?usp=sharing","") # .replace("mpd","m3u8")
            url = "https://" + V
            
            if "visionias" in url:
                async with ClientSession() as session:
                    async with session.get(url, headers={'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 'Accept-Language': 'en-US,en;q=0.9', 'Cache-Control': 'no-cache', 'Connection': 'keep-alive', 'Pragma': 'no-cache', 'Referer': 'http://www.visionias.in/', 'Sec-Fetch-Dest': 'iframe', 'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'cross-site', 'Upgrade-Insecure-Requests': '1', 'User-Agent': 'Mozilla/5.0 (Linux; Android 12; RMX2121) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Mobile Safari/537.36', 'sec-ch-ua': '"Chromium";v="107", "Not=A?Brand";v="24"', 'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"',}) as resp:
                        text = await resp.text()
                        url = re.search(r"(https://.*?playlist.m3u8.*?)\"", text).group(1)
            elif 'videos.classplusapp' in url or "tencdn.classplusapp" in url or "webvideos.classplusapp.com" in url or "media-cdn-alisg.classplusapp.com" in url or "videos.classplusapp" in url or "videos.classplusapp.com" in url or "media-cdn-a.classplusapp" in url or "media-cdn.classplusapp" in url:
                url = requests.get(f'https://api.classplusapp.com/cams/uploader/video/jw-signed-url?url={url}', headers={'x-access-token': 'eyJjb3Vyc2VJZCI6IjQ1NjY4NyIsInR1dG9ySWQiOm51bGwsIm9yZ0lkIjo0ODA2MTksImNhdGVnb3J5SWQiOm51bGx9'}).json()['url']
            elif "cwmediabkt99.crwilladmin.com" in url:
            	url = url.replace(' ', '%20')
            elif ".pdf*abcdefg" in url:
             a = url.replace('*abcdefg', '')
             url = a
            elif '/ivs' in url:
                url = f"https://master-api-v2.onrender.com/adda-mp4-m3u8?url={url}" + "&token=eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJiYXdhaGFycnkyN0BnbWFpbC5jb20iLCJhdWQiOiIxMTExOTI3MSIsImlhdCI6MTczNTgyNjQ3NywiaXNzIjoiYWRkYTI0Ny5jb20iLCJuYW1lIjoiSEFSU0ggQmF3YSAiLCJlbWFpbCI6ImJhd2FoYXJyeTI3QGdtYWlsLmNvbSIsInBob25lIjoiODgyNTA5MzM1MiIsInVzZXJJZCI6ImFkZGEudjEuZmZjYTYyOTk5MjJmZjI0NGZlMTBlOTUyNDYxZGRiMzciLCJsb2dpbkFwaVZlcnNpb24iOjJ9.SzM7P5_6cP-yFlekONl3lTf52KWaGUdzqS4bEHHbZZGTZeQt0feOdca59hweADv3c3Sj47DRnqaUTTYe3abpEg&quality=480"
            elif '/master.mpd' in url:
             token = "abc"
             id =  url.split("/")[-2]
             url =   "https://madxapi-d0cbf6ac738c.herokuapp.com/" + id + f"/master.m3u8?token={token}"
            name1 = links[i][0].replace("\t", "").replace(":", "").replace("/", "").replace("+", "").replace("#", "").replace("|", "").replace("@", "").replace("*", "").replace(".", "").replace("https", "").replace("http", "").strip()
            name = f'{str(count).zfill(3)}) {name1[:60]}'
            

            if "youtu" in url:
                ytf = f"b[height<={raw_text2}][ext=mp4]/bv[height<={raw_text2}][ext=mp4]+ba[ext=m4a]/b[ext=mp4]"
            else:
                ytf = f"b[height<={raw_text2}]/bv[height<={raw_text2}]+ba/b/bv+ba"

            if "jw-prod" in url and (url.endswith(".mp4") or "Expires=" in url):
                cmd = f'yt-dlp -o "{name}.mp4" "{url}"'
            else:
                cmd = f"yt-dlp --verbose -f '{ytf}' '{url}' -o '{name}.mp4' --no-check-certificate --retry 5 --retries 10 --concurrent-fragments 8"

            try:  
                
                cc = f'**Total Downloaded :** {str(count).zfill(3)} \n\n [📽️]Video Title :** {𝗻𝗮𝗺𝗲𝟭} .mkv\n\n<blockquote>🔷Batch Name: {b_name}</blockquote>\n\n **Downloaded By:** : <blockquote>**{MR}**</blockquote>'
                cc1 = f'**Total Downloaded :** {str(count).zfill(3)} \n\n [📁] Pdf_Title : {𝗻𝗮𝗺𝗲𝟭} .pdf \n\n**Batch Name** : <blockquote>**{b_name}**</blockquote>\n\n  **Downloaded By:** : <blockquote>**{MR}**</blockquote>'
                if "*" in url:
                     a, k = url.split("*", 1)
                     url = a
                     key = k
                     try:
                      	if ".pdf" in a:
                            
                      		await encrypted_pdf_store(bot, m, url, cc1, name, helper, key)
                      		count += 1
                      		await asyncio.sleep(2)
                         
                                
                                
                                
                      
                       
                      	else:
                      		await encrypted_video(bot, m, url, key, cmd, name, raw_text2, cc, thumb, helper)
                      		count += 1
                      		await asyncio.sleep(2)
                     except FloodWait as e:
                      print("Error")
                      
                      continue
                
                elif "drive" in url or ".ws" in url or "cwmediabkt99.crwilladmin.com" in url or ".json" in url:
                    await cw_pdf_store(bot, m, url, cc1, name, helper)
                    count += 1
                    await asyncio.sleep(2)
                
                elif "^" in url:
                    a, k = url.split("^", 1)
                    url = a
                    key = k
                    await new_encryptedpdf(url, key, name, cc1, bot, m)
                    count += 1
                    await asyncio.sleep(2)
                elif ".doc" in url:
                    hdr = {"Host": "store.adda247.com", "x-auth-token": "fpoa43edty5", "x-jwt-token": "eyJhbGciOiJIUzUxMiJ9.eyJzdWIiOiJiYXdhaGFycnkyN0BnbWFpbC5jb20iLCJhdWQiOiIxMTExOTI3MSIsImlhdCI6MTczNTgyNjQ3NywiaXNzIjoiYWRkYTI0Ny5jb20iLCJuYW1lIjoiSEFSU0ggQmF3YSAiLCJlbWFpbCI6ImJhd2FoYXJyeTI3QGdtYWlsLmNvbSIsInBob25lIjoiODgyNTA5MzM1MiIsInVzZXJJZCI6ImFkZGEudjEuZmZjYTYyOTk5MjJmZjI0NGZlMTBlOTUyNDYxZGRiMzciLCJsb2dpbkFwaVZlcnNpb24iOjJ9.SzM7P5_6cP-yFlekONl3lTf52KWaGUdzqS4bEHHbZZGTZeQt0feOdca59hweADv3c3Sj47DRnqaUTTYe3abpEg", "range": "bytes=0-", "referer": "https://store.adda247.com", "user-agent": "okhttp/4.9.3"}
                    try:
                        response = requests.get(url, headers=hdr)
                        filename = f'{name}.pdf'
                        with open(filename, 'wb') as output_file:
                            output_file.write(response.content)
                        copy = await bot.send_document(chat_id=m.chat.id,document=f'{name}.pdf', caption=cc1)
                        
                        count += 1
                        os.remove(f'{name}.pdf')
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        continue
                
                
                elif ".pdf" in url:
                    await cw_pdf_store(bot, m, url, cc1, name, helper)
                    count += 1
                    await asyncio.sleep(2)
                    continue
            
                else:
                    await download_and_send(bot, m, url, cmd, name, raw_text2, cc, thumb, helper)
                    count += 1
                    await asyncio.sleep(2)
                    continue
                    

            except Exception as e:
                await m.reply_text(
                    f"**downloading Failed**\n{str(e)}\n**Name** » {name}/n URL : {url}"
                )
                continue

    except Exception as e:
        await m.reply_text(e)
    await m.reply_text("<blockquote>**Batch Completed**✅</blockquote>")





bot.run()
        
