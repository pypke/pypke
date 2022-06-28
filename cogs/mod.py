import asyncio
from dateutil.relativedelta import relativedelta
from copy import deepcopy
from datetime import datetime, timedelta
from utils.time import TimeConverter, TimeHumanizer
from typing import Optional, Union

import discord
from discord.ext import commands, tasks
from discord.ext.commands import Greedy


class Moderation(commands.Cog):
    """Commands for server Moderation."""

    def __init__(self, client):
        self.client = client

    @commands.command(
        name="kick",
        description="Kick the member from this server.",
        cooldown_after_parsing=True,
    )
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    async def kick_command(self, ctx, member: discord.Member, *, reason="No Reason Provided"):
        if not reason:
            reason = f"No reason provided. ({ctx.author})"
        else:
            reason = reason + f" {ctx.author} (ID: {ctx.author.id})"

        if member in ctx.guild.members:
            if (
                ctx.author.top_role.position < member.top_role.position
                and member in ctx.guild.members
            ):
                return await ctx.send(
                    f"Can't kick {member} because you don't have higher role."
                )

            if (
                ctx.author.top_role.position == member.top_role.position
                and member in ctx.guild.members
            ):
                return await ctx.send(
                    f"Can't kick {member} because you both has similar role hierarchy."
                )

            if ctx.guild.me.top_role.position < member.top_role.position:
                return await ctx.send(
                    f"Can't kick {member} because the member has higher role than the bot."
                )

            if ctx.guild.me.top_role.position == member.top_role.position:
                return await ctx.send(
                    f"Can't kick {member} because the member has similar role hierarchy as the bot."
                )

        try:
            await member.kick(reason=reason)
        except Exception:
            await ctx.send(
                f"Unable To Kick {member}! Are You Sure That The Bot Has Higher Role Than {member} Or The Bot Isn't Missing Permissions!"
            )
            return

        await ctx.send(f"Kicked {member}!")

    @commands.command(
        name="ban",
        description="Bans a member whether or not the member is in the server.",
        aliases=["forceban", "hackban"],
        cooldown_after_parsing=True,
    )
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def ban_command(
        self,
        ctx,
        member: Union[discord.Member, discord.User],
        delete_days: Optional[int],
        *,
        reason=None,
    ):
        if not reason:
            reason = f"No reason provided. ({ctx.author})"
        else:
            reason = reason + f" {ctx.author} (ID: {ctx.author.id})"

        if not delete_days:
            delete_days = 0
        if 0 > delete_days > 7:
            return await ctx.send(
                "Argument `delete_days` should be more than 0 or less than 7"
            )

        if member in ctx.guild.members:
            if (
                ctx.author.top_role.position < member.top_role.position
                and member in ctx.guild.members
            ):
                return await ctx.send(
                    f"Can't ban {member} because you don't have higher role."
                )

            if (
                ctx.author.top_role.position == member.top_role.position
                and member in ctx.guild.members
            ):
                return await ctx.send(
                    f"Can't ban {member} because you both has similar role hierarchy."
                )

            if ctx.guild.me.top_role.position < member.top_role.position:
                return await ctx.send(
                    f"Can't ban {member} because the member has higher role than the bot."
                )

            if ctx.guild.me.top_role.position == member.top_role.position:
                return await ctx.send(
                    f"Can't ban {member} because the member has similar role hierarchy as the bot."
                )

            await member.ban(delete_message_days=delete_days, reason=reason)
        else:
            try:
                await ctx.guild.ban(
                    user=member, delete_message_days=delete_days, reason=reason
                )
            except discord.HTTPException:
                await ctx.send(f"Unable to ban {member}")
                return

        await ctx.send(f"Banned {member}.")

    @commands.command(
        name="unban",
        description="Unban banned user from this server.",
        cooldown_after_parsing=True,
    )
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

    @commands.command(
        name="massban",
        description="Bans any number of members whether or not they're in the server.",
        cooldown_after_parsing=True,
    )
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def massban_command(
        self,
        ctx,
        delete_days: Optional[int],
        members: Greedy[Union[discord.Member, discord.User]],
    ):

        if len(members) <= 0:
            return await ctx.send("You need to specify members to ban.")
        delete_days = delete_days or 0
        reason = f"Massban by {ctx.author} (ID: {ctx.author.id})"

        if 0 > delete_days > 7:
            return await ctx.send(
                "Argument `delete_days` should be more than 0 or less than 7"
            )

        for member in members:

            if member in ctx.guild.members:
                if ctx.author.top_role.position < member.top_role.position:
                    return await ctx.send(
                        f"Can't ban {member}. (You need to be higher in the role hierarchy.)"
                    )

                if ctx.author.top_role.position == member.top_role.position:
                    return await ctx.send(
                        f"Can't ban {member} because you both has similar role hierarchy."
                    )

                if ctx.guild.me.top_role.position < member.top_role.position:
                    return await ctx.send(
                        f"Can't ban {member} because the member has higher role than the bot."
                    )

                if ctx.guild.me.top_role.position == member.top_role.position:
                    return await ctx.send(
                        f"Can't ban {member} because the member has similar role hierarchy as the bot."
                    )

                await member.ban(delete_message_days=delete_days, reason=reason)
                await ctx.send(f"Banned {member}.")

            else:
                try:
                    await ctx.guild.ban(
                        user=member, delete_message_days=delete_days, reason=reason
                    )
                    await ctx.send(f"Banned {member}.")

                except discord.HTTPException:
                    await ctx.send(f"Unable to ban {member}.")

    @commands.command(
        name="softban",
        description="Softban a member to clear all his/her messages. Bans a user then instantly unbans them.",
        cooldown_after_parsing=True,
    )
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    async def softban_command(
        self,
        ctx,
        member: Union[discord.Member, discord.User],
        delete_days: Optional[int] = 2,
        *,
        reason: Optional[str],
    ):
        if not reason:
            reason = f"No reason provided. ({ctx.author})"
        else:
            reason = reason + f" (Soft-Banned by {ctx.author})"

        if 0 > delete_days > 7:
            return await ctx.send(
                "Argument `delete_days` should be more than 0 or less than 7"
            )

        if member in ctx.guild.members:
            if (
                ctx.author.top_role.position < member.top_role.position
                and member in ctx.guild.members
            ):
                return await ctx.send(
                    f"Can't ban {member} because you don't have higher role."
                )

            if (
                ctx.author.top_role.position == member.top_role.position
                and member in ctx.guild.members
            ):
                return await ctx.send(
                    f"Can't ban {member} because you both has similar role hierarchy."
                )

            if ctx.guild.me.top_role.position < member.top_role.position:
                return await ctx.send(
                    f"Can't ban {member} because the member has higher role than the bot."
                )

            if ctx.guild.me.top_role.position == member.top_role.position:
                return await ctx.send(
                    f"Can't ban {member} because the member has similar role hierarchy as the bot."
                )

            await member.ban(delete_message_days=delete_days, reason=reason)
        else:
            try:
                await ctx.guild.ban(
                    user=member, delete_message_days=delete_days, reason=reason
                )
            except discord.HTTPException:
                await ctx.send(f"Unable to ban {member.id}")
                return

        await ctx.guild.unban(member, reason=reason)
        await ctx.send(f"Soft-Banned {member}.")

    @commands.command(
        name="timeout",
        description="Timeouts the user. Better than mute.",
        aliases=["mute"],
        cooldown_after_parsing=True,
    )
    @commands.guild_only()
    @commands.has_permissions(moderate_members=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def timeout(self, ctx, member: discord.Member, *, duration: TimeConverter):
        if duration > 2419200:
            return await ctx.send("Time cannot be greater than 28 days now, This command uses discord's timeout feature.")

        duration_ = duration
        duration = timedelta(seconds=duration)

        if (
            ctx.author.top_role.position < member.top_role.position
            and member in ctx.guild.members
        ):
            return await ctx.send(
                f"Can't timeout {member} because you don't have higher role."
            )
        elif (
            ctx.author.top_role.position == member.top_role.position
            and member in ctx.guild.members
        ):
            return await ctx.send(
                f"Can't timeout {member} because you both has similar role hierarchy."
            )
        elif ctx.guild.me.top_role.position < member.top_role.position:
            return await ctx.send(
                f"Can't timeout {member} because the member has higher role than the bot."
            )
        elif ctx.guild.me.top_role.position == member.top_role.position:
            return await ctx.send(
                f"Can't timeout {member} because the member has similar role hierarchy as the bot."
            )

        await member.timeout_for(
            duration=duration, reason=f"Timeout by {ctx.author} (ID: {ctx.author.id})"
        )
        await ctx.send(f"Timed out `{member}` for {TimeHumanizer(duration_)}.")

    @commands.command(
        name="untimeout",
        description="Remove timeout from the user.",
        aliases=["unmute"],
        cooldown_after_parsing=True,
    )
    @commands.guild_only()
    @commands.has_permissions(moderate_members=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def untimeout(self, ctx, member: discord.Member, *, reason: Optional[str]):
        if (
            ctx.author.top_role.position < member.top_role.position
            and member in ctx.guild.members
        ):
            return await ctx.send(
                f"Can't untimeout {member} because you don't have higher role."
            )
        elif (
            ctx.author.top_role.position == member.top_role.position
            and member in ctx.guild.members
        ):
            return await ctx.send(
                f"Can't untimeout {member} because you both has similar role hierarchy."
            )
        elif ctx.guild.me.top_role.position < member.top_role.position:
            return await ctx.send(
                f"Can't untimeout {member} because the member has higher role than the bot."
            )
        elif ctx.guild.me.top_role.position == member.top_role.position:
            return await ctx.send(
                f"Can't untimeout {member} because the member has similar role hierarchy as the bot."
            )

        await member.timeout(until=None, reason=f"{reason} {ctx.author} (ID: {ctx.author.id})")
        await ctx.send(f"Untimed out {member}.")

    @commands.group(
        name="lock",
        description="Lock the channel it's used in to prevent everyone from speaking",
        aliases=["lockdown"],
    )
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
                self.client.user: discord.PermissionOverwrite(send_messages=True),
            }
            await channel.edit(overwrites=overwrites, reason=f"Channel locked by {ctx.author}")
            await ctx.send(f":lock: Locked!! {channel.mention}")
        elif (
            channel.overwrites[ctx.guild.default_role].send_messages == True
            or channel.overwrites[ctx.guild.default_role].send_messages == None
        ):
            overwrites = channel.overwrites[ctx.guild.default_role]
            overwrites.send_messages = False
            await channel.set_permissions(
                ctx.guild.default_role,
                overwrite=overwrites,
                reason=f"Channel locked by {ctx.author}",
            )
            await ctx.send(f":lock: Locked!! {channel.mention}")

        elif channel.overwrites[ctx.guild.default_role].send_messages == False:
            await ctx.send("This channel is already locked!")

    @commands.group(
        name="unlock",
        description="Unlock the channel it's used to allow everyone to speak.",
        aliases=["unlockdown"],
    )
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
            await channel.set_permissions(
                ctx.guild.default_role,
                overwrite=overwrites,
                reason=f"Channel Unlocked by {ctx.author}",
            )
            await ctx.send(f":unlock: Unlocked!! {channel.mention}")

    @lock.command(
        name="server",
        description="Locks the whole server preventing everyone from speaking.",
    )
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def lock_server(self, ctx):
        role = ctx.guild.default_role
        permissions = discord.Permissions()
        permissions.update(
            send_messages=False,
            read_messages=True,
            connect=True,
            speak=True,
            read_message_history=True,
            use_external_emojis=True,
            add_reactions=False,
        )
        await role.edit(reason=f"Server Lockdown By {ctx.author}", permissions=permissions)
        try:
            await ctx.send(f":lock: Server Locked!!")
        except:
            pass

    @unlock.command(
        name="server", description="Reverts send messages for everyone back to normal"
    )
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    async def unlock_server(self, ctx):
        role = ctx.guild.default_role
        permissions = discord.Permissions()
        permissions.update(
            send_messages=True,
            read_messages=True,
            connect=True,
            speak=True,
            read_message_history=True,
            use_external_emojis=True,
            add_reactions=True,
        )
        await role.edit(reason=f"Server Unlocked by {ctx.author}", permissions=permissions)
        try:
            await ctx.send(f":unlock: Server Unlocked!!")
        except:
            pass


def setup(client):
    client.add_cog(Moderation(client))
