import asyncio
from dateutil.relativedelta import relativedelta
from copy import deepcopy
from datetime import datetime
from utils.time import TimeConverter, TimeHumanizer
from typing import Optional, Union

import discord
from discord.ext import commands, tasks
from discord.ext.commands import Greedy


class Moderation(commands.Cog):
    """Commands for server Moderation."""

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

            unmuteTime = value['mutedAt'] + \
                relativedelta(seconds=value['muteDuration'])

            if currentTime >= unmuteTime:
                guild = self.client.get_guild(value['guildId'])
                offender = guild.get_member(value['_id'])
                moderator = guild.get_member(value['mutedBy'])

                role = discord.utils.get(guild.roles, name="Muted")
                if role in offender.roles:
                    await offender.remove_roles(role)
                    print(f"Unmuted: {offender}")

                await self.client.mutes.delete(offender.id)
                try:
                    self.client.muted_users.pop(offender.id)
                except KeyError:
                    pass

    @check_current_mutes.before_loop
    async def before_check_current_mutes(self):
        await self.client.wait_until_ready()

    @commands.command(name="kick", description="Kick the member from this server.", cooldown_after_parsing=True)
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def kick_command(self, ctx, member: discord.Member, *, reason="No Reason Provided"):
        if not reason:
            reason = f"No reason provided. ({ctx.author})"
        else:
            reason = reason + f" {ctx.author} (ID: {ctx.author.id})"

        if member in ctx.guild.members:
            if ctx.author.top_role.position < member.top_role.position and member in ctx.guild.members:
                return await ctx.send(f"Can't kick {member} because you don't have higher role.")

            if ctx.author.top_role.position == member.top_role.position and member in ctx.guild.members:
                return await ctx.send(f"Can't kick {member} because you both has similar role hierarchy.")

            if ctx.guild.me.top_role.position < member.top_role.position:
                return await ctx.send(f"Can't kick {member} because the member has higher role than the bot.")

            if ctx.guild.me.top_role.position == member.top_role.position:
                return await ctx.send(f"Can't kick {member} because the member has similar role hierarchy as the bot.")

        try:
            await member.kick(reason=reason)
        except Exception:
            await ctx.send(f"Unable To Kick {member}! Are You Sure That The Bot Has Higher Role Than {member} Or The Bot Isn't Missing Permissions!")
            return

        await ctx.send(f"Kicked {member}!")

    @commands.command(name="ban", description="Bans a member whether or not the member is in the server.", aliases=["forceban", "hackban"], cooldown_after_parsing=True)
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def ban_command(self, ctx, member: Union[discord.Member, discord.User], delete_days: Optional[int], *, reason=None):
        if not reason:
            reason = f"No reason provided. ({ctx.author})"
        else:
            reason = reason + f" {ctx.author} (ID: {ctx.author.id})"

        if not delete_days:
            delete_days = 0
        if 0 > delete_days > 7:
            return await ctx.send("Argument `delete_days` should be more than 0 or less than 7")

        if member in ctx.guild.members:
            if ctx.author.top_role.position < member.top_role.position and member in ctx.guild.members:
                return await ctx.send(f"Can't ban {member} because you don't have higher role.")

            if ctx.author.top_role.position == member.top_role.position and member in ctx.guild.members:
                return await ctx.send(f"Can't ban {member} because you both has similar role hierarchy.")

            if ctx.guild.me.top_role.position < member.top_role.position:
                return await ctx.send(f"Can't ban {member} because the member has higher role than the bot.")

            if ctx.guild.me.top_role.position == member.top_role.position:
                return await ctx.send(f"Can't ban {member} because the member has similar role hierarchy as the bot.")

            await member.ban(delete_message_days=delete_days, reason=reason)
        else:
            try:
                await ctx.guild.ban(user=member, delete_message_days=delete_days, reason=reason)
            except discord.HTTPException:
                await ctx.send(f"Unable to ban {member}")
                return

        await ctx.send(f"Banned {member}.")

    @commands.command(name="unban", description="Unban banned user from this server.", cooldown_after_parsing=True)
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def unban_command(self, ctx, member: discord.User, *, reason: Optional[str]):
        if not reason:
            reason = f"No reason provided. ({ctx.author})"
        else:
            reason = reason + f" {ctx.author} (ID: {ctx.author.id})"

        banned_users = await ctx.guild.bans()

        for ban_entry in banned_users:
            user = ban_entry.user
            member_id = member.id
            user_id = user.id

            if member_id == user_id:
                await ctx.guild.unban(user, reason=reason)
                await ctx.send(f"{member} Is Unbanned!")
                return

    @commands.command(name="massban", description="Bans any number of members whether or not they're in the server.", cooldown_after_parsing=True)
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def massban_command(self, ctx, delete_days: Optional[int], members: Greedy[Union[discord.Member, discord.User]]):

        if len(members) <= 0:
            return await ctx.send("You need to specify members to ban.")
        delete_days = delete_days or 0
        reason = f"Massban by {ctx.author} (ID: {ctx.author.id})"

        if 0 > delete_days > 7:
            return await ctx.send("Argument `delete_days` should be more than 0 or less than 7")

        for member in members:

            if member in ctx.guild.members:
                if ctx.author.top_role.position < member.top_role.position:
                    return await ctx.send(f"Can't ban {member}. (You need to be higher in the role hierarchy.)")

                if ctx.author.top_role.position == member.top_role.position:
                    return await ctx.send(f"Can't ban {member} because you both has similar role hierarchy.")

                if ctx.guild.me.top_role.position < member.top_role.position:
                    return await ctx.send(f"Can't ban {member} because the member has higher role than the bot.")

                if ctx.guild.me.top_role.position == member.top_role.position:
                    return await ctx.send(f"Can't ban {member} because the member has similar role hierarchy as the bot.")

                await member.ban(delete_message_days=delete_days, reason=reason)
                await ctx.send(f"Banned {member}.")

            else:
                try:
                    await ctx.guild.ban(user=member, delete_message_days=delete_days, reason=reason)
                    await ctx.send(f"Banned {member}.")

                except discord.HTTPException:
                    await ctx.send(f"Unable to ban {member}.")

    @commands.command(name="softban", description="Softban a member to clear all his/her messages. Bans a user then instantly unbans them.", cooldown_after_parsing=True)
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def softban_command(self, ctx, member: Union[discord.Member, discord.User], delete_days: Optional[int] = 2, *, reason: Optional[str]):
        if not reason:
            reason = f"No reason provided. ({ctx.author})"
        else:
            reason = reason + f" (Soft-Banned by {ctx.author})"

        if 0 > delete_days > 7:
            return await ctx.send("Argument `delete_days` should be more than 0 or less than 7")

        if member in ctx.guild.members:
            if ctx.author.top_role.position < member.top_role.position and member in ctx.guild.members:
                return await ctx.send(f"Can't ban {member} because you don't have higher role.")

            if ctx.author.top_role.position == member.top_role.position and member in ctx.guild.members:
                return await ctx.send(f"Can't ban {member} because you both has similar role hierarchy.")

            if ctx.guild.me.top_role.position < member.top_role.position:
                return await ctx.send(f"Can't ban {member} because the member has higher role than the bot.")

            if ctx.guild.me.top_role.position == member.top_role.position:
                return await ctx.send(f"Can't ban {member} because the member has similar role hierarchy as the bot.")

            await member.ban(delete_message_days=delete_days, reason=reason)
        else:
            try:
                await ctx.guild.ban(user=member, delete_message_days=delete_days, reason=reason)
            except discord.HTTPException:
                await ctx.send(f"Unable to ban {member.id}")
                return

        await ctx.guild.unban(member, reason=reason)
        await ctx.send(f"Soft-Banned {member}.")

    @commands.command(name="mute", description="Mute a member. isn't that self explainatory?", cooldown_after_parsing=True)
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, *, time: TimeConverter = None):
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
            await ctx.send(f"{member} Was Muted")
            modlogs = discord.utils.get(ctx.guild.channels, name="modlogs")
            embed = discord.Embed(
                title="Muted",
                description=f"Offender: {member} | {member.mention}\nModerator: {ctx.author}",
                color=discord.Color.red(),
                timestamp=datetime.now()
            )
            await modlogs.send(embed=embed)
        else:
            # Converting Time Back To Readble Letters
            minutes, seconds = divmod(time, 60)
            hours, minutes = divmod(minutes, 60)
            days, hours = divmod(hours, 24)
            duration = ""
            if days != 0:
                duration = duration + f"{days} days "
            if hours != 0:
                duration = duration + f"{hours} hours "
            if minutes != 0:
                duration = duration + f"{minutes} minutes "
            if seconds != 0:
                duration = duration + f"{seconds} seconds "

            try:
                modlogs = discord.utils.get(ctx.guild.channels, name="modlogs")
                embed = discord.Embed(
                    title="Muted",
                    description=f"Offender: {member} | {member.mention}\nModerator: {ctx.author}\nDuration: {duration}",
                    color=discord.Color.red(),
                    timestamp=datetime.now()
                )
                await modlogs.send(embed=embed)
                await ctx.send(f"{member} was muted for {duration}")
            except:
                await ctx.send(f"{member} was muted for {duration}")

        if time and time < 300:
            await asyncio.sleep(time)
            try:
                modlogs = discord.utils.get(ctx.guild.channels, name="modlogs")
                embed = discord.Embed(
                    title="Unmuted",
                    description=f"Offender: {member} | {member.mention}\nModerator: {ctx.author}\nDuration: {duration}",
                    color=discord.Color.green(),
                    timestamp=datetime.now()
                )
                await modlogs.send(embed=embed)
            except:
                pass

            if role in member.roles:
                await member.remove_roles(role)
                await ctx.send(f"{member} Was Unmuted ")

            await self.client.mutes.delete(member.id)
            try:
                self.client.muted_users.pop(member.id)
            except KeyError:
                pass

    @commands.command(name="unmute", description="Unmute a muted member.", cooldown_after_parsing=True)
    @commands.guild_only()
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not role:
            await ctx.send("No muted role was found! Please create one called `Muted`")
            return

        if role not in member.roles:
            await ctx.send("This member is not muted.")
            return

        await self.client.mutes.delete(member.id)
        try:
            self.client.muted_users.pop(member.id)
        except KeyError:
            pass

        await member.remove_roles(role)
        await ctx.send(f"{member} Was Unmuted")
        try:
            modlogs = discord.utils.get(ctx.guild.channels, name="modlogs")
            embed = discord.Embed(
                title="Unmuted",
                description=f"Offender: {member} | {member.mention}\nModerator: {ctx.author}",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            await modlogs.send(embed=embed)
        except:
            pass

    # @commands.command(name="timeout", description="Timeouts the user. Works better than mute.", cooldown_after_parsing=True)
    # @commands.guild_only()
    # @commands.has_permissions(moderate_members=True)
    # async def timeout(self, ctx, member: discord.Member, *, time: TimeConverter):
    #     if time > 2419200:
    #         return await ctx.send("Time cannot be greater than 28 days.")

    #     if ctx.author.top_role.position < member.top_role.position and member in ctx.guild.members:
    #         return await ctx.send(f"Can't timeout {member} because you don't have higher role.")
    #     elif ctx.author.top_role.position == member.top_role.position and member in ctx.guild.members:
    #         return await ctx.send(f"Can't timeout {member} because you both has similar role hierarchy.")
    #     elif ctx.guild.me.top_role.position < member.top_role.position:
    #         return await ctx.send(f"Can't timeout {member} because the member has higher role than the bot.")
    #     elif ctx.guild.me.top_role.position == member.top_role.position:
    #         return await ctx.send(f"Can't timeout {member} because the member has similar role hierarchy as the bot.")

    #     await member.timeout(duration=time, reason=f"Timeout by {ctx.author} (ID: {ctx.author.id})")
    #     await ctx.send(f"Timed out {member}` for {TimeHumanizert(time)}.")

    # @commands.command(name="untimeout", description="Remove timeout from the user.", cooldown_after_parsing=True)
    # @commands.guild_only()
    # @commands.has_permissions(moderate_members=True)
    # async def untimeout(self, ctx, member: discord.Member, *, reason: Optional[str]):
    #     if ctx.author.top_role.position < member.top_role.position and member in ctx.guild.members:
    #         return await ctx.send(f"Can't untimeout {member} because you don't have higher role.")
    #     elif ctx.author.top_role.position == member.top_role.position and member in ctx.guild.members:
    #         return await ctx.send(f"Can't untimeout {member} because you both has similar role hierarchy.")
    #     elif ctx.guild.me.top_role.position < member.top_role.position:
    #         return await ctx.send(f"Can't untimeout {member} because the member has higher role than the bot.")
    #     elif ctx.guild.me.top_role.position == member.top_role.position:
    #         return await ctx.send(f"Can't untimeout {member} because the member has similar role hierarchy as the bot.")

    #     await member.timeout(duration=None, reason=f"{reason} {ctx.author} (ID: {ctx.author.id})")
    #     await ctx.send(f"Untimed out {member}.")

    @commands.group(name="lock", description="Lock the channel it's used in to prevent everyone from speaking", aliases=["lockdown"])
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def lock(self, ctx, channel: Optional[discord.TextChannel]):
        if ctx.invoked_subcommand:
            return

        channel = channel or ctx.channel
        if ctx.guild.default_role not in channel.overwrites:
            # This is the same as the elif except it handles agaisnt empty overwrites dicts
            overwrites = {
                ctx.guild.default_role: discord.PermissionOverwrite(send_messages=False),
                self.client.user: discord.PermissionOverwrite(
                    send_messages=True)
            }
            await channel.edit(overwrites=overwrites, reason=f"Channel locked by {ctx.author}")
            await ctx.send(f":lock: Locked!! {channel.mention}")
        elif (
            channel.overwrites[ctx.guild.default_role].send_messages == True
            or channel.overwrites[ctx.guild.default_role].send_messages == None
        ):
            overwrites = channel.overwrites[ctx.guild.default_role]
            overwrites.send_messages = False
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrites, reason=f"Channel locked by {ctx.author}")
            await ctx.send(f":lock: Locked!! {channel.mention}")

        elif channel.overwrites[ctx.guild.default_role].send_messages == False:
            await ctx.send("This channel is already locked!")

    @commands.group(name="unlock", description="Unlock the channel it's used to allow everyone to speak.", aliases=["unlockdown"])
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx, channel: Optional[discord.TextChannel]):
        if ctx.invoked_subcommand:
            return

        channel = channel or ctx.channel
        if ctx.guild.default_role not in channel.overwrites:
            await ctx.send("This channel is not locked!")
        elif (
            channel.overwrites[ctx.guild.default_role].send_messages == True
            or channel.overwrites[ctx.guild.default_role].send_messages == None
        ):
            await ctx.send("This channel is not locked!")
        else:
            overwrites = channel.overwrites[ctx.guild.default_role]
            overwrites.send_messages = None
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrites, reason=f"Channel Unlocked by {ctx.author}")
            await ctx.send(f":unlock: Unlocked!! {channel.mention}")

    @lock.command(name="server", description="Locks the whole server preventing everyone from speaking.")
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def lock_server(self, ctx):
        role = ctx.guild.default_role
        permissions = discord.Permissions()
        permissions.update(
            send_messages=False, read_messages=True, connect=True, speak=True,
            read_message_history=True, use_external_emojis=True, add_reactions=False
        )
        await role.edit(reason=f"Server Lockdown By {ctx.author}", permissions=permissions)
        try:
            await ctx.send(f":lock: Server Locked!!")
        except:
            pass

    @unlock.command(name="server", description="Reverts send messages for everyone back to normal")
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def unlock_server(self, ctx):
        role = ctx.guild.default_role
        permissions = discord.Permissions()
        permissions.update(
            send_messages=True, read_messages=True, connect=True, speak=True,
            read_message_history=True, use_external_emojis=True, add_reactions=True
        )
        await role.edit(reason=f"Server Unlocked by {ctx.author}", permissions=permissions)
        try:
            await ctx.send(f":unlock: Server Unlocked!!")
        except:
            pass


def setup(client):
    client.add_cog(Moderation(client))
