# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import time
import datetime
import aiohttp
import aiofiles
import aiohttp
import aiofiles
import subprocess
import yt_dlp
import asyncio
import logging
import requests
import tgcrypto
import subprocess
import concurrent.futures
import mmap
from pathlib import Path
from utils import progress_bar

from pyrogram import Client, filters
from pyrogram.types import Message

def duration(filename):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    return float(result.stdout)
async def download_file(url, name):
    if ".pdf" in url:
     file_path = f"{name}.pdf"
    else:
     file_path = name
    command = [
        'aria2c', '--continue', '--max-connection-per-server=4', '--split=4', '--min-split-size=1M',
        '--out=' + file_path, url
    ]
    subprocess.run(command, check=True)
    return file_path

# Function to decrypt a file
def decrypt_file(file_path, key):
    if not os.path.exists(file_path):
        print(f"File does not exist: {file_path}")
        return False
    
    file_size = os.path.getsize(file_path)
    num_bytes = min(28, file_size)

    if file_size < 28:
        print(f"File too small for decryption: {file_path}")
        return False

    with open(file_path, "r+b") as f:
        with mmap.mmap(f.fileno(), length=num_bytes, access=mmap.ACCESS_WRITE) as mmapped_file:
            for i in range(num_bytes):
                mmapped_file[i] ^= ord(key[i]) if i < len(key) else i
        return True




async def get_mps_and_keys(api_url):
    response = requests.get(api_url)
    response_json = response.json()
    mpd = response_json.get('url')
    keys = response_json.get('keys')
    return mpd, keys

async def decrypt_and_merge_video(mpd_url, keys_string, output_path, output_name, quality="720"):
    try:
        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)

        cmd1 = f'yt-dlp -f "bv[height<={quality}]+ba/b" -o "{output_path}/file.%(ext)s" --allow-unplayable-format --no-check-certificate --external-downloader aria2c "{mpd_url}"'
        print(f"Running command: {cmd1}")
        os.system(cmd1)
        
        avDir = list(output_path.iterdir())
        print(f"Downloaded files: {avDir}")
        print("Decrypting")

        video_decrypted = False
        audio_decrypted = False

        for data in avDir:
            if data.suffix == ".mp4" and not video_decrypted:
                cmd2 = f'mp4decrypt {keys_string} --show-progress "{data}" "{output_path}/video.mp4"'
                print(f"Running command: {cmd2}")
                os.system(cmd2)
                if (output_path / "video.mp4").exists():
                    video_decrypted = True
                data.unlink()
            elif data.suffix == ".m4a" and not audio_decrypted:
                cmd3 = f'mp4decrypt {keys_string} --show-progress "{data}" "{output_path}/audio.m4a"'
                print(f"Running command: {cmd3}")
                os.system(cmd3)
                if (output_path / "audio.m4a").exists():
                    audio_decrypted = True
                data.unlink()

        if not video_decrypted or not audio_decrypted:
            raise FileNotFoundError("Decryption failed: video or audio file not found.")

        cmd4 = f'ffmpeg -i "{output_path}/video.mp4" -i "{output_path}/audio.m4a" -c copy "{output_path}/{output_name}.mp4"'
        print(f"Running command: {cmd4}")
        os.system(cmd4)
        if (output_path / "video.mp4").exists():
            (output_path / "video.mp4").unlink()
        if (output_path / "audio.m4a").exists():
            (output_path / "audio.m4a").unlink()
        
        filename = output_path / f"{output_name}.mp4"

        if not filename.exists():
            raise FileNotFoundError("Merged video file not found.")

        cmd5 = f'ffmpeg -i "{filename}" 2>&1 | grep "Duration"'
        duration_info = os.popen(cmd5).read()
        print(f"Duration info: {duration_info}")

        return str(filename)

    except Exception as e:
        print(f"Error during decryption and merging: {str(e)}")
        raise 
def duration(filename):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                             "format=duration", "-of",
                             "default=noprint_wrappers=1:nokey=1", filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    return float(result.stdout)
    
