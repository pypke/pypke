import discord
from discord.ext import commands
from copy import copy
from utils.pagination import Pagination


class Owners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(hidden=True)
    @commands.is_owner()
    async def blacklist(self, ctx, user: discord.Member):
        if ctx.message.author.id == user.id:
            await ctx.send("Hey, you cannot blacklist yourself!")
            return
        if self.bot.user.id == user.id:
            await ctx.send("Hey, be senseful you can't blacklist me.")
            return
        await self.bot.blacklisted_users.upsert({"_id": user.id, "ban": True})
        await ctx.send(f"Hey, I have blacklisted {user.name}.")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def unblacklist(self, ctx, user: discord.Member):
        data = await self.bot.blacklisted_users.find(user.id)
        if not data:
            await ctx.send("Hey, This guy is not blacklisted.")
            return
        await self.bot.blacklisted_users.delete(user.id)
        await ctx.send(f"Hey, I have unblacklisted {user.name}.")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def sudo(self, ctx, victim: discord.Member, *, command):
        """Take control."""
        new_message = copy(ctx.message)
        new_message.author = victim
        new_message.content = ctx.prefix + command
        await self.bot.process_commands(new_message)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def sudoleave(self, ctx, guildid: int):
        guild = self.bot.get_guild(guildid)
        await guild.leave()
        await ctx.send(f":ok_hand: **Left guild**: {guild.name} ({guild.id})")


def setup(bot):
    bot.add_cog(Owners(bot))
