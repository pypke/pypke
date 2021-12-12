from utils import TimeConverter

import asyncio
import humanize
import re
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import Optional

import discord
from discord.ext import commands, tasks
from dislash import ActionRow, Button, ButtonStyle, user_command


class Utility(commands.Cog):
    """Commands to help you with various tasks."""

    def __init__(self, client):
        self.client = client
        self.remind_loop.start()

    def cog_unload(self):
        self.remind_loop.cancel()

    @tasks.loop(minutes=1)
    async def remind_loop(self):
        currentTime = datetime.now()
        reminds = await self.client.remind.get_all()
        for remind in reminds:
            if remind['remindIn'] is None:
                continue

            endTime = remind['startedAt'] + \
                relativedelta(seconds=remind['remindIn'])
            if currentTime >= endTime:
                try:
                    guild = self.client.get_guild(remind['guildId'])
                    channel = guild.get_channel(remind['channelId'])
                    msg = await channel.fetch_message(remind['msgId'])
                except discord.errors.NotFound:
                    print("Deleted NotFound reminder!")
                    return await self.client.remind.delete(remind['_id'])

                task = remind['task']
                try:
                    await msg.reply(f"{msg.author.mention}! Reminder for `{task.lower()}`.")
                except discord.HTTPException:
                    pass

                await self.client.remind.delete(msg.author.id)

    @remind_loop.before_loop
    async def before_remind_loop(self):
        await self.client.wait_until_ready()

    @commands.group(name="purge", description="Clear/purge amount of message in channel.\nIgnores pinned messages.", aliases=['clear'], invoke_without_command=True)
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(1, commands.BucketType.channel)
    async def purge_command(self, ctx, member: Optional[discord.User], amount: int = 1):
        def member_check(message):
            return not member and not message.pinned or message.author == member and not message.pinned

        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=amount, after=datetime.utcnow() - timedelta(days=14), check=member_check)

        if len(deleted) < 1:
            return await ctx.send("No message was deleted! Make sure the messages aren't two weeks old.")
        elif 0 < amount <= 1000:
            embed = discord.Embed(
                title=f"{ctx.author.name} purged: {ctx.channel.name}",
                description=f"{len(deleted)} messages were cleared!",
                color=self.client.color
            )
            await ctx.send(embed=embed, delete_after=3)
        else:
            return await ctx.send("Amount should be less 1000 and more than 0.")

    @purge_command.command(name="human", description="Clear amount of messages by a human\nIgnores pinned messages.", aliases=["humans"])
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(1, commands.BucketType.channel)
    async def purge_human(self, ctx, amount: int = 1):
        def human_check(message):
            return not message.author.bot and not message.pinned

        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=amount, after=datetime.utcnow() - timedelta(days=14), check=human_check)

        if len(deleted) < 1:
            return await ctx.send("No message was deleted! Make sure the messages aren't two weeks old.")
        elif 0 < amount <= 1000:
            embed = discord.Embed(
                title=f"{ctx.author.name} purged: {ctx.channel.name}",
                description=f"{len(deleted)} messages were cleared!",
                color=self.client.color
            )
            await ctx.send(embed=embed, delete_after=3)
        else:
            return await ctx.send("Amount should be less 1000 and more than 0.")

    @purge_command.command(name="bot", description="Removes a bot user's messages.\nIgnores pinned messages.", aliases=["bots"])
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(1, commands.BucketType.channel)
    async def purge_bot(self, ctx, amount: int = 1):
        def bot_check(message):
            return message.author.bot and not message.pinned

        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=amount, after=datetime.utcnow() - timedelta(days=14), check=bot_check)

        if len(deleted) < 1:
            return await ctx.send("No message was deleted! Make sure the messages aren't two weeks old.")
        elif 0 < amount <= 1000:
            embed = discord.Embed(
                title=f"{ctx.author.name} purged: {ctx.channel.name}",
                description=f"{len(deleted)} messages were cleared!",
                color=self.client.color
            )
            await ctx.send(embed=embed, delete_after=3)
        else:
            return await ctx.send("Amount should be less 1000 and more than 0.")

    @purge_command.command(name="embed", description="Removes messages with embed.\nIgnores pinned messages.", aliases=["embeds"])
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(1, commands.BucketType.channel)
    async def purge_embed(self, ctx, amount: int = 1):
        def embed_check(message):
            return len(message.embeds) > 0 and not message.pinned

        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=amount, after=datetime.utcnow() - timedelta(days=14), check=embed_check)

        if len(deleted) < 1:
            return await ctx.send("No message was deleted! Make sure the messages aren't two weeks old.")
        elif 0 < amount <= 1000:
            embed = discord.Embed(
                title=f"{ctx.author.name} purged: {ctx.channel.name}",
                description=f"{len(deleted)} messages were cleared!",
                color=self.client.color
            )
            await ctx.send(embed=embed, delete_after=3)
        else:
            return await ctx.send("Amount should be less 1000 and more than 0.")

    @purge_command.command(name="attachments", description="Removes messages with attachments.\nIgnores pinned messages.", aliases=["files", "file"])
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(1, commands.BucketType.channel)
    async def purge_files(self, ctx, amount: int = 1):
        def embed_check(message):
            return len(message.attachments) > 0 and not message.pinned

        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=amount, after=datetime.utcnow() - timedelta(days=14), check=embed_check)

        if len(deleted) < 1:
            return await ctx.send("No message was deleted! Make sure the messages aren't two weeks old.")
        elif 0 < amount <= 1000:
            embed = discord.Embed(
                title=f"{ctx.author.name} purged: {ctx.channel.name}",
                description=f"{len(deleted)} messages were cleared!",
                color=self.client.color
            )
            await ctx.send(embed=embed, delete_after=3)
        else:
            return await ctx.send("Amount should be less 1000 and more than 0.")

    @purge_command.command(name="mention", description="Removes messages with mentions in it.\nIgnores pinned messages.", aliases=["mentions"])
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(1, commands.BucketType.channel)
    async def purge_mention(self, ctx, amount: int = 1):
        def mention_check(message):
            return len(message.mentions) or len(message.role_mentions) and not message.pinned

        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=amount, after=datetime.utcnow() - timedelta(days=14), check=mention_check)

        if len(deleted) < 1:
            return await ctx.send("No message was deleted! Make sure the messages aren't two weeks old.")
        elif 0 < amount <= 1000:
            embed = discord.Embed(
                title=f"{ctx.author.name} purged: {ctx.channel.name}",
                description=f"{len(deleted)} messages were cleared!",
                color=self.client.color
            )
            await ctx.send(embed=embed, delete_after=3)
        else:
            return await ctx.send("Amount should be less 1000 and more than 0.")

    @purge_command.command(name="contains", description="Removes messages with substr in it.\nIgnores pinned messages.", aliases=["has"])
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(1, commands.BucketType.channel)
    async def purge_contain(self, ctx, substr: str, amount: int = 1):
        def contain_check(message):
            return substr in message.content and not message.pinned

        if len(substr) < 3:
            await ctx.send("The substring length must be at least 3 characters.")

        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=amount, after=datetime.utcnow() - timedelta(days=14), check=contain_check)

        if len(deleted) < 1:
            return await ctx.send("No message was deleted! Make sure the messages aren't two weeks old.")
        elif 0 < amount <= 1000:
            embed = discord.Embed(
                title=f"{ctx.author.name} purged: {ctx.channel.name}",
                description=f"{len(deleted)} messages were cleared!",
                color=self.client.color
            )
            await ctx.send(embed=embed, delete_after=3)
        else:
            return await ctx.send("Amount should be less 1000 and more than 0.")

    @purge_command.command(name="reaction", description="Removes reactions in from a message.\nIgnores pinned messages.", aliases=["reactions"])
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(1, commands.BucketType.channel)
    async def purge_reaction(self, ctx, amount: int = 1):
        def reaction_check(message):
            return not message.pinned

        await ctx.message.delete()
        total_reactions = 0
        async for message in ctx.history(limit=amount, before=ctx.message):
            if len(message.reactions):
                total_reactions += sum(r.count for r in message.reactions)
                await message.clear_reactions()

        if total_reactions < 1:
            return await ctx.send("No reaction was clear! Make sure the messages aren't two weeks old.")
        elif 0 < amount <= 1000:
            embed = discord.Embed(
                title=f"{ctx.author.name} purged: {ctx.channel.name}",
                description=f"{total_reactions} reactions were cleared!",
                color=self.client.color
            )
            await ctx.send(embed=embed, delete_after=3)
        else:
            return await ctx.send("Amount should be less 1000 and more than 0.")

    @purge_command.command(name="emoji", description="Removes messages with emojis in it.\nIgnores pinned messages.", aliases=["emojis"])
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(1, commands.BucketType.channel)
    async def purge_emoji(self, ctx, amount: int = 1):
        custom_emoji = re.compile(
            r"<a?:(.*?):(\d{17,21})>|[\u263a-\U0001f645]")

        def emoji_check(message):
            return custom_emoji.search(message.content) and not message.pinned

        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=amount, after=datetime.utcnow() - timedelta(days=14), check=emoji_check)

        if len(deleted) < 1:
            return await ctx.send("No message was deleted! Make sure the messages aren't two weeks old.")
        elif 0 < amount <= 1000:
            embed = discord.Embed(
                title=f"{ctx.author.name} purged: {ctx.channel.name}",
                description=f"{len(deleted)} messages were cleared!",
                color=self.client.color
            )
            await ctx.send(embed=embed, delete_after=3)
        else:
            return await ctx.send("Amount should be less 1000 and more than 0.")

    @purge_command.command(name="after", description="Removes messages after the specified message.\nIgnores pinned messages.", hidden=True)
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(1, commands.BucketType.channel)
    async def purge_after(self, ctx, message_id: int, amount: int = 1):
        def after_check(message):
            return not message.pinned

        msg = ctx.channel.fetch_message(message_id)
        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=amount, after=datetime.utcnow() - timedelta(days=14), check=after_check)

        if len(deleted) < 1:
            return await ctx.send("No message was deleted! Make sure the messages aren't two weeks old.")
        elif 0 < amount <= 1000:
            embed = discord.Embed(
                title=f"{ctx.author.name} purged: {ctx.channel.name}",
                description=f"{len(deleted)} messages were cleared!",
                color=self.client.color
            )
            await ctx.send(embed=embed, delete_after=3)
        else:
            return await ctx.send("Amount should be less 1000 and more than 0.")

    @commands.command(name="nuke", description="Purges the whole channel by cloning and deleting the original.", aliases=["clone"])
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def nuke_command(self, ctx):
        confirm = ActionRow(
            Button(
                style=ButtonStyle.grey,
                emoji="<:agreed:918425367251935242>",
                label="Confirm",
                custom_id="yes"
            ),
            Button(
                style=ButtonStyle.grey,
                emoji="<:disagreed:918425439960186930>",
                label="Cancel",
                custom_id="no"
            )
        )
        embed = discord.Embed(
            color=self.client.color,
            description="Are you sure you want to nuke/clone this channel?"
        )
        msg = await ctx.send(embed=embed, components=[confirm])

        while True:
            # Try and except blocks to catch timeout and break
            def check(inter):
                return inter.message.id == msg.id and inter.author.id == ctx.author.id

            try:
                inter = await ctx.wait_for_button_click(check=check, timeout=20.0)

                if (inter.clicked_button.custom_id) == "yes":
                    channel = ctx.channel
                    position = channel.position
                    new_channel = await channel.clone(reason=f"Channel Nuked By {ctx.author} (ID: {ctx.author.id})")
                    await channel.delete(reason=f"Channel Nuked By {ctx.author} (ID: {ctx.author.id})")
                    await new_channel.edit(position=position)
                    await new_channel.send(f"{ctx.author.mention} Successfully nuked the channel!")
                    break
                else:
                    await msg.delete()
                    await ctx.send("Ok, withdrawing the nukes..  Canceling the attack")
                    break

            except asyncio.TimeoutError:
                await msg.delete()
                await ctx.send("Ok, withdrawing the nukes..  Canceling the attack")
                break
            except:
                break

    @commands.command(
        name="slowmode",
        description="Change the channels slowmode time.\nExample: `?slowmo 1h`\nPossible values:\n`0s, 5s, 10s, 15s, 30s, 1m, 2m, 5m, 10m, 15m, 30m, 1h, 2h, 6h`",
        aliases=["slowmo"]
    )
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def slowmode_command(self, ctx, channel: Optional[discord.TextChannel], slowmode: TimeConverter):
        channel = channel or ctx.channel

        if slowmode > 21600:
            slowmode = 21600

        await channel.edit(slowmode_delay=slowmode)
        await ctx.send(f"Set channel slowmode to {channel.slowmode_delay} secs.")

    @commands.command(name="mail", description="Mail/Dm a user through the bot because you're lazy ;-; to manually do it.", aliases=['dm'])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def mail_command(self, ctx, user: discord.User, *, msg):
        try:
            mail = discord.Embed(
                title=f"Meow Mail Service",
                description=f"```txt\n{msg}\n```",
                color=discord.Color.blurple(),

            )
            mail.set_footer(text=f"Mail From {ctx.author.name}")
            await user.send(embed=mail)
            await ctx.send(f"Mailed {user} successfully!!")
        except:
            await ctx.message.delete()
            await ctx.send(f"{user} has their DMs closed!!", delete_after=3)

    @commands.group(
        name="remind",
        description="Reminds you do to something after specified time.",
        aliases=["reminder", "remindme"],
        invoke_without_command=True
    )
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def remind_command(self, ctx, time: TimeConverter, *, task: str):
        try:
            data = await self.client.remind.get(ctx.author.id)
        except Exception:
            data = None

        if data:
            remindin = humanize.precisedelta(
                timedelta(seconds=data['time'], minimum_unit="minutes"))
            task = data['task']
            task = discord.utils.escape_mentions(task)
            return await ctx.reply(f"You will be reminded in {remindin} for **{task.lower()}**.")

        data = {
            "_id": ctx.author.id,
            "msgId": ctx.message.id,
            "guildId": ctx.guild.id,
            "channelId": ctx.channel.id,
            "startedAt": datetime.now(),
            "remindIn": time,
            "task": task
        }
        task = discord.utils.escape_mentions(task)
        await ctx.reply(f"Ok, I will remind you <t:{round(datetime.timestamp(datetime.now()) + int(time))}:R> to **{task.lower()}**.")
        await self.client.remind.upsert(data)

        if time <= 300:
            await asyncio.sleep(time)
            try:
                task = discord.utils.escape_mentions(task)
                await ctx.message.reply(f"{ctx.author.mention} Reminder for **{task.lower()}**.")
            except discord.HTTPException:
                pass

            await self.client.remind.delete(ctx.author.id)

    @remind_command.command(
        name="cancel",
        description="Cancel the reminder using this command.",
        aliases=["delete"]
    )
    async def remind_cancel(self, ctx):
        try:
            data = await self.client.remind.find(ctx.author.id)
        except Exception:
            pass

        if not data:
            return await ctx.send("You've no reminder ongoing.")

        await self.client.remind.delete(ctx.author.id)
        await ctx.reply("Cancelled reminder!")

    @commands.command(name="avatar", description="Gives the users avatar.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def avatar_command(self, ctx, member: Optional[discord.User]):
        member = member or ctx.author
        embed = discord.Embed(
            title=f"{member}'s Avatar!",
            colour=self.client.colors["og_blurple"]
        )
        embed.set_image(url=member.avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="whois", description="Shows some interesting information about a member.", aliases=["userinfo", "ui"])
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def whois_command(self, ctx, member: Optional[discord.Member]):

        if member is None:
            member = ctx.author
            roles = [role for role in ctx.author.roles]
            roles.pop(roles.index(ctx.guild.default_role))
            roles = sorted(roles, reverse=True)

        else:
            roles = [role for role in member.roles]
            roles.pop(roles.index(ctx.guild.default_role))
            roles = sorted(roles, reverse=True)

        """
        member.created_at.strftime("%a, %d, %B, %Y, %I, %M, %p UTC")
        member.joined_at.strftime("%a, %d, %B, %Y, %I, %M, %p UTC")
        """
        created_time = member.created_at
        created_time = round(created_time.timestamp())
        joined_time = member.joined_at
        joined_time = round(joined_time.timestamp())

        embed = discord.Embed(colour=member.color,
                              timestamp=ctx.message.created_at)

        embed.set_footer(
            text=f"Requested by: {ctx.author}", icon_url=ctx.author.avatar.url)
        embed.set_author(
            name=member, icon_url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.set_thumbnail(
            url=member.avatar.url if member.avatar else member.default_avatar.url)

        embed.add_field(
            name="__Information__",
            value=f"**Name:** {member}\n**ID:** {member.id}\n**Nick:** {member.display_name}\n**Status:** {str(member.status).title()}\n**Created At:** <t:{created_time}:f>\n**Joined At:** <t:{joined_time}:f>\n**Bot?** {member.bot}",
            inline=False
        )
        embed.add_field(
            name="__Role Info__",
            value=f"**Highest Role:** {member.top_role.mention}\n**Roles:** {' **|** '.join([role.mention for role in roles])}\n**Color:** `{member.top_role.color}`",
            inline=False
        )

        await ctx.send(embed=embed)

    @user_command(name="User Info", guild_ids=["850732056790827020"])
    async def whois_message_command(self, ctx):
        member = ctx.target

        roles = [role for role in member.roles]
        roles.pop(roles.index(ctx.guild.default_role))
        roles = sorted(roles, reverse=True)

        """
        member.created_at.strftime("%a, %d, %B, %Y, %I, %M, %p UTC")
        member.joined_at.strftime("%a, %d, %B, %Y, %I, %M, %p UTC")
        """
        created_time = member.created_at
        created_time = round(created_time.timestamp())
        joined_time = member.joined_at
        joined_time = round(joined_time.timestamp())

        embed = discord.Embed(colour=member.top_role.color,
                              timestamp=ctx.message.created_at)

        embed.set_footer(
            text=f"Requested by: {ctx.author}", icon_url=ctx.author.avatar.url)
        embed.set_author(
            name=member, icon_url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.set_thumbnail(
            url=member.avatar.url if member.avatar else member.default_avatar.url)

        embed.add_field(
            name="__Information__",
            remind=f"**Name:** {member}\n**ID:** {member.id}\n**Nick:** {member.display_name}\n**Status:** {str(member.status).title()}\n**Created At:** <t:{created_time}:f>\n**Joined At:** <t:{joined_time}:f>\n**Bot?** {member.bot}",
            inline=False
        )
        embed.add_field(
            name="__Role Info__",
            remind=f"**Highest Role:** {member.top_role.mention}\n**Roles:** {' **|** '.join([role.mention for role in roles])}\n**Color:** `{member.top_role.color}`",
            inline=False
        )
        await ctx.respond(embed=embed)

    @commands.group(
        name="modlog",
        description="Modlog group command. Does nothing without subcommands.",
        invoke_without_subcommand=False,
        hidden=True
    )
    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def modlog_command(self, ctx):
        pass

    @modlog_command.command(
        name="moderation",
        description="Set modlog channel for moderation actions.",
        aliases=["mod"]
    )
    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.guild)
    async def modlog_mod(self, ctx, channel: Optional[discord.TextChannel]):
        if channel:
            data = await self.client.config.find(ctx.guild.id)
            new_data = {
                "_id": ctx.guild.id,
                "prefix": data["prefix"] or self.client.prefix,
                "modlog_mod": channel.id,
                "modlog_member": data["modlog_member"] if data["modlog_member"] else None,
                "modlog_message": data["modlog_message"] if data["modlog_member"] else None
            }
            await self.client.config.upsert(new_data)
            await ctx.send(f"{channel.mention} is now set as Modlog channel for moderation actions.")
        else:
            data = await self.client.config.find(ctx.guild.id)
            new_data = {
                "_id": ctx.guild.id,
                "prefix": data["prefix"] or self.client.prefix,
                "modlog_mod": None,
                "modlog_member": data["modlog_member"] if data["modlog_member"] else None,
                "modlog_message": data["modlog_message"] if data["modlog_member"] else None
            }
            await self.client.config.upsert(new_data)
            await ctx.send(f"{channel.mention} is now removed as a Modlog channel.")

    @commands.command(
        name='afk',
        description='Set Your Afk To Let People Know What Are You Doing.'
    )
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def afk(self, ctx, *, text: str = None):
        if text == None:
            await self.client.afks.upsert({"_id": ctx.author.id, "text": None})
        else:
            await self.client.afks.upsert({"_id": ctx.author.id, "text": text})

        await ctx.send("Your Afk Status Has Been Set.")

    @commands.command(
        name='afkremove',
        description='Stop/Remove Your Afk',
        aliases=['afkstop', 'afkr']
    )
    @commands.guild_only()
    async def afkremove(self, ctx):
        data = await self.client.afks.get_by_id(ctx.author.id)
        if not data:
            await ctx.send("You Haven't Set Your Afk Status Yet.")
        else:
            await self.client.afks.delete(ctx.author.id)
            await ctx.send("Your Afk Status Has Been Removed.")


def setup(client):
    client.add_cog(Utility(client))
