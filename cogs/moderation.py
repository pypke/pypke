import discord
from discord.ext import commands, tasks

from dateutil.relativedelta import relativedelta
from copy import deepcopy
from datetime import datetime
from utils.time import TimeConverter
import asyncio

class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.mute_task = self.check_current_mutes.start()

    def cog_unload(self):
        self.mute_task.cancel()

    @tasks.loop(minutes=5)
    async def check_current_mutes(self):
        currentTime = datetime.now()
        mutes = deepcopy(self.client.muted_users)
        for key, value in mutes.items():
            if value['muteDuration'] is None:
                continue

            unmuteTime = value['mutedAt'] + relativedelta(seconds=value['muteDuration'])

            if currentTime >= unmuteTime:
                guild = self.client.get_guild(value['guildId'])
                member = guild.get_member(value['_id'])

                role = discord.utils.get(guild.roles, name="Muted")
                if role in member.roles:
                    await member.remove_roles(role)
                    print(f"Unmuted: {member.display_name}")

                await self.client.mutes.delete(member.id)
                try:
                    self.client.muted_users.pop(member.id)
                except KeyError:
                    pass
    
    @check_current_mutes.before_loop
    async def before_check_current_mutes(self):
        await self.client.wait_until_ready()

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
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, *, time: TimeConverter=None):
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not role:
            await ctx.send("No muted role was found! Please create one called `Muted`")
            return

        try:
            if self.client.muted_users[member.id]:
                await ctx.send("This user is already muted")
                return
        except KeyError:
            pass

        data = {
            '_id': member.id,
            'mutedAt': datetime.now(),
            'muteDuration': time or None,
            'mutedBy': ctx.author.id,
            'guildId': ctx.guild.id,
        }
        await self.client.mutes.upsert(data)
        self.client.muted_users[member.id] = data

        await member.add_roles(role)

        if time and time > 2592000:
            ctx.send("Time cannot be greater than 1 Month/30 Days")
        else:
            pass

        if not time:
            await ctx.send(f"{member.display_name} Was Muted")
        else:
            minutes, seconds = divmod(time, 60)
            hours, minutes = divmod(minutes, 60)
            days, hours = divmod(hours, 24)
            if int(days):
                await ctx.send(
                    f"{member.display_name} was muted for {days} days, {hours} hours, {minutes} minutes and {seconds} seconds"
                )
            elif int(hours):
                await ctx.send(
                    f"{member.display_name} was muted for {hours} hours, {minutes} minutes and {seconds} seconds"
                )
            elif int(minutes):
                await ctx.send(
                    f"{member.display_name} was muted for {minutes} minutes and {seconds} seconds"
                )
            elif int(seconds):
                await ctx.send(f"{member.display_name} was muted for {seconds} seconds")

        if time and time < 300:
            await asyncio.sleep(time)

            if role in member.roles:
                await member.remove_roles(role)
                await ctx.send(f"{member.display_name} Was Unmuted ")

            await self.client.mutes.delete(member.id)
            try:
                self.client.muted_users.pop(member.id)
            except KeyError:
                pass

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not role:
            await ctx.send("No muted role was found! Please create one called `Muted`")
            return

        await self.client.mutes.delete(member.id)
        try:
            self.client.muted_users.pop(member.id)
        except KeyError:
            pass

        if role not in member.roles:
            await ctx.send("This member is not muted.")
            return

        await member.remove_roles(role)
        await ctx.send(f"{member.display_name} Was Unmuted")

def setup(client):
    client.add_cog(Moderation(client))