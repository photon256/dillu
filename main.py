
# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import re
import sys
import json
import time
import asyncio
import requests
import subprocess
import core as helper
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
                
                cc = f'**Total Downloaded :** {str(count).zfill(3)} \n\n [📽️]Video Title :** {𝗻𝗮𝗺𝗲𝟭} {MR}.mkv\n\n<blockquote>🔷Batch Name: {b_name}</blockquote>\n\n **Downloaded By:** : <blockquote>**{MR}**</blockquote>'
                cc1 = f'**Total Downloaded :** {str(count).zfill(3)} \n\n [📁] Pdf_Title : {𝗻𝗮𝗺𝗲𝟭} {MR}.pdf \n\n**Batch Name** : <blockquote>**{b_name}**</blockquote>\n\n  **Downloaded By:** : <blockquote>**{MR}**</blockquote>'
                if "*" in url:
                     a, k = url.split("*", 1)
                     url = a
                     key = k
                     try:
                      	if ".pdf" in a:
                      		Show = f"**Ｄｏｗｎｌｏａｄｉｎｇ...**\n\n📝Name » {name}\n❄Quality » {raw_text2}"
                      		prog = await m.reply_text(Show)
                      		file_path = await helper.download_file(url, name)
                      		copy = helper.decrypt_file(file_path, key)
                      		filename = file_path
                      		await prog.delete(True)
                      		await bot.send_document(chat_id=m.chat.id, document=filename, caption=cc1)
                            
                      		count += 1
                      		time.sleep(2)
                         
                                
                                
                                
                      
                      
                      
                            
                      	else:
                      		Show = f"**Ｄｏｗｎｌｏａｄｉｎｇ... »**\n\n**Name:{name}**\nQuality » {raw_text2}"
                      		prog = await m.reply_text(Show)
                            
                      		file_path = await helper.download_file(url, name)
                      		copy = helper.decrypt_file(file_path, key)
                      		filename = file_path
                      		await prog.delete(True)
                      		
                      		await helper.send_vid(bot, m, cc, filename, thumb, name, prog)
                            
                      		count += 1
                      		time.sleep(2)
                     except FloodWait as e:
                      await m.reply_text(str(e))
                      
                      continue
                
                elif "drive" in url or ".ws" in url or "cwmediabkt99.crwilladmin.com" in url or ".json" in url:
                    try:
                        ka = await helper.download(url, name)
                        copy = await bot.send_document(chat_id=m.chat.id,document=ka, caption=cc1)
                        count+=1
                        os.remove(ka)
                        time.sleep(2)
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        continue
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
                    try:
                        cmd = f'yt-dlp -o "{name}.pdf" "{url}"'
                        download_cmd = f"{cmd} -R 25 --fragment-retries 25"
                        os.system(download_cmd)
                        copy = await bot.send_document(chat_id=m.chat.id, document=f'{name}.pdf', caption=cc1)
                        count += 1
                        os.remove(f'{name}.pdf')
                        time.sleep(2)
                    except FloodWait as e:
                        await m.reply_text(str(e))
                        time.sleep(e.x)
                        continue
                else:
                    Show = f"<blockquote>**Ｄｏｗｎｌｏａｄｉｎｇ... »**\n\n**Name:{name}**\nQuality » {raw_text2}</blockquote>"
                    prog = await m.reply_text(Show)
                    
                    res_file = await helper.download_video(url, cmd, name)
                    time.sleep(2)
                    filename = res_file
                    await prog.delete(True)
                    
                    await helper.send_vid(bot, m, cc, filename, thumb, name, prog)
                    
                    count += 1
                    time.sleep(3)
                    

            except Exception as e:
                await m.reply_text(
                    f"**downloading Failed**\n{str(e)}\n**Name** » {name}/n URL : {url}"
                )
                continue

    except Exception as e:
        await m.reply_text(e)
    await m.reply_text("<blockquote>**Batch Completed**✅</blockquote>")





bot.run()
