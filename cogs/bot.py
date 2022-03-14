from utils.time import TimeHumanizer

import platform
from datetime import datetime
from psutil import Process, cpu_percent
from os import getpid
from typing import Optional

import discord
from discord.ext import commands
from dislash import ActionRow, Button, ButtonStyle


class Bot(commands.Cog, description="Commands for bot setup & support."):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command(name="ping", description="Check the bot's ping.", aliases=["pong"])
    async def ping(self, ctx):
        await ctx.send(
            f":ping_pong: Pong! \nBot latency is `{round(self.bot.latency * 1000)}ms`."
        )

    @commands.command(name="uptime", description="Check the bot's uptime.")
    async def uptime(self, ctx):
        seconds = self.bot.uptime
        duration = TimeHumanizer(seconds)
        embed = discord.Embed(
            color=self.bot.colors["green"],
            title="Uptime",
            description=f"{duration}",
            timestamp=self.bot.launch_time,
        )
        embed.set_footer(text="Last restarted at")
        await ctx.send(embed=embed)

    @commands.command(name="stats", description="See the bot statistics.")
    async def stats(self, ctx):
        pythonVersion = platform.python_version()
        dpyVersion = discord.__version__
        serverCount = len(self.bot.guilds)
        memberCount = len(set(self.bot.get_all_members()))
        memoryUsed = f"{round(Process(getpid()).memory_info().rss/1204/1204/1204, 3)} GB Used ({round(Process(getpid()).memory_percent())}%)"
        cpuPercent = cpu_percent()
        uptime = TimeHumanizer(self.bot.uptime)
        text_channels = self.bot.text_channels
        voice_channels = self.bot.voice_channels
        stage_channels = self.bot.stage_channels

        embed = discord.Embed(
            description=f"**Ping** `{round(self.bot.latency * 1000)}ms`\n**Uptime** `{uptime}`",
            colour=0x2F3136,
            timestamp=ctx.message.created_at,
        )
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.set_footer(text=f"Made by Mr.Natural#3549")
        embed.set_author(
            name=f"{self.bot.user.name} Stats", icon_url=self.bot.user.avatar.url
        )

        embed.add_field(
            name="Version Info:",
            value=f"Bot Version `{self.bot.version}`\nPython version `{pythonVersion}`\nDpy Version `{dpyVersion}`",
            inline=False,
        )
        embed.add_field(
            name="Counters:",
            value=f"{serverCount} Servers | {memberCount} Users\n"
            + f"<:text_channel:924929739754446870> `{text_channels}` **|** <:voice_channel:924929804833288223> `{voice_channels}` **|** `{stage_channels}`",
        )
        embed.add_field(
            name="System Info:",
            value=f"Memory: `{memoryUsed}` \nCPU usage: `{cpuPercent}%`",
        )

        await ctx.send(embed=embed)

    @commands.command(name="news", description="See the latest news about this bot!")
    async def news(self, ctx):
        news = discord.Embed(
            description="**📢 __New Fun Commands Added__**\n• `trivia` to answer difficult questions.\n• `pokedex` to search info about a pokémon.\n• `wyr` to answer would you rather questions.\n• `joke` to read wholesome jokes.\n\n**🤖 __ChatBot AI Implementation__**\n• Use `#chatbot <channel-id>` to start ChatBot.\n• Use `#chatbot stop` to stop chatbot.\n\n**🔗 __Some New Links__**\n• [**Website**](https://www.pypke.tk)\n• [**Docs**](https://docs.pypke.tk)\n• [**Support Server**](https://discord.gg/mYXgu2NVzH)",
            color=0xF7770F,
        )
        news.set_footer(
            text="If you encounter any bugs or breaks report them on our Support Server."
        )
        news.set_author(name="Bot Changes", url="https://docs.pypke.tk/")
        await ctx.send(embed=news)

    @commands.command(
        name="links",
        description="Get the links related to pypke.",
        aliases=["support", "invite", "docs", "website"],
    )
    async def links_command(self, ctx):
        """Get the links related to pypke."""
        invite_btn = ActionRow(
            Button(
                style=ButtonStyle.link,
                label="Invite Me!",
                url="https://discord.com/oauth2/authorize?bot_id=823051772045819905&permissions=8&scope=bot%20applications.commands",
            ),
            Button(
                style=ButtonStyle.link,
                label="Support Server!",
                url="https://discord.gg/mYXgu2NVzH",
            ),
            Button(style=ButtonStyle.link, label="Website",
                   url="https://www.pypke.tk"),
            Button(style=ButtonStyle.link, label="Docs",
                   url="https://docs.pypke.tk"),
        )
        em = discord.Embed(
            description="Links related to Pypke.", color=self.bot.colors["og_blurple"]
        )
        await ctx.send(embed=em, components=[invite_btn])

    @commands.command(
        name="donate",
        description="Support the bot's development directly by donating.",
        aliases=["patreon"],
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def donate_command(self, ctx):
        donate_btn = ActionRow(
            Button(
                style=ButtonStyle.link,
                label="Donate!",
                url="https://www.patreon.com/pypke",
            ),
            Button(
                style=ButtonStyle.link,
                label="Vote For Us!",
                url="https://top.gg/bot/823051772045819905",
            ),
        )
        em = discord.Embed(
            description="Bot development is hard & I need money for bot hosting as you know.\nSo you can support this bot by donating. Thanks!\nIf you don't have money by still wanna help consider voting for us everyday on topgg. Please",
            color=self.bot.colors["og_blurple"],
        )
        await ctx.send(embed=em, components=[donate_btn])

    @commands.command(
        name="vote",
        description="Vote for the bot because it's really cool!",
        slash_command=True,
    )
    async def vote_command(self, ctx):
        vote_btn = ActionRow(
            Button(
                style=ButtonStyle.link,
                label="Vote For Us!",
                url="https://top.gg/bot/823051772045819905",
            )
        )
        em = discord.Embed(
            description="Vote for Pypke, So that we can continue to exist.",
            color=self.bot.colors["og_blurple"],
        )
        await ctx.send(embed=em, components=[vote_btn])

    @commands.command(
        name="prefix",
        description="Set a custom prefix.",
        aliases=["changeprefix", "setprefix"],
    )
    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def prefix(self, ctx, *, prefix: Optional[str]):
        if not prefix:
            return await ctx.send(
                f"My current prefix for this server is `{ctx.prefix}`. Use `{ctx.prefix}prefix <prefix>` to change it"
            )
        data = await self.bot.config.get(ctx.guild.id)
        if not data:
            await self.bot.config.upsert(
                {
                    "_id": ctx.guild.id,
                    "prefix": prefix,
                }
            )
        else:
            await self.bot.config.change(ctx.guild.id, "prefix", prefix)
            
        self.bot.prefixes[ctx.guild.id] = prefix
        await ctx.send(
            f"The guild prefix is changed to `{prefix}`. Use `{prefix}prefix [prefix]` to change it again!"
        )
        
    @commands.group(
        name="logging",
        description="Set logging channel for the bot.",
        aliases=["setlogging", "setlog"],
    )
    @commands.has_permissions(manage_guild=True)
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def logging_command(self, ctx: commands.Context, channel: Optional[discord.TextChannel]):
        if not channel:
            if ctx.invoked_subcommand:
                return await ctx.invoke(self.bot.get_command("help"), command_or_module="logging")
            
        data = await self.bot.config.get(ctx.guild.id)
        if data:
            await self.bot.config.change(ctx.guild.id, "logging", channel.id)
        else:
            await self.bot.config.upsert(
                {
                    "_id": ctx.guild.id,
                    "logging": channel.id
                }
            )
        
        await ctx.send(f"Logging channel for all the available activities is now set as {channel.mention}")

    @commands.command(
        name="feedback",
        description="Send feedback to the developer's server.",
        aliases=["report"],
    )
    @commands.guild_only()
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def feedback_command(self, ctx, *, message):
        channel = await self.bot.fetch_channel(911854839074537513)
        embed = discord.Embed(
            title=f"Feedback from {ctx.author}",
            description=message,
            color=self.bot.colors["og_blurple"],
            timestamp=datetime.now(),
        )
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)

        msg = await channel.send(embed=embed)
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")

        await ctx.send("Message sent! Thanks for your feedback!")


def setup(bot):
    bot.add_cog(Bot(bot))
