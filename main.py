import asyncio
import logging
import os
import random
import re
from copy import deepcopy
from datetime import datetime
from pathlib import Path

import discord
import dislash
import motor.motor_asyncio
import topgg
from discord.ext import commands, tasks

from utils.keep_alive import keep_alive
from utils.mongo import Document

# Path
cwd = Path(__file__).parents[0]
cwd = str(cwd)

# Lists
owners = [624572769484668938]

# Code To Get Prefix


async def get_prefix(client, message):
    """Gives the prefix for that guild.

    Args:
        bot (commands.Bot): The running bot instance.
        message (message): The context message.

    Returns:
        prefix: The prefix for that guild.
    """
    # If dm's
    if not message.guild:
        return bot.prefix

    try:
        return bot.prefixes[message.guild.id]
    except KeyError:
        pass

    try:
        data = await bot.config.find(message.guild.id)

        # Make sure we have a usable prefix
        if not data or "prefix" not in data:
            return bot.prefix

        bot.prefixes[message.guild.id] = data["prefix"]
        return data["prefix"]
    except Exception:
        bot.prefixes[message.guild.id] = bot.prefix
        return bot.prefix


async def status_task():
    while not bot.is_closed():
        await bot.change_presence(
            status=discord.Status.idle,
            activity=discord.Activity(
                name="@Pypke", type=discord.ActivityType.listening
            ),
        )
        await asyncio.sleep(30)
        await bot.change_presence(
            status=discord.Status.idle,
            activity=discord.Activity(
                name="?help | ?invite", type=discord.ActivityType.playing
            ),
        )
        await asyncio.sleep(30)


class PypkeBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix=get_prefix,
            description="A Multi-purpose discord bot and apparently a cat!",
            strip_after_prefix=True,
            case_insensitive=True,
            owner_ids=owners,
            intents=discord.Intents.all(),
            slash_command_guilds=[850732056790827020],
        )

        super().remove_command("help")

        self.__version__ = "v1.7.6"
        self.launch_time = datetime.now()

        self.color = 0x7289DA
        self.colors = {
            "white": 0xF7F8FF,
            "aqua": 0x00A6B4,
            "green": 0x2ECC71,
            "blue": 0x00B6F7,
            "cyan": 0x6EFACC,
            "purple": 0x9B58AF,
            "pink": 0xFF8AB9,
            "yellow": 0xF1C40F,
            "orange": 0xF7770F,
            "red": 0xF60030,
            "new_blurple": 0x5865F2,
            "og_blurple": 0x7289DA,
        }
        self.color_list = [c for c in self.colors.values()]

    @property
    def random_color(self):
        return random.choice(self.color_list)

    @property
    def uptime(self):
        delta = datetime.now() - self.launch_time
        uptime = int(delta.total_seconds())
        return uptime

    @property
    def text_channels(self):
        channels = 0
        for guild in self.guilds:
            channels += len(guild.text_channels)

        return channels

    @property
    def voice_channels(self):
        channels = 0
        for guild in self.guilds:
            channels += len(guild.voice_channels)

        return channels

    @property
    def stage_channels(self):
        channels = 0
        for guild in self.guilds:
            channels += len(guild.stage_channels)

        return channels


# Bot Info
bot = PypkeBot()
bot.topgg = topgg.DBLClient(bot, token=os.getenv("topgg"), autopost=True)
bot.slash = dislash.InteractionClient(bot, modify_send=True)

bot.cwd = cwd
bot.version = "v1.7.6"
bot.muted_users = {}
bot.current_giveaways = {}
bot.current_afks = {}
bot.prefix = "?"
bot.prefixes = {}
bot.afk_allowed_channel = {}

# Mongo DB Stuff
MONGO_URL = os.getenv("mongo")

