import os
import re
import requests
from netease import NeteaseApi
from functools import reduce
from datetime import datetime, timedelta
from time import sleep
import subprocess
import json


TOKEN = os.environ["DISCORD_TOKEN"]
assert TOKEN
FILE_D = os.path.dirname(__file__)
NETEASE_MUSIC_DOWNLOAD_DIR = os.path.join(FILE_D, "netease_download")


import discord
from io import BytesIO
import requests
import asyncio
from discord.ext.commands import Bot
from musicbot import get_metadata

NETEASE_MUSIC_SHARE_RE = re.compile(r".*https://.*music.163.com/.+?id=([^&]+).*")


bot = Bot(command_prefix="")


@bot.event
async def on_ready():
    print("We have logged in as {0.user}".format(bot))


def get_music_metadata(id):
    return json.loads(
        subprocess.check_output(
            [
                "node",
                os.path.join(FILE_D, "get.js"),
                str(id),
            ]
        ).decode("utf8")
    )


def process_lyric_line(line: str) -> (float, str):
    t, lrc = line.split("]", 1)
    t = t[1:]
    t.split(":")
    t = reduce(lambda prev, next: prev * 60 + next, [float(x) for x in t.split(":")], 0)
    return (t, lrc)


stopped = True


async def join_voice_channel(name: str, guild: discord.Guild):
    for voice_client in bot.voice_clients:
        if voice_client.channel.name == name:
            await voice_client.disconnect()
    for voice_channel in guild.voice_channels:
        if voice_channel.name == name:
            player = await voice_channel.connect()
    if player.is_playing():
        player.stop()
    return player


async def play_local(path: str, channel: discord.TextChannel, guild: discord.Guild):
    global stopped

    player = await join_voice_channel("music", guild)

    metadata = get_metadata(path)
    title = metadata.title
    artist = metadata.artist
    (album, cover) = metadata.album
    desc = ""
    if title:
        desc += "Title: " + title + "\n"
    if artist:
        desc += "Artist: " + artist + "\n"
    if album:
        desc += "Album: " + album + "\n"
    await channel.send(desc)
    if cover:
        content = BytesIO(bytearray(cover.data))
        f = discord.File(content, filename="cover." + cover.ext())
        await channel.send(file=f)
    stopped = False
    player.play(
        discord.FFmpegPCMAudio(
            path,
        ),
        after=lambda e: print("done", e),  # disconnect?
    )
    while player.is_playing() and not stopped:
        await asyncio.sleep(1)
    # disconnect after the player has finished
    player.stop()


async def play_netease(id: str, channel: discord.TextChannel, guild: discord.Guild):
    global stopped
    music_fn = os.path.join(NETEASE_MUSIC_DOWNLOAD_DIR, id + ".mp3")
    info_fn = os.path.join(NETEASE_MUSIC_DOWNLOAD_DIR, id + ".json")
    if not os.path.exists(info_fn):
        m = await channel.send("Fetching music metadata...")
        info = get_music_metadata(id)
        if not info["url"]:
            r = requests.get(f"https://api.moeblog.vip/163/?type=url&id={id}&br=999000")
            if r.status_code != 200 or r.text == "":
                errmsg = "Real URL cannot be found"
                channel.send(errmsg)
                raise Exception(errmsg)
            info["url"] = r.json()["url"]
        print(info)
        with open(info_fn, "w") as f:
            json.dump(info, f, ensure_ascii=False)
        await m.delete()
    else:
        with open(info_fn) as f:
            info = json.load(f)
    description = f"""\
Title: {info["title"]}
Artists: {', '.join([ar['name'] for ar in info['artists']])}
Album: {info["album"]}
"""
    await channel.send(description)
    if not os.path.exists(music_fn):
        # m = await channel.send("Fetching music file URL...")
        # url = NeteaseApi.url(id)
        # await m.delete()
        m = await channel.send("Downloading music file...")
        url = info["url"]

        r = requests.get(url)
        if not r.status_code == 200:
            errmsg = f"Failed to download {url}"
            channel.send(errmsg)
            raise Exception(errmsg)
        with open(music_fn, "wb") as f:
            f.write(r.content)
        await m.delete()

    if lyrics := info["lyrics"]:
        lyrics = (
            [process_lyric_line(line) for line in lyrics.splitlines()] if lyrics else []
        )
    # start voice
    player = await join_voice_channel("music", guild)

    if u := info["cover_url"]:
        id = info["album_id"]
        cover_fn = os.path.join(NETEASE_MUSIC_DOWNLOAD_DIR, str(id) + ".jpg")
        if not os.path.exists(cover_fn):
            r = requests.get(u)
            if r.status_code == 200:
                with open(cover_fn, "wb") as f:
                    f.write(r.content)
        f = discord.File(cover_fn)
        await channel.send(file=f)

    player.play(
        discord.FFmpegPCMAudio(
            music_fn,
        ),
        after=lambda e: print("done", e),  # disconnect?
    )
    stopped = False
    start_time = datetime.now()
    # start lyrics
    if lyrics:
        for i in range(len(lyrics)):
            print(f"player stopped: {stopped} (play_netease)")
            if stopped:
                break
            lyric = lyrics[i][1]
            t1 = lyrics[i][0]
            if i == len(lyrics) - 1:
                delta = 10
            else:
                t2 = lyrics[i + 1][0]
                delta = t2 - t1
            while datetime.now() - start_time < timedelta(seconds=t1 - 0.1):
                sleep(0.1)
                pass
            else:
                if lyric:
                    m = await channel.send(lyric, delete_after=delta)

    while player.is_playing() and not stopped:
        await asyncio.sleep(1)
    # disconnect after the player has finished
    player.stop()


@bot.event
async def on_message(msg: discord.Message):
    global stopped
    if msg.author == bot.user:
        return
    guild = msg.guild
    channel = msg.channel
    msg = msg.content

    if match := NETEASE_MUSIC_SHARE_RE.match(msg):
        id = match[1]
        print(f"Netease Music share link detected: {msg}\nid: {id}")
        await play_netease(id, channel, guild)
    if match := re.match("sieg heil", msg, re.IGNORECASE):
        await play_local(
            "/home/tianyi/Music/Adolf Hitler's Closing Speech.m4a", channel, guild
        )
    elif msg == "/stop":
        stopped = True
        await msg.delete()


if __name__ == "__main__":
    bot.run(TOKEN)
