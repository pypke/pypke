import discord
from discord.ext import commands
import platform
from copy import copy

class Config(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, module: str):
        module = module.lower()
        try:
            self.client.unload_extension(f"cogs.{module}")
            await ctx.send(f"{module.capitalize()} Module Was Successfully Unloaded!")
        except:
            await ctx.send("Nope, Not Like That!")
            return

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, module: str):
        module = module.lower()
        try:
            self.client.load_extension(f"cogs.{module}")
            await ctx.send(f"{module.capitalize()} Module Was Successfully Loaded!")
        except:
            await ctx.send("Nope, Not Like That!")
            return

    @commands.command()
    @commands.is_owner()
    async def reload(self, ctx, module: str):
        module = module.lower()
        try:
            self.client.unload_extension(f"cogs.{module}")
            self.client.load_extension(f"cogs.{module}")
            await ctx.send(f"{module.capitalize()} Module Was Successfully Reloaded!")
        except:
            await ctx.send("Nope, Not Like That!")
            return

    @commands.command()
    @commands.is_owner()
    async def logout(self, ctx):
        try:
            await ctx.message.add_reaction("👋")
        except:
            pass
        await ctx.send(f"{ctx.author.mention}, Successfully Disconnected!! :wave:")
        await self.client.logout()
    
    @commands.command()
    @commands.is_owner()
    async def blacklist(self, ctx, user: discord.Member):
        if ctx.message.author.id == user.id:
            await ctx.send("Hey, you cannot blacklist yourself!")
            return
        if self.client.user.id == user.id:
            await ctx.send("Hey, be senseful you can't blacklist me.")
            return
        await self.client.blacklisted_users.upsert({"_id": user.id, "ban": True})
        await ctx.send(f"Hey, I have blacklisted {user.name}.")

    @commands.command()
    @commands.is_owner()
    async def unblacklist(self, ctx, user: discord.Member):
        data = await self.client.blacklisted_users.find(user.id)
        if not data:
            await ctx.send("Hey, This guy is not blacklisted.")
            return
        await self.client.blacklisted_users.delete(user.id)
        await ctx.send(f"Hey, I have unblacklisted {user.name}.")

    @commands.command()
    async def stats(self, ctx):
        pythonVersion = platform.python_version()
        dpyVersion = discord.__version__
        serverCount = len(self.client.guilds)
        memberCount = len(set(self.client.get_all_members()))

        embed = discord.Embed(title=f"{self.client.user.name} Stats", description="\uFEFF", colour=0x2f3136, timestamp=ctx.message.created_at)

        embed.add_field(name="Bot Version:", value=f"`{self.client.version}`")
        embed.add_field(name="Python Version:", value=f"`{pythonVersion}`")
        embed.add_field(name="Discord.Py Version", value=f"`{dpyVersion}`")
        embed.add_field(name="Total Servers:", value=f"{serverCount} Servers")
        embed.add_field(name="Total Users:", value=f"{memberCount} Users")
        embed.add_field(name="Bot Developers:", value="<@624572769484668938>")

        embed.set_footer(text=f"Mr.Natural#3549 | {self.client.user.name}")
        embed.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)

        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def sudo(self, ctx, victim: discord.Member, *, command):
        """Take control."""
        new_message = copy(ctx.message)
        new_message.author = victim
        new_message.content = ctx.prefix + command
        await self.client.process_commands(new_message)

    # Guild Stuff Owner Only
    @commands.command()
    @commands.is_owner()
    async def shguild(self, ctx):
        desc = ""
        index = 0
        guilds = self.client.guilds
        for guild in guilds:
            guild_name = guild.name
            guild_id = guild.id
            guild_owner_name = guild.owner.name
            index += 1
            desc = desc + f"**Guild #{index}**\nGuild Name: {guild_name}\nGuild Id: {guild_id}\nOwner: {guild_owner_name}\n\n"
            if index > 10:
                break
            
        embed = discord.Embed(
            title="Bot Guilds",
            description=desc,
            color=0x2f3136
        )
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def shinvite(self, ctx, guildid: int):
        try:
            guild = self.client.get_guild(guildid)
            invitelink = ""
            i = 0
            while invitelink == "":
                channel = guild.text_channels[i]
                link = await channel.create_invite(max_age=300, max_uses=1)
                invitelink = str(link)
                i += 1
            await ctx.send(invitelink)
        except Exception:
            await ctx.send("Something went wrong")

    @commands.command()
    @commands.is_owner()
    async def shleave(self, ctx, guildid: int):
        guild = self.client.get_guild(guildid)
        await guild.leave()
        await ctx.send(f":ok_hand: **Left guild**: {guild.name} ({guild.id})")

def setup(client):
    client.add_cog(Config(client))