def exec(cmd):
        process = subprocess.run(cmd, stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        output = process.stdout.decode()
        print(output)
        return output
        #err = process.stdout.decode()
def pull_run(work, cmds):
    with concurrent.futures.ThreadPoolExecutor(max_workers=work) as executor:
        print("Waiting for tasks to complete")
        fut = executor.map(exec,cmds)
async def aio(url,name):
    k = f'{name}.pdf'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                f = await aiofiles.open(k, mode='wb')
                await f.write(await resp.read())
                await f.close()
    return k


async def zoom_download(url, name):
    ka = f'{name}'.mp4
    try:
        subprocess.run(['aria2c', url, '-o', ka], check=True)
        print(f"Downloaded using aria2c: {ka}")
        return ka
    except Exception:
        pass
    print(f"All download methods failed for {url}")
    return None
async def download(url, name):
    if ".pdf" in url:
    	ka = f'{name}.pdf'
    elif ".ws" in url:
    	ka = f'{name}.html'
    elif ".json" in url:
        ka = f'{name}.json'
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                if resp.status == 200:
                    async with aiofiles.open(ka, mode='wb') as f:
                        await f.write(await resp.read())
                    print(f"Downloaded using aiohttp: {ka}")
                    return ka
    except Exception:
        pass
    try:
        ydl_opts = {
            'outtmpl': ka,
            'format': 'best',
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"Downloaded using yt-dlp: {ka}")
        return ka
    except Exception:
        pass
    try:
        subprocess.run(['aria2c', url, '-o', ka], check=True)
        print(f"Downloaded using aria2c: {ka}")
        return ka
    except Exception:
        pass
    print(f"All download methods failed for {url}")
    return None

def parse_vid_info(info):
    info = info.strip()
    info = info.split("\n")
    new_info = []
    temp = []
    for i in info:
        i = str(i)
        if "[" not in i and '---' not in i:
            while "  " in i:
                i = i.replace("  ", " ")
            i.strip()
            i = i.split("|")[0].split(" ",2)
            try:
                if "RESOLUTION" not in i[2] and i[2] not in temp and "audio" not in i[2]:
                    temp.append(i[2])
                    new_info.append((i[0], i[2]))
            except:
                pass
    return new_info


def vid_info(info):
    info = info.strip()
    info = info.split("\n")
    new_info = dict()
    temp = []
    for i in info:
        i = str(i)
        if "[" not in i and '---' not in i:
            while "  " in i:
                i = i.replace("  ", " ")
            i.strip()
            i = i.split("|")[0].split(" ",3)
            try:
                if "RESOLUTION" not in i[2] and i[2] not in temp and "audio" not in i[2]:
                    temp.append(i[2])
                    
                    # temp.update(f'{i[2]}')
                    # new_info.append((i[2], i[0]))
                    #  mp4,mkv etc ==== f"({i[1]})" 
                    
                    new_info.update({f'{i[2]}':f'{i[0]}'})

            except:
                pass
    return new_info



async def run(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    stdout, stderr = await proc.communicate()

    print(f'[{cmd!r} exited with {proc.returncode}]')
    if proc.returncode == 1:
        return False
    if stdout:
        return f'[stdout]\n{stdout.decode()}'
    if stderr:
        return f'[stderr]\n{stderr.decode()}'

    

def old_download(url, file_name, chunk_size = 1024 * 10):
    if os.path.exists(file_name):
        os.remove(file_name)
    r = requests.get(url, allow_redirects=True, stream=True)
    with open(file_name, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=chunk_size):
            if chunk:
                fd.write(chunk)
    return file_name


def human_readable_size(size, decimal_places=2):
    for unit in ['B', 'KB', 'MB', 'GB', 'TB', 'PB']:
        if size < 1024.0 or unit == 'PB':
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f} {unit}"


def time_name():
    date = datetime.date.today()
    now = datetime.datetime.now()
    current_time = now.strftime("%H%M%S")
    return f"{date} {current_time}.mp4"


async def download_video(url,cmd, name):
    time.sleep(2)
    download_cmd = f'{cmd} -R 25 --fragment-retries 25 --external-downloader aria2c --downloader-args "aria2c: -x 16 -j 32" --cookies cookies.txt'
    global failed_counter
    print(download_cmd)
    logging.info(download_cmd)
    k = subprocess.run(download_cmd, shell=True)
    if "visionias" in cmd and k.returncode != 0 and failed_counter <= 10:
        failed_counter += 1
        await asyncio.sleep(5)
        await download_video(url, cmd, name)
    failed_counter = 0
    try:
        if os.path.isfile(name):
            return name
        elif os.path.isfile(f"{name}.webm"):
            return f"{name}.webm"
        name = name.split(".")[0]
        if os.path.isfile(f"{name}.mkv"):
            return f"{name}.mkv"
        elif os.path.isfile(f"{name}.mp4"):
            return f"{name}.mp4"
        elif os.path.isfile(f"{name}.mp4.webm"):
            return f"{name}.mp4.webm"

        return name
    except FileNotFoundError as exc:
        return os.path.isfile.splitext[0] + "." + "mp4"

async def send_videoo(bot: Client, m: Message,cc,ka,cc1,prog,count,name):
    reply = await m.reply_text(f"Uploading » `{name}`")
    
    start_time = time.time()
    await m.reply_video(ka,caption=cc1)
    count+=1
    await reply.delete (True)
    
    os.remove(ka)
    time.sleep(3) 
async def send_doc(bot: Client, m: Message,cc,ka,cc1,prog,count,name):
    reply = await m.reply_text(f"Uploading » `{name}`")
    
    start_time = time.time()
    await m.reply_document(ka,caption=cc1)
    count+=1
    await reply.delete (True)
    
    os.remove(ka)
    time.sleep(3) 


MAX_FILE_SIZE_MB = 2000
upload_lock = asyncio.Lock()

async def get_file_size_mb(file_path):
    return os.path.getsize(file_path) / (1024 * 1024)

async def split_video(input_file, part1, part2):
    duration_cmd = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{input_file}"'
    total_duration = float(subprocess.check_output(duration_cmd, shell=True).decode().strip())
    half_duration = total_duration / 2

    subprocess.run(f'ffmpeg -i "{input_file}" -t {half_duration} -c copy "{part1}"', shell=True)
    subprocess.run(f'ffmpeg -i "{input_file}" -ss {half_duration} -c copy "{part2}"', shell=True)

async def upload_video(bot, m, filename, caption, thumb, reply):
    dur = int(duration(filename))
    start_time = asyncio.get_event_loop().time()

    try:
        async with upload_lock:
            msg = await m.reply_video(
                filename,
                caption=caption,
                supports_streaming=True,
                height=720,
                width=1280,
                thumb=thumb,
                duration=dur,
                progress_args=(reply, start_time)
            )
            return msg
    except Exception:
        async with upload_lock:
            msg = await m.reply_document(
                filename,
                caption=caption,
                progress=progress_bar,
                progress_args=(reply, start_time)
            )
            return msg

async def send_vid(bot: Client, m: Message, cc, filename, thumb, name, prog):
    await asyncio.sleep(2)

    subprocess.run(f'ffmpeg -i "{filename}" -ss 00:00:12 -vframes 1 "{filename}.jpg"', shell=True)
    await prog.delete()

    reply = await m.reply_text(f"**Uploading ...** - `{name}`")
    thumbnail = f"{filename}.jpg" if thumb == "no" else thumb
    file_size = await get_file_size_mb(filename)

    try:
        if file_size <= MAX_FILE_SIZE_MB:
            await upload_video(bot, m, filename, cc, thumbnail, reply)
            return msg
        else:
            part1 = filename.replace(".mp4", "_part1.mp4")
            part2 = filename.replace(".mp4", "_part2.mp4")
            await split_video(filename, part1, part2)

            for i, part in enumerate([part1, part2], 1):
                caption = f"{cc}\n\nPart {i}/2"
                await upload_video(bot, m, part, caption, thumbnail, reply)
                os.remove(part)

    except Exception as e:
        async with upload_lock:
            await m.reply_text(f"❌ Upload failed:\n`{str(e)}`")

    # Clean up
    for f in [filename, f"{filename}.jpg"]:
        if os.path.exists(f):
            os.remove(f)
    return msg
    await reply.delete()
                       
