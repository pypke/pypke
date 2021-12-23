from utils.time import TimeConverter

import aiohttp
import random
from typing import Optional
from urllib.parse import quote_plus
from datetime import datetime

import discord
from discord.ext import commands
from dislash import message_command, ActionRow, Button, ButtonStyle

WEATHER_KEY = "073a1838197e477bb83141102213110"


class Misc(commands.Cog, description="Commands that do not belong to any module."):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # if not message.guild:
        #     return

        chatbot_channels = await self.client.chatbot.get_all()
        data = await self.client.config.find(message.guild.id)
        if not data or "prefix" not in data:
            prefix = "#"
        else:
            prefix = data["prefix"]

        if message.content.lower().startswith(f"{prefix}"):
            return
        msg = quote_plus(message.content.lower())
        for channel in chatbot_channels:
            if int(channel['channel']) == message.channel.id:
                try:
                    async with aiohttp.ClientSession() as session:
                        async with session.get(f'http://api.brainshop.ai/get?bid=160282&key=ymIz1TEF0CNxURTu&uid={message.author.id}&msg={msg}') as r:
                            if 300 > r.status >= 200:
                                data = await r.json()
                                response = data['cnt']
                                await message.reply(response, mention_author=False)
                except discord.HTTPException:
                    pass

    @commands.group(name="chatbot", description="Configure chatbot in this server.", invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def chatbot_command(self, ctx, channel: discord.TextChannel):
        data = {
            '_id': ctx.guild.id,
            'channel': channel.id
        }
        await self.client.chatbot.upsert(data)
        await ctx.send(f"ChatBot will now function in {channel.mention}, To stop it use `{ctx.prefix}chatbot stop`")

    @chatbot_command.command(name="stop", description="Stop chatbot in this server.")
    @commands.has_permissions(manage_guild=True)
    async def chatbot_stop(self, ctx):
        data = await self.client.chatbot.find(ctx.guild.id)
        if not data:
            await ctx.send("ChatBot isn't setup for this server!!")

        await self.client.chatbot.delete(ctx.guild.id)
        await ctx.send(f"ChatBot has now stopped!!")

    @commands.command(name="weather", description="Gives info about the real time weather.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def weather_command(self, ctx, *, location: str):
        if location == "auto:ip" and ctx.author.id != 624572769484668938:
            return await ctx.send("Location not found!")

        query = location.replace(" ", "+")
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.weatherapi.com/v1/current.json?key={WEATHER_KEY}&q={query}") as r:
                if 300 > r.status >= 200:
                    data = await r.json()

                    embed = discord.Embed(
                        color=self.client.color
                    )
                    temp_c = round(data["current"]["temp_c"])
                    temp_f = round(data["current"]["temp_f"])
                    condition = data["current"]["condition"]["text"]
                    humidity = data["current"]["humidity"]
                    cloud = data["current"]["cloud"]
                    wind_speed = data["current"]["wind_mph"]
                    wind_dir = data["current"]["wind_dir"]
                    epoch = data["current"]["last_updated_epoch"]
                    tz_id = data["location"]["tz_id"]
                    localtime = data["location"]["localtime"]

                    embed.set_author(
                        name=f'{data["location"]["name"]}, {data["location"]["country"]}')
                    embed.add_field(
                        name="__Weather__",
                        value=f"**Temperature:** `{temp_c} °C` | `{temp_f} °F`\n**Condtion:** {condition}\n**Humidity:** {humidity}%\n**Cloud Cover:** {cloud}%\n**Wind Speed:** {wind_speed} mph\n**Wind Direction:** {wind_dir}\n**Last Updated:** <t:{epoch}:f>",
                        inline=False
                    )
                    embed.add_field(
                        name="__Infomation__",
                        value=f"**Timezone:** {tz_id}\n**Local Time:** {localtime}",
                        inline=False
                    )
                    embed.set_thumbnail(
                        url=f'https:{data["current"]["condition"]["icon"]}')
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("Location not found!")

    @commands.command(name="define", description="Get the definition of a word.")
    async def define_command(self, ctx, *, word):
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{quote_plus(word)}") as r:
                if not 300 > r.status >= 200:
                    return await ctx.send(f"Can't find the definition of \"{word}\". If it is a word like 'snow ball' try writing it without space.")

                data = await r.json()
                data = data[0]

                word = data["word"]
                phonetic = data["phonetic"]
                try: origin = data["origin"]
                except KeyError: origin = ""
                embed = discord.Embed(
                    title=f"{word.capitalize()} [{phonetic}]",
                    description=f"{origin.capitalize()}",
                    color=self.client.colors["og_blurple"]
                )
                for meaning in data["meanings"]:
                    value = f"**Definition:** {meaning['definitions'][0]['definition']}\n"
                    try:
                        if meaning['definitions'][0]['example']:
                            value += f"**Example:** {meaning['definitions'][0]['example']}\n"
                    except KeyError:
                        pass
                    if meaning['definitions'][0]['synonyms']:
                        value += f"**Synonyms:** {', '.join(meaning['definitions'][0]['synonyms'][:5])}\n"
                    if meaning['definitions'][0]['antonyms']:
                        value += f"**Antonyms:** {', '.join(meaning['definitions'][0]['antonyms'][:5])}\n"

                    embed.add_field(
                        name=meaning["partOfSpeech"].capitalize(),
                        value=value
                    )
                    value = ""

                await ctx.send(embed=embed)

    @commands.command(name="google", description="Search something on google")
    async def google_command(self, ctx, query: str):
        link = quote_plus(query)
        url = f"https://www.google.com/search?q={link}"

        google_btn = ActionRow(
            Button(
                style=ButtonStyle.link,
                label="Search",
                url=url
            )
        )
        google = discord.Embed(
            title="Google Search Results",
            description=f"**Query:** {query}\n**Results:** Click The Button Below To Open", color=self.client.color,
            timestamp=datetime.now()
        )
        google.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=google, components=[google_btn])

    @commands.command(name="unix", description="Get unix timestamp to copy as of current time or future.", aliases=["epoch"])
    async def unix_command(self, ctx, *, value: Optional[TimeConverter]):
        if value == None:
            epoch_time = round(datetime.timestamp())
        else:
            epoch_time = datetime.timestamp()
            epoch_time = round(epoch_time + value)

        embed = discord.Embed(
            title="Timestamp",
            description="\uFEFF",
            color=self.client.colors["orange"],
            timestamp=datetime.now()
        )
        embed.add_field(
            name="Timestamp Example",
            value=f"<t:{epoch_time}:f>\n",
            inline=False
        )
        embed.add_field(
            name="Timestamp Copy",
            value=f"`<t:{epoch_time}:f>`\n",
            inline=False
        )
        await ctx.send(embed=embed)

    @message_command(name="Translate", guild_ids=["850732056790827020"])
    async def translate_message_command(self, inter):
        await inter.respond("Hmmm test success!")


def setup(client):
    client.add_cog(Misc(client))
