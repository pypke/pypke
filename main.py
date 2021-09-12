# Discord Imports
import discord
from discord.ext import commands

# Other Imports
import os
from pathlib import Path
from datetime import datetime
from better_profanity import profanity
import asyncio
import motor.motor_asyncio
from urllib.parse import quote_plus
import random
import epoch

# Local Imports
from utils.keep_alive import keep_alive
from utils.mongo import Document
from cogs.moderation import TimeConverter

# Path
cwd = Path(__file__).parents[0]
cwd = str(cwd)

# Lists
owners = [764116023489986601, 624572769484668938]

# Code To Get Prefix
async def get_prefix(client, message):
    # If dm's
    if not message.guild:
        return commands.when_mentioned_or(client.prefix)(client, message)

    try:
        data = await client.config.find(message.guild.id)

        # Make sure we have a useable prefix
        if not data or "prefix" not in data:
            return commands.when_mentioned_or(client.prefix)(client, message)
        return commands.when_mentioned_or(data["prefix"])(client, message)
    except:
        return commands.when_mentioned_or(client.prefix)(client, message)


# Status Cycle
async def status_task():
    while not client.is_closed():
        await client.change_presence(status=discord.Status.idle, activity=discord.Activity(name="@Pypke", type=discord.ActivityType.listening))
        await asyncio.sleep(30)
        await client.change_presence(status=discord.Status.idle, activity=discord.Activity(name="NedHuman | #help", type=discord.ActivityType.listening))
        await asyncio.sleep(30)
        await client.change_presence(status=discord.Status.idle, activity=discord.Game(name="With NedHuman"))
        await asyncio.sleep(30)
        await client.change_presence(status=discord.Status.idle, activity=discord.Activity(name="NedHuman Play Minecraft", type=discord.ActivityType.watching))
        await asyncio.sleep(30)


# Client Info
client = commands.Bot(command_prefix=get_prefix, intents = discord.Intents.all(), owner_ids=owners)
client.remove_command("help")
client.launch_time = datetime.utcnow()
client.cwd = cwd
client.version = "1.7.3"
client.muted_users = {}
client.prefix = "#"
guild_ids=["883378824753066015", "883378824753066015"]
client.colors = {
    "white": 0xFFFFFF,
    "aqua": 0x1ABC9C,
    "green": 0x2ECC71,
    "blue": 0x3498DB,
    "purple": 0x9B59B6,
    "pink": 0xE91E63,
    "gold": 0xF1C40F,
    "orange": 0xE67E22,
    "red": 0xE74C3C,
    "navy": 0x34495E
}
client.color_list = [c for c in client.colors.values()]

#Filter Words
profanity.load_censor_words_from_file(cwd + "/bot_config/filtered_words.txt")

#Mongo DB Stuff
client.connection_url = "mongodb+srv://MrNatural:aman5368@pypke-cluster.ekgfx.mongodb.net/database?retryWrites=true&w=majority"
   
# Invite Viewpanel
# class Button(discord.ui.View):

#     @(self, button: discord.ui.Button, interaction: discord.Interaction):
#         button.
#         button.style = discord.ButtonStyle.success
#         button.label = str("Invite Me")
        
#         await interaction.response.edit_message(view=self)

@client.event
async def on_ready():

    # Client Connection
    asyncio.sleep(10)
    os.system("clear")
    print(f"\u001b[32mSuccessfully Logged In As:\u001b[0m\nName: {client.user.name}\nId: {client.user.id}\nTotal Guilds: {len(client.guilds)}")
    print("---------")
    for file in os.listdir(cwd + "/cogs"):
        if file.endswith(".py") and not file.startswith("_"):
            client.load_extension(f"cogs.{file[:-3]}")
            print(f"{file[:-3].capitalize()} Module Has Been Loaded.")
    client.loop.create_task(status_task())

    # Database Connection
    client.mongo = motor.motor_asyncio.AsyncIOMotorClient(str(client.connection_url))
    client.db = client.mongo["pypke"]
    client.config = Document(client.db, "config")
    client.mutes = Document(client.db, "mutes")
    client.blacklisted_users = Document(client.db, "blacklist")

    # Muted Users
    currentMutes = await client.mutes.get_all()
    for mute in currentMutes:
        client.muted_users[mute["_id"]] = mute

    print(f"\u001b[31m{len(client.muted_users)} Users Are Muted!!\u001b[0m")
    print("\u001b[34mInitialized Database\u001b[0m\n--------")
    

@client.event
async def on_member_join(member):
    # More Updates Needed
    pass
    
@client.event
async def on_member_remove(member):
    # More Updates Needed
    pass