if __name__ == "__main__":
    # Loading cogs
    os.system("clear")
    for file in os.listdir(cwd + "/cogs"):
        if file.endswith(".py") and not file.startswith("_"):
            bot.load_extension(f"cogs.{file[:-3]}")
    bot.load_extension("jishaku")
    # bot.load_extension('slashcogs.mod')

    # Database Connection
    bot.mongo = motor.motor_asyncio.AsyncIOMotorClient(str(MONGO_URL))
    bot.db = bot.mongo["pypke"]
    bot.config = Document(bot.db, "config")  # For prefixes
    bot.mutes = Document(bot.db, "mutes")  # For muted users
    bot.blacklisted_users = Document(bot.db, "blacklist")  # For blacklisted users
    bot.giveaways = Document(bot.db, "giveaways")  # For Giveaways
    bot.afks = Document(bot.db, "afks")  # For afk users
    bot.chatbot = Document(bot.db, "chatbot")  # For chatbot
    bot.remind = Document(bot.db, "remind")  # For remind command
    bot.ticket_config = Document(bot.db, "ticket_config")
    bot.active_tickets = Document(bot.db, "active_tickets")

    print("\u001b[34mInitialized Database\u001b[0m\n---")

    logging.basicConfig(
        level=logging.ERROR,
        filename="data/errors.log",
        format="%(asctime)s %(name)s %(levelname)s: %(message)s",
    )
    bot.logger = logging.getLogger("pypke")


@tasks.loop(seconds=30)
async def update_db_cache():  # To update cache every 5 minutes
    # Current mutes
    currentMutes = await bot.mutes.get_all()
    for mute in currentMutes:
        bot.muted_users[mute["_id"]] = mute

    # Current giveaways
    currentGiveaways = await bot.giveaways.get_all()
    for giveaway in currentGiveaways:
        bot.current_giveaways[giveaway["_id"]] = giveaway

    currentAfks = await bot.afks.get_all()
    for afk in currentAfks:
        bot.current_afks[afk["_id"]] = afk


@bot.event
async def on_ready():
    await bot.wait_until_ready()
    # bot Connection
    os.system("clear")
    print(
        f"\u001b[32mSuccessfully Logged In As:\u001b[0m\nName: {bot.user.name}\nId: {bot.user.id}\nTotal Guilds: {len(bot.guilds)}"
    )
    print("---------")
    update_db_cache.start()
    bot.loop.create_task(status_task())


@bot.event
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

    # If the bot is mentioned tell the server prefix.
    if re.fullmatch(rf"<@!?{bot.user.id}>", message.content):
        prefix = await get_prefix(bot, message)

        embed = discord.Embed(
            title="Bot Mentioned",
            description=f"Prefix of the bot is `{prefix}`\nDo `{prefix}help` to view help on each command.",
            colour=bot.colors["og_blurple"],
        )

        await message.channel.send(embed=embed, delete_after=5)

    afks = deepcopy(bot.current_afks)
    for key, value in afks.items():
        member = await message.guild.fetch_member(value["_id"])
        if member.mentioned_in(message):
            await message.channel.send(
                f"`{member.display_name}` is AFK: {value['status']} - <t:{round(datetime.timestamp(value['started_when']))}:R>"
            )

    try:
        afk_data = bot.current_afks[message.author.id]
    except KeyError:
        afk_data = None
    if afk_data:
        try:
            channels = bot.afk_allowed_channel[message.author.id]
        except KeyError:
            channels = []
        if not message.channel.id in channels:
            await bot.afks.delete(message.author.id)
            if "AFK | " in message.author.display_name:
                await message.author.edit(nick=message.author.display_name[6:])
            await message.channel.send(
                f"Welcome back {message.author.mention}, I removed your AFK."
            )

            try:
                bot.current_afks.pop(message.author.id)
            except KeyError:
                pass

    # This checks whether the user is blacklisted or not.
    users = await bot.blacklisted_users.find(message.author.id)
    if users:
        prefix = bot.prefixes[message.guild.id]
        if message.content.startswith(f"{prefix}"):
            await message.channel.send(
                "Hey, lol you did something bad you are banned from using this bot.",
                delete_after=3,
            )
            return
        else:
            return

    await bot.process_commands(message)


async def start():
    print("Starting bot....")
    await bot.start(os.getenv("TOKEN"))


if __name__ == "__main__":
    keep_alive()  # Start the keep alive server
    asyncio.run(start())
