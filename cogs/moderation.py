import discord
from discord.ext import commands


class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No Reason Provided"):
        try:
            await member.send(
                f"You Have Been Kicked From {member.guild.name}, Because " + reason)
        except:
            await ctx.send("The Member Has Their DMs Closed!")
        await member.kick(reason=reason)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No Reason Provided"):
        await ctx.send(f"{member} Been Banned From {member.guild.name}, Because " + reason)
        await member.ban(reason=reason)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, *, member):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(member_name + " has been unbanned!")
                return
        await ctx.send(member + " was not found!")

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def mute(self, ctx, member: discord.Member):
        muted_role = ctx.guild.get_role(822852164174348308)
        if muted_role in member.roles:
            await ctx.send(f"{member} is already muted!!")
            return
        await member.add_roles(muted_role)
        await ctx.send(member.mention + " Has Been Muted!")

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def unmute(self, ctx, member: discord.Member):
        muted_role = ctx.guild.get_role(822852164174348308)

        await member.remove_roles(muted_role)
        await ctx.send(member.mention + " Has Been Unmuted!")

def setup(client):
    client.add_cog(Moderation(client))