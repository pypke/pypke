import discord
from discord.ext import commands
from copy import copy
from utils.pagination import Pagination
from typing import Optional, Union


class Owners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def blacklist(self, ctx, user: discord.Member, *, reason: str):
        """Blacklist a user from using the bot."""
        if ctx.message.author.id == user.id:
            await ctx.send("Hey, you cannot blacklist yourself!")
            return
        if self.bot.user.id == user.id:
            await ctx.send("Hey, you can't blacklist me!")
            return
        await self.bot.blacklisted_users.upsert({"_id": user.id, "ban": True, "reason": reason})
        await ctx.send(f"Hey, I have blacklisted {user.name}.")

    @commands.command()
    @commands.is_owner()
    async def unblacklist(self, ctx, user: discord.Member):
        """Remove a user from the blacklist."""
        data: Optional[dict] = await self.bot.blacklisted_users.find(user.id)
        if not data:
            await ctx.send("Hey, this guy is not blacklisted.")
            return
        await self.bot.blacklisted_users.delete(user.id)
        await ctx.send(f"Hey, I have unblacklisted {user.name}.")

    @commands.command()
    @commands.is_owner()
    async def listblacklisted(self, ctx):
        """List all currently blacklisted users."""
        blacklisted_users = await self.bot.blacklisted_users.find_all()
        if not blacklisted_users:
            await ctx.send("No users are currently blacklisted.")
            return

        embeds = []
        for i in range(0, len(blacklisted_users), 25):
            embed = discord.Embed(
                title=f"Current blacklisted users ({i+1}-{min(i+25, len(blacklisted_users))}/{len(blacklisted_users)})",
                color=discord.Color.blurple()
            )
            for user in blacklisted_users[i:i+25]:
                try:
                    user_obj = await self.bot.fetch_user(user["_id"])
                    name = user_obj.name
                except:
                    name = "Unknown"
                embed.add_field(
                    name=f"{name} ({user['_id']}) {'(BANNED)' if user['ban'] else ''}",
                    value=f"Banned: {user['ban']}\nReason: {user.get('reason', 'N/A')}"
                )
            embeds.append(embed)

        await Pagination.paginate(self, ctx, embeds)

    @commands.command()
    @commands.is_owner()
    async def sudo(self, ctx, victim: Union[discord.Member, discord.User], *, command: str):
        """Execute a command as another user."""
        new_message = copy(ctx.message)
        new_message.author = victim
        new_message.content = ctx.prefix + command
        await self.bot.process_commands(new_message)

    @commands.command()
    @commands.is_owner()
    async def sudoleave(self, ctx, guildid: int):
        """Make the bot leave a guild."""
        guild = self.bot.get_guild(guildid)
        if not guild:
            await ctx.send(f"Hey, I'm not a member of guild {guildid}!")
            return
        await guild.leave()
        await ctx.send(f":ok_hand: **Left guild**: {guild.name} ({guild.id})")

    @commands.command()
    @commands.is_owner()
    async def sudoguild(self, ctx):
        """Show information about all guilds the bot is in."""
        guilds = self.bot.guilds
        pages = []
        for guild in guilds:
            embed = discord.Embed(
                title=f"{guild.name} ({guild.id})",
                color=self.bot.transp()
            )
            embed.set_thumbnail(url=guild.icon_url)
            embed.add_field(name="Owner", value=guild.owner)
            embed.add_field(name="Members", value=guild.member_count)
            embed.add_field(name="Region", value=str(guild.region))
            pages.append(embed)
        await Pagination.paginate(self, ctx, pages)


def setup(bot):
    bot.add_cog(Owners(bot))
