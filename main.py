# Discord Imports
import discord
from discord.ext import commands
from dislash import InteractionClient

# Other Imports
import os, asyncio, random
from pathlib import Path
from datetime import datetime
from better_profanity import profanity
import motor.motor_asyncio

# Local Imports
from utils.mongo import Document

# Path
cwd = Path(__file__).parents[0]
cwd = str(cwd)

# Lists
owners = [624572769484668938]

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
        await client.change_presence(status=discord.Status.idle, activity=discord.Activity(name="#help | #invite", type=discord.ActivityType.listening))
        await asyncio.sleep(30)

# Client Info
client = commands.Bot(command_prefix=get_prefix, intents = discord.Intents.all(), owner_ids=owners)
client.remove_command("help")
client.slash = InteractionClient(client)

client.launch_time = datetime.now()
client.cwd = cwd
client.version = "1.7.5"
client.muted_users = {}
client.current_giveaways = {}
client.prefix = "#"
client.color = 0xF7770F
client.colors = {
    "white": 0xFFFFFF,
    "aqua": 0x60BAAF,
    "green": 0x2ECC71,
    "blue": 0x3498DB,
    "purple": 0x9B59B6,
    "pink": 0xE91E63,
    "gold": 0xF1C40F,
    "orange": 0xF7770F,
    "red": 0xED4245,
    "new_blurple": 0x5865F2,
    "og_blurple": 0x7289da
}
client.color_list = [c for c in client.colors.values()]
client.randcolor = random.choice(client.color_list)

#Mongo DB Stuff
client.connection_url = os.getenv('mongo')

#Filter Words
profanity.load_censor_words_from_file(cwd + "/data/filtered_words.txt")

if __name__ == "__main__":
    # Loading cogs
    os.system("clear")
    for file in os.listdir(cwd + "/cogs"):
        if file.endswith(".py") and not file.startswith("_"):
            client.load_extension(f"cogs.{file[:-3]}")
            print(f"{file[:-3].capitalize()} Loaded")
    client.load_extension('jishaku')

    # Database Connection
    client.mongo = motor.motor_asyncio.AsyncIOMotorClient(str(client.connection_url))
    client.db = client.mongo["pypke"]
    client.config = Document(client.db, "config")
    client.mutes = Document(client.db, "mutes")
    client.blacklisted_users = Document(client.db, "blacklist")
    client.giveaways = Document(client.db, "giveaways")
    client.afks = Document(client.db, "afks")
    client.chatbot = Document(client.db, "chatbot")
    

    print(f"\u001b[31m{len(client.muted_users)} Users Are Muted!!\u001b[0m")
    print("\u001b[34mInitialized Database\u001b[0m\n--------")

@client.event
async def on_ready():
    await client.wait_until_ready()
    # Client Connection
    print(f"\u001b[32mSuccessfully Logged In As:\u001b[0m\nName: {client.user.name}\nId: {client.user.id}\nTotal Guilds: {len(client.guilds)}")
    print("---------")
    client.loop.create_task(status_task())

        
    # Muted Users
    currentMutes = await client.mutes.get_all()
    for mute in currentMutes:
        client.muted_users[mute["_id"]] = mute

    # Current Giveaways
    currentGiveaways = await client.giveaways.get_all()
    for ga in currentGiveaways:
        client.current_giveaways[ga["_id"]] = ga 
    
@client.event
async def on_member_join(member):
    # More Updates Needed
    pass
    
@client.event
async def on_member_remove(member):
    # More Updates Needed
    pass

@client.event
async def on_guild_join(guild):
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
    # Checks If Message Author Is A Bot
    if message.author.bot:
        return
    
    # If The Bot Is Mentioned Tell The Bot's Prefix
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
    
    # If User Has Set Afk Tell The Message Author That He/She Is Afk
    afks = await client.afks.get_all()
    for value in afks:
        if str(value['_id']) in message.content.lower():
            afk_user = message.guild.get_member(value['_id'])
            afk_embed = discord.Embed(
                title=f"{afk_user.name} Is Afk!",
                color=afk_user.color,
                timestamp=datetime.now()
            )
            if value['text'] is None:
                afk_embed.description=discord.Embed.Empty
            else:
                afk_embed.description=f"**Status:** {value['text']}"
            
            afk_embed.set_footer(text="Don't Ping This User Pls!")
            afk_embed.set_thumbnail(url=afk_user.avatar.url)
            await message.channel.send(embed=afk_embed)
        
    # chat_guilds = await client.chatbot.get_all()
    # # for guild in chat_guilds:
    # if message.channel.id == 892071521634361345:
    #     response = chatbot.get_response(message.content)
    #     await message.reply(response, mention_author=False)

    """
    if "discord.gg" or "discord.com/invite" in message.content.lower():
        if message.author.bot:
            return
        if message.author.id in owners:
            return
        if message.author.has_permissions(manage_guild=True):
            return
        else:
            await message.delete()
            await message.channel.send(f'Hey {message.author.mention} :rage: You cannot send discord links on this server!', delete_after=3)

    if "tenor.com" or "giphy.com" in message.content.lower():
        if message.author.bot:
            return
        if message.author.id in owners:
            return
        if message.author.has_permissions(manage_guild=True):
            return
        else:
            await message.delete()
            await message.channel.send(f'Hey {message.author.mention} :rage: You cannot send gifs!', delete_after=3)
    """

    # This Checks Whether The Message Author Is Blacklisted Or Not
    users = await client.blacklisted_users.find(message.author.id)
    if users:
        prefix = get_prefix
        if message.content.startswith(f"{prefix}"):
            await message.channel.send("Hey, Lmao You Are Banned From Using This Bot", delete_after=3)
            return
        else:
            return

    await client.process_commands(message)

# <--- Commands --->
# @sclient.slash_command(description="Check the ping of the bot")
# async def ping(inter):
#     await inter.reply(type=4, content=f":ping_pong: Pong! \nCurrent End-to-End latency is `{round(client.latency * 1000)}ms`", ephemeral=True)

# @sclient.slash_command(description="Get a link to invite this bot")
# async def invite(inter):
#     invite_btn = ActionRow(Button(
#                 style=ButtonStyle.link,
#                 label="Invite",
#                 url= "https://discord.com/oauth2/authorize?client_id=823051772045819905&permissions=8&scope=bot%20applications.commands"
#             ))
#     embed = discord.Embed(title="Pypke Bot", description="You Can Invite The Bot By Clicking The Button Below!", color=discord.Color.blurple(), timestamp=datetime.now())
#     embed.set_footer(text="Bot by Mr.Natural#3549")

#     await inter.reply(type=4, content="This Bot Is Still In Development You May Experience Downtime!!\n", embed=embed, components=[invite_btn])
    
# @sclient.slash_command(description="Checks for how long the bot is up")
# async def uptime(inter):
#     delta_uptime = datetime.now() - client.launch_time
#     hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
#     minutes, seconds = divmod(remainder, 60)
#     days, hours = divmod(hours, 24)
#     await inter.reply(type=4, content=f"I'm Up For `{days}d, {hours}h, {minutes}m, {seconds}s`", ephemeral=True)

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
    embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar.url)
    embed.set_thumbnail(url=ctx.guild.icon_url)
    await ctx.send(embed=embed)
    
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
client.run(os.getenv('token'), reconnect=True)
