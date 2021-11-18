from utils.time import TimeConverter

import aiohttp, random
from urllib.parse import quote_plus
from datetime import datetime

import discord
from discord.ext import commands
from dislash import message_command, ActionRow, Button, ButtonStyle

WEATHER_KEY = "073a1838197e477bb83141102213110"

class Misc(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="weather", description="Gives info about the real time weather.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def weather_command(self, ctx, location: str):
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

                    embed.set_author(name=f'{data["location"]["name"]}, {data["location"]["country"]}')
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
                    embed.set_thumbnail(url=f'https:{data["current"]["condition"]["icon"]}')
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("Location not found!")

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
        google = discord.Embed(title="Google Search Results", description=f"**Query:** {query}\n**Results:** Click The Button Below To Open", color = random.choice(self.client.color_list), timestamp=datetime.now())
        google.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
        await ctx.send(embed=google, components=[google_btn])

    @commands.command(name="unix", description="Get unix timestamp to copy as of current time or future.", aliases=["epoch"])
    async def unix_command(self, ctx, *, value: TimeConverter=None):
        if value == None:
            epoch_time = round(datetime.timestamp())
        else:
            epoch_time = datetime.timestamp()
            epoch_time = round(epoch_time + value)

        embed = discord.Embed(title="Timestamp", description="\uFEFF", color=self.client.randcolor, timestamp=datetime.now())
        embed.add_field(name="Timestamp Example", value=f"<t:{epoch_time}:f>\n", inline=False)
        embed.add_field(name="Timestamp Copy", value=f"`<t:{epoch_time}:f>`\n", inline=False)
        await ctx.send(embed=embed)
        
    @message_command(name="Translate", guild_ids=["850732056790827020"])
    async def translate_message_command(self, inter):
        await inter.respond("Hmmm test success!")

def setup(client):
    client.add_cog(Misc(client))