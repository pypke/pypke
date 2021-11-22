import platform, epoch
from datetime import datetime
from psutil import Process, cpu_percent
from os import getpid

import discord
from discord.ext import commands
from dislash import ActionRow, Button, ButtonStyle



class Bot(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['pong'])
    async def ping(self, ctx):
        await ctx.send(f":ping_pong: Pong! \nCurrent End-to-End latency is `{round(self.client.latency * 1000)}ms`")

    @commands.command()
    async def uptime(self, ctx):
        delta_uptime = datetime.now() - self.client.launch_time
        time = int(delta_uptime.total_seconds())   
             
        # Converting Time Back To Readble Letters
        minutes, seconds = divmod(time, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        duration = ""
        if days != 0:
            duration = duration + f"{days} days "
        if hours != 0:
            duration = duration + f"{hours} hrs "
        if minutes != 0:
            duration = duration + f"{minutes} mins "
        if seconds != 0:
            duration = duration + f"{seconds} secs "
        await ctx.send(f"I'm up since {duration}")

    @commands.command()
    async def stats(self, ctx):
        pythonVersion = platform.python_version()
        dpyVersion = discord.__version__
        serverCount = len(self.client.guilds)
        memberCount = len(set(self.client.get_all_members()))
        memoryUsed = f"{round(Process(getpid()).memory_info().rss/1204/1204/1204, 3)} GB Used ({round(Process(getpid()).memory_percent())}%)"
        cpuPercent = cpu_percent()

        embed = discord.Embed(
            title=f"{self.client.user.name} Stats",
            description="\uFEFF",
            colour=0x2f3136,
            timestamp=ctx.message.created_at
        )
        embed.add_field(name="Bot Version:", value=f"`{self.client.version}`")
        embed.add_field(name="Python Version:", value=f"`{pythonVersion}`")
        embed.add_field(name="Discord.py Version", value=f"`{dpyVersion}`")
        embed.add_field(name="Total Servers:", value=f"{serverCount} Servers")
        embed.add_field(name="Total Users:", value=f"{memberCount} Users")
        embed.add_field(name="Memory Used:", value=f"{memoryUsed}")
        embed.add_field(name="CPU Usage:", value=f"{cpuPercent}%")
        embed.add_field(name="Bot Developers:", value="<@624572769484668938>")

        embed.set_footer(text=f"Mr.Natural#3549 | {self.client.user.name}")
        embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar.url)

        await ctx.send(embed=embed)

    @commands.command(name='news', description='See the latest news about this bot!')
    async def news(self, ctx):
        news = discord.Embed(
                        description="**📢 __New Fun Commands Added__**\n• `trivia` to answer difficult questions.\n• `pokedex` to search info about a pokémon.\n• `wyr` to answer would you rather questions.\n• `joke` to read wholesome jokes.\n\n**🤖 __ChatBot AI Implementation__**\n• Use `#chatbot channel [channel-id]` to start ChatBot.\n• Use `#chatbot stop` to stop chatbot.\n\n**🔗 __Some New Links__**\n• [**Website**](https://www.pypke.tk)\n• [**Docs**](https://docs.pypke.tk)\n• [**Support Server**](https://discord.gg/mYXgu2NVzH)",
                        color=0xF7770F
                )
        news.set_footer(text="If you encounter any bugs or breaks report them on our Support Server.")
        news.set_author(name="Bot Changes", url="https://docs.pypke.tk/")
        await ctx.send(embed=news)

    @commands.command(description="Get a link to invite this bot")
    async def invite(self, inter):
        invite_btn = ActionRow(
            Button(
                style=ButtonStyle.link,
                label="Invite",
                url=
                "https://discord.com/oauth2/authorize?client_id=823051772045819905&permissions=8&scope=bot%20applications.commands"
            )
        )
        embed = discord.Embed(
            title="Pypke Bot",
            description="You Can Invite The Bot By Clicking The Button Below!",
            color=discord.Color.blurple(),
            timestamp=datetime.now()
            )
        embed.set_footer(text="Bot by Mr.Natural#3549")
        await inter.send(
            content=
            "This Bot Is Still In Development You May Experience Downtime!!\n",
            embed=embed,
            components=[invite_btn]
        )

    @commands.command(slash_command=True, description="Send feedback to the developer's server.", aliases=["report"])
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def feedback(self, ctx, *, message):
        """Send feedback to the developer's server."""

        channel = await self.client.fetch_channel(911854839074537513)
        embed = discord.Embed(
            title=f"Feedback from {ctx.author}",
            description=message,
            color=self.client.color,
            timestamp=datetime.now()
        )
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
                
        msg = await channel.send(embed=embed)
        await msg.add_reaction("✅")
        await msg.add_reaction("❌")
        
        await ctx.send("Message sent! Thanks for your feedback!")


def setup(client):
    client.add_cog(Bot(client))
