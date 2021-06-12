import discord
import os
import time
from io import BytesIO
import requests
import asyncio
from discord.ext.commands import Bot
from mimetypes import guess_type
from musicbot import get_metadata, Metadata


client = discord.Client()


@client.event
async def on_ready():
    print("We have logged in as {0.user}".format(client))


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content == "来点涩图":
        setu = requests.get("https://api.lolicon.app/setu/").json()["data"][0]
        print(setu)
        title = setu["title"]
        author = setu["author"]
        author_url = f"https://www.pixiv.net/users/{setu['uid']}"
        url = f'https://www.pixiv.net/artworks/{setu["pid"]}'
        tags = " ".join([f"#{tag}" for tag in setu["tags"]])

        info = (
            discord.Embed(title=setu["title"])
            .add_field(
                name="author",
                value=f"[{author}]({author_url})",
            )
            .add_field(name="source", value=url)
            .add_field(name="tags", value=tags)
        )
        setu_url = setu["url"]
        setu = requests.get(setu_url).content
        setu_f = BytesIO(setu)
        f = discord.File(setu_f, filename="setu.jpg")
        await message.channel.send(embed=info, file=f)


bot = Bot(command_prefix="")


@bot.command(name="test")
async def _test(ctx, arg):
    print("good")


@bot.event
async def on_ready():
    print("We have logged in as {0.user}".format(bot))


@bot.command(
    name="music",
    description="Plays an audio in the voice channel",
    pass_ctx=True,
)
async def music(ctx):
    print("playing music...")

    # guild = ctx.guild
    # voice_channel = guild.voice_channels[0]

    # grab the user who sent the command
    user = ctx.message.author
    print(user)
    # if not user.voice:
    #     user.voice.channel
    voice_channel = user.voice.channel
    # only play music if user is in a voice channel

    music_filename = "./01-ふわふわ時間.m4a"

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


class PixivApi(object):
    USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:88.0) Gecko/20100101 Firefox/88.0"

    def __init__(self, phpsessid: str):
        self.session = requests.Session()
        self.session.cookies.update({"PHPSESSID": phpsessid})

    def get(self, url):
        return self.session.get(url)


# curl 'https://www.pixiv.net/ranking.php?mode=daily_r18&p=1&format=json' \
#     -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:88.0) Gecko/20100101 Firefox/88.0' \
#     -H 'Cookie: PHPSESSID=xxx'

if __name__ == "__main__":
    bot.run(TOKEN)
    client.run(TOKEN)
