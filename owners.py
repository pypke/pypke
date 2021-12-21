import discord
from discord.ext import commands
from copy import copy
from utils.pagination import Pagination


class Owners(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(hidden=True)
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

    @commands.command(hidden=True)
    @commands.is_owner()
    async def unblacklist(self, ctx, user: discord.Member):
        data = await self.client.blacklisted_users.find(user.id)
        if not data:
            await ctx.send("Hey, This guy is not blacklisted.")
            return
        await self.client.blacklisted_users.delete(user.id)
        await ctx.send(f"Hey, I have unblacklisted {user.name}.")

    @commands.command(hidden=True)
    @commands.is_owner()
    async def sudo(self, ctx, victim: discord.Member, *, command):
        """Take control."""
        new_message = copy(ctx.message)
        new_message.author = victim
        new_message.content = ctx.prefix + command
        await self.client.process_commands(new_message)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def shguild(self, ctx):
        desc = ""
        index = 0
        embeds = []
        guilds = self.client.guilds

        for guild in guilds:
            guild_name = guild.name
            guild_id = guild.id
            guild_owner_name = guild.owner
            index += 1
            desc = desc + \
                f"**Guild #{index}**\nGuild Name: {guild_name}\nGuild Id: {guild_id}\nMembers:{len(guild.members)}\nOwner: {guild_owner_name}\n\n"
            if index >= 5:
                embed = discord.Embed(
                    title="Pypke Guilds",
                    description=desc,
                    color=0x2f3136
                )
                embeds.append(embed)
                index = 0

        await Pagination.paginate(self, ctx, embeds)

    @commands.command(hidden=True)
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

    @commands.command(hidden=True)
    @commands.is_owner()
    async def shleave(self, ctx, guildid: int):
        guild = self.client.get_guild(guildid)
        await guild.leave()
        await ctx.send(f":ok_hand: **Left guild**: {guild.name} ({guild.id})")


def setup(client):
    client.add_cog(Owners(client))