@client.event
async def on_message(message):
    """
    if not message.author.bot:
        if profanity.contains_profanity(message.content.lower()):
            await message.delete()
            await message.channel.send("Hey There, Watch Your Language!!")
    """

    if client.user.mentioned_in(message):
        data = await client.config.get_by_id(message.guild.id)
        if not data or "prefix" not in data:
            prefix = "#"
        else:
            prefix = data["prefix"]

        embed = discord.Embed(title="Bot Mentioned",
                              description=f"Prefix of the bot is `{prefix}`\nDo `{prefix}help` to view help on each command.",
                              colour=discord.Color.blurple())

        await message.channel.send(embed=embed, delete_after=5)

    if "discord.gg" in message.content.lower():
        if message.author.bot:
            return
        if message.author.id in owners:
            return
        else:
            await message.delete()
            await message.channel.send(f'Hey {message.author.mention} :rage: You cannot send discord links on this server!', delete_after=3)

    if "discord.com/invite" in message.content.lower():
        if message.author.bot:
            return
        if message.author.id in owners:
            return
        else:
            await message.delete()
            await message.channel.send(f'Hey {message.author.mention} :rage: You cannot send discord links on this server!', delete_after=3)

    if "tenor.com" in message.content.lower():
        if message.author.bot:
            return
        if message.author.id in owners:
            return
        else:
            await message.delete()
            await message.channel.send(f'Hey {message.author.mention} :rage: You cannot send gifs!', delete_after=3)

    if "giphy.com" in message.content.lower():
        if message.author.bot:
            return
        if message.author.id in owners:
            return
        else:
            await message.delete()
            await message.channel.send(f'Hey {message.author.mention} :rage: You cannot send gifs!', delete_after=3)

    users = await client.blacklisted_users.find(message.author.id)

    # This Checks Whether The Message Author Is Blacklisted Or Not
    if users:
        prefix = get_prefix
        if message.content.startswith(f"{prefix}"):
            await message.channel.send("Hey, Lmao You Are Banned From Using This Bot", delete_after=3)
            return
        else:
            return

    await client.process_commands(message)

# Commands
@client.command()
@commands.is_owner()
async def name(ctx, *, name):
    pog = ctx.guild.get_role(828525798113804288)
    await pog.edit(reason="Edited Name", name=name)


@client.command()
async def invite(ctx):
    embed = discord.Embed(title="Pypke Bot", description="You Can Invite The Bot By Clicking The Button Below!\n__**[Invite Me](https://discord.com/api/oauth2/authorize?client_id=823051772045819905&permissions=8&scope=bot)**__", color=discord.Color.blurple(), timestamp=datetime.now())
    embed.set_footer(text="Bot by Mr.Natural#3549")

    await ctx.send(content="This Bot Is Still In Development You May Experience Downtime!!\n", embed=embed)
    

@client.command(description="Checks How Long The Bot Has Been Running")
async def uptime(ctx):
    delta_uptime = datetime.utcnow() - client.launch_time
    hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    await ctx.send(f"I'm Up For `{days}d, {hours}h, {minutes}m, {seconds}s`")

@client.command()
@commands.is_owner()
async def boosters(ctx):
    role = ctx.guild.premium_subscriber_role
    members = role.members
    if not members:
        return await ctx.send("Sad, No one is boosting this server.")
    embed = discord.Embed(
            title=f"No. Of Booster: {len(members)}",
            description=(
                "\n".join(
                    f"**{i+1}.** {member.display_name}"
                    for i, member in enumerate(members)
                )
            ),
            colour=random.choice(client.color_list),
            timestamp=datetime.now()
        )
    embed.add_field(name="\uFEFF", value=f"Thanks To {role.mention} Above For Boosting This Server. :hugging:")
    embed.set_author(name="Server Boosters")
    embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
    embed.set_thumbnail(url=ctx.guild.icon_url)
    await ctx.send(embed=embed)

@client.command()
async def google(ctx, *, query: str):
    query = quote_plus(query)
    url = f"https://www.google.com/search?q={query}"
    google = discord.Embed(title="Google Search Results", description=f"**Query:** {query}\n**Results:** [Click Here]({url})", color=random.choice(client.color_list), timestamp=datetime.now())
    google.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
    await ctx.send(embed=google)

@client.command()
async def etime(ctx, *, value: TimeConverter=None):
    if value == None:
        epoch_time = round(epoch.now())
    else:
        epoch_time = epoch.now()
        epoch_time = round(epoch_time + value)

    embed = discord.Embed(title="Epoch Time", description="\uFEFF", color=random.choice(client.color_list), timestamp=datetime.now())
    embed.add_field(name="Epoch Timestamp Example", value=f"<t:{epoch_time}:f>\n", inline=False)
    embed.add_field(name="Epoch Timestamp Copy", value=f"`<t:{epoch_time}:f>`\n", inline=False)
    await ctx.send(embed=embed)
    
""" For Slash Command In Future
@client.command(description="Check The Ping Of The Bot")
async def ping(ctx):
    await ctx.send(f":ping_pong: Pong! \nCurrent End-to-End latency is `{round(client.latency * 1000)}ms`")
"""
"""
@client.slash_command()
@commands.is_owner()
async def status(
    ctx,
    act_type: Option(str, "Choose The Type", choices=["Listening", "Watching", "Playing"]),
    text: Option(str, "Text", required=True)
):
    if act_type == "Listening":
        await client.change_presence(status=discord.Status.idle, activity=discord.Activity(name=f"{text}", type=discord.ActivityType.listening))
        await ctx.send("Status Changed Successfully!! Now Listening")

    elif act_type == "Watching":
        await client.change_presence(status=discord.Status.idle, activity=discord.Activity(name=f"{text}", type=discord.ActivityType.watching))
        await ctx.send("Status Changed Successfully!! Now Watching")

    elif act_type == "Playing":
        await client.change_presence(status=discord.Status.idle, activity=discord.Game(name=f"{text}"))
        await ctx.send("Status Changed Successfully!! Now Playing")
"""

keep_alive()
client.run(os.getenv('token'))