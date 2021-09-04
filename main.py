# Discord Imports
import discord
from discord.ext import commands
from discord.app import Option

# Other Imports
import os
from pathlib import Path
from datetime import datetime
from better_profanity import profanity
import asyncio
import motor.motor_asyncio

# Local Imports
from keep_alive import keep_alive
from utils.mongo import Document

# Path
cwd = Path(__file__).parents[0]
cwd = str(cwd)

# Lists
owners = [764116023489986601, 624572769484668938]

# Code To Get Prefix
async def get_prefix(client, message):
    # If dm's
    if not message.guild:
        return commands.when_mentioned_or("#")(client, message)

    try:
        data = await client.config.find(message.guild.id)

        # Make sure we have a useable prefix
        if not data or "prefix" not in data:
            return commands.when_mentioned_or("#")(client, message)
        return commands.when_mentioned_or(data["prefix"])(client, message)
    except:
        return commands.when_mentioned_or("#")(client, message)


# Status Cycle
async def status_task():
    while not client.is_closed():
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
client.version = "1.7.3"

#Filter Words
profanity.load_censor_words_from_file(cwd + "/bot_config/filtered_words.txt")

#Mongo DB Stuff
client.connection_url = "mongodb+srv://MrNatural:aman5368@pypke-cluster.ekgfx.mongodb.net/database?retryWrites=true&w=majority"


@client.event
async def on_ready():

    # Client Connection
    asyncio.sleep(10)
    os.system("clear")
    print(f"\u001b[32mSuccessfully Logged In As:\u001b[0m\nName: {client.user.name}\nId: {client.user.id}")
    print(f"Path: {cwd}")
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
    print("Initialized Database\n--------")

    # Extra Stuff
    client.blacklisted_users = Document(client.db, "blacklist")

@client.event
async def on_member_join(member):
    if member.guild.id == 798760033281507337:
        embed = discord.Embed(title=f"Welcome To {member.guild.name}! {member}", description=f":tada: {member.guild.name}\n\nThanks For Joining & Here is our Link If You Want To Invite Your Friends:", color=discord.Color.orange())
        embed.add_field(name="Links", value="[Discord Server](https://discord.gg/BaMAZB2Hrb)\n[YouTube](https://youtube.com/c/NedHuman)\n\nBe Sure To Check Out <#822852164539514932> To Gain Access To Rest Of The Server!")
        embed.set_thumbnail(url='{}'.format(member.avatar_url))
        embed.set_footer(text="Enjoy Your Stay! 🤗", icon_url="{}".format(member.avatar_url))
        await member.send(embed=embed)
    else:
        pass

    if member.guild.id == 770016980379762770:
        join_channel = client.get_channel(772734602166796308)
        embed2 = discord.Embed(title=f"Welcome To {member.guild.name}!", description=f"**{member.name}**\n\nWelcome {member.mention} To {member.guild.name}!", color=discord.Color.orange())
        embed2.set_thumbnail(url='{}'.format(member.avatar_url))
        embed2.set_footer(text="Enjoy Your Stay! 🤗", icon_url="{}".format(member.guild.icon_url))
        embed2.set_image(url="https://cdn.discordapp.com/attachments/815886601364176966/831515105963409488/standard_4.gif")
        embed2.set_author(name=f"{member.name}", icon_url='{}'.format(member.avatar_url))
        await join_channel.send(embed=embed2)
    elif member.guild.id == 798760033281507337:
        join_channel = client.get_channel(822852164313415739)
        embed2 = discord.Embed(title=f"Welcome To {member.guild.name}!", description=f"**{member.name}**\n\nWelcome {member.mention} To {member.guild.name}!", color=discord.Color.orange())
        embed2.set_thumbnail(url='{}'.format(member.avatar_url))
        embed2.set_footer(text="Enjoy Your Stay! 🤗", icon_url="{}".format(member.guild.icon_url))
        embed2.set_image(url="https://cdn.discordapp.com/attachments/822852164313415734/823061048587845673/standard_1.gif")
        embed2.set_author(name=f"{member.name}", icon_url='{}'.format(member.avatar_url))
        await join_channel.send(embed=embed2)

@client.event
async def on_member_remove(member):
    if member.guild.id == 770016980379762770:
        leave_channel=client.get_channel(773913564435316756)
        await leave_channel.send(f"{member.name}, Has Left Us...")
    elif member.guild.id == 798760033281507337:
        leave_channel=client.get_channel(822852164539514930)
        await leave_channel.send(f"{member.name}, Has Left Us...")

@client.event
async def on_message(message):
    """
    if not message.author.bot:
        if profanity.contains_profanity(message.content.lower()):
            await message.delete()
            await message.channel.send("Hey There, Watch Your Language!!")
    """

    if message.content.startswith(f"<@!{client.user.id}>") and len(message.content) == len(f"<@!{client.user.id}>"
    ):
        data = await client.config.get_by_id(message.guild.id)
        if not data or "prefix" not in data:
            prefix = "#"
        else:
            prefix = data["prefix"]

        embed = discord.Embed(title="Bot Mentioned",
                              description=f"Prefix of the bot is `{prefix}`\nDo `{prefix}help` to view help on each command.",
                              colour=discord.Color.blurple())
        embed.set_thumbnail(url="{}".format(message.guild.icon_url))

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

    data = await client.blacklisted_users.find(message.author.id)

    # This Checks Whether The Message Author Is Blacklisted Or Not
    if data:
        prefix = get_prefix
        if message.content.startswith(f"{prefix}"):
            await message.channel.send("Hey, Lmao You Are Banned From Using This Bot")
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

@client.slash_command(description="Checks How Long The Bot Has Been Running")
async def uptime(ctx):
    delta_uptime = datetime.utcnow() - client.launch_time
    hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)
    await ctx.send(f"I'm Up For `{days}d, {hours}h, {minutes}m, {seconds}s`")

@client.command()
async def boosters(ctx):
    role = ctx.guild.premium_subscriber_role
    members = role.members
    embed = discord.Embed(title="__Server Boosters__", description=f"No. Of Booster: {len(members)}\nThanks To The Boosters Below For Boosting This Server. :hugging:", color=0xff69b4)
    i = 1
    for member in members:
        embed.add_field(name="\uFEFF", value=f"**{i}.** {member} - {member.mention}")
        i = i + 1
        if i > 20:
            break
        
    embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar_url)
    embed.set_thumbnail(url=ctx.guild.icon_url)
    await ctx.send(embed=embed)

@client.slash_command(guild_ids=[770016980379762770])
async def ping(ctx):
    await ctx.send(f":ping_pong: Pong! \nCurrent End-to-End latency is `{round(client.latency * 1000)}ms`")

@client.slash_command(guild_ids=[770016980379762770])
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

keep_alive()
client.run(os.getenv('token'))