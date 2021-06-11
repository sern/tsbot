import os
import re
import requests
from netease import NeteaseApi
from functools import reduce
from datetime import datetime, timedelta
from time import sleep


TOKEN = os.environ["DISCORD_TOKEN"]
assert TOKEN
NETEASE_MUSIC_DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "netease_download")


import discord
from io import BytesIO
import requests
import asyncio
from discord.ext.commands import Bot
from musicbot import get_metadata

NETEASE_MUSIC_SHARE_RE = re.compile(r".*https://y.music.163.com/.+?id=([^&]+).*")


bot = Bot(command_prefix="")


@bot.command(name="test")
async def _test(ctx, arg):
    print("good")


@bot.event
async def on_ready():
    print("We have logged in as {0.user}".format(bot))


def process_lyric_line(line: str) -> (float, str):
    t, lrc = line.split("]", 1)
    t = t[1:]
    t.split(":")
    t = reduce(lambda prev, next: prev * 60 + next, [float(x) for x in t.split(":")], 0)
    return (t, lrc)


@bot.event
async def on_message(msg: discord.Message):
    if msg.author == bot.user:
        return
    guild = msg.guild
    channel = msg.channel
    msg = msg.content

    if match := NETEASE_MUSIC_SHARE_RE.match(msg):
        id = match[1]
        print(f"Netease Music share link detected: {msg}\nid: {id}")
        music_fn = os.path.join(NETEASE_MUSIC_DOWNLOAD_DIR, id + ".mp3")
        lyrics_fn = os.path.join(NETEASE_MUSIC_DOWNLOAD_DIR, id + ".lrc")
        if not os.path.exists(music_fn):
            m = await channel.send("Fetching music file URL...")
            url = NeteaseApi.url(id)
            await m.delete()

            m = await channel.send("Downloading music file...")
            r = requests.get(url)
            if not r.status_code == 200:
                raise Exception(f"Fail to download {url}")
            # TODO: get album cover
            # TODO: display lyrics
            with open(music_fn, "wb") as f:
                f.write(r.content)
            await m.delete()

        if os.path.exists(lyrics_fn):
            with open(lyrics_fn) as f:
                lyrics = f.read()
        else:
            lyrics = NeteaseApi.lyric(id)
            with open(lyrics_fn, "w") as f:
                f.write(lyrics)
        lyrics = [process_lyric_line(line) for line in lyrics.splitlines()]
        # start voice
        for voice_client in bot.voice_clients:
            if voice_client.channel.name == "music":
                await voice_client.disconnect()
        for voice_channel in guild.voice_channels:
            print(voice_channel.name)
            if voice_channel.name == "music":
                player = await voice_channel.connect()
        if player.is_playing():
            player.stop()
        # await msg.channel.send(desc)
        # if cover:
        #     content = BytesIO(bytearray(cover.data))
        #     f = discord.File(content, filename="cover." + cover.ext())
        #     await ctx.channel.send(file=f)
        player.play(
            discord.FFmpegPCMAudio(
                music_fn,
            ),
            after=lambda e: print("done", e),  # disconnect?
        )
        start_time = datetime.now()
        # start lyrics
        for i in range(len(lyrics)):
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
                    print(m)

        while player.is_playing():
            await asyncio.sleep(1)
        # disconnect after the player has finished
        player.stop()


@bot.command(
    name="music",
    description="Plays an audio in the voice channel",
    pass_ctx=True,
)
async def music(ctx):

    # guild = ctx.guild
    # voice_channel = guild.voice_channels[0]

    # grab the user who sent the command
    user = ctx.message.author
    print(user)
    # if not user.voice:
    #     user.voice.channel
    voice_channel = user.voice.channel
    # only play music if user is in a voice channel

    music_filename = "/Users/sern/Documents/GitHub/tsbot/musicbot/01-ふわふわ時間.m4a"

    metadata = get_metadata(music_filename)
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

    if voice_channel:
        # grab user's voice channel
        print("User is in channel: " + voice_channel.name)
        # create StreamPlayer
        player = None
        for voice_client in bot.voice_clients:
            if voice_client.channel.id == voice_channel.id:
                player = voice_client
        if not player:
            player = await voice_channel.connect()
        if player.is_playing():
            player.stop()
        await ctx.channel.send(desc)
        if cover:
            content = BytesIO(bytearray(cover.data))
            f = discord.File(content, filename="cover." + cover.ext())
            await ctx.channel.send(file=f)
        player.play(
            discord.FFmpegPCMAudio(
                music_filename,
            ),
            after=lambda e: print("done", e),  # disconnect?
        )
        while not player.is_done():
            await asyncio.sleep(1)
        # disconnect after the player has finished
        player.stop()
        # await vc.disconnect()
    else:
        await ctx.channel.send("Please join a voice channel and retry.")
        print("User is not in a channel.")
        # await bot.say("User is not in a channel.")


if __name__ == "__main__":
    bot.run(TOKEN)
