import asyncio
import re
from datetime import datetime, timedelta
from typing import Optional

import discord
from dateutil.relativedelta import relativedelta
from discord.ext import commands, tasks
from dislash import ActionRow, Button, ButtonStyle, user_command
from utils import TimeConverter, TimeHumanizer


class PurgeMessages:
    def __init__(self, bot):
        self.bot = bot

    async def messages(self, ctx, amount: int, check_func):
        if not 0 < amount <= 1000:
            return await ctx.send("Amount should be less 1000 and more than 0.")

        deleted = await ctx.channel.purge(
            limit=amount,
            after=datetime.utcnow() - timedelta(days=14),
            check=check_func,
        )

        if len(deleted) < 1:
            return await ctx.send(
                "No message was deleted! Make sure the messages aren't two weeks old."
            )
        elif 0 < amount <= 1000:
            embed = discord.Embed(
                title=f"{ctx.author.name} purged: {ctx.channel.name}",
                description=f"{len(deleted)} messages were cleared!",
                color=self.bot.color,
            )
            await ctx.send(embed=embed, delete_after=3)
            await ctx.message.delete()
        else:
            return await ctx.send("Amount should be less 1000 and more than 0.")

    async def reactions(self, ctx, amount: int = 1, emoji=None):
        if not 0 < amount <= 1000:
            return await ctx.send("Amount should be less 1000 and more than 0.")

        if emoji:
            custom_emoji = re.compile(r"<a?:(.*?):(\d{17,21})>")
            if not custom_emoji.search(emoji):
                return await ctx.send(
                    f"Non valid emoji was provided for clearing. {emoji}"
                )

        total_reactions = await self._reaction_count(ctx, amount, emoji)
        if total_reactions < 1:
            return await ctx.send(
                "No reaction was cleared! Make sure the messages aren't two weeks old."
            )
        elif 0 < amount <= 1000:
            embed = discord.Embed(
                title=f"{ctx.author.name} purged: {ctx.channel.name}",
                description=f"{total_reactions} reactions were cleared!",
                color=self.client.color,
            )
            await ctx.send(embed=embed, delete_after=3)
            await ctx.message.delete()

    async def _reaction_count(self, ctx, amount, emoji=None):
        total_reactions = 0
        async for message in ctx.history(limit=amount, before=ctx.message):
            if emoji:
                for reaction in message.reactions:
                    if reaction.emoji == emoji:
                        total_reactions += reaction.count
                        await reaction.remove(ctx.bot.user)
            else:
                if len(message.reactions):
                    total_reactions += sum(r.count for r in message.reactions)
                    await message.clear_reactions()


class Utility(commands.Cog):
    """Commands to help you with various tasks."""

    def __init__(self, bot):
        self.bot = bot
        self.remind_loop.start()
        self.purge = PurgeMessages(bot)

    def cog_unload(self):
        self.remind_loop.cancel()

    @tasks.loop(minutes=1)
    async def remind_loop(self):
        currentTime = datetime.now()
        reminds = await self.bot.remind.get_all()
        for remind in reminds:
            if remind["remindIn"] is None:
                continue

            endTime = remind["startedAt"] + relativedelta(seconds=remind["remindIn"])
            if currentTime >= endTime:
                try:
                    guild = self.bot.get_guild(remind["guildId"])
                    channel = guild.get_channel(remind["channelId"])
                    msg = await channel.fetch_message(remind["msgId"])
                except discord.errors.NotFound:
                    print("Deleted NotFound reminder!")
                    return await self.bot.remind.delete(remind["_id"])

                task = remind["task"]
                try:
                    await msg.reply(
                        f"{msg.author.mention}! Reminder for `{task.lower()}`."
                    )
                except discord.HTTPException:
                    pass

                await self.bot.remind.delete(msg.author.id)

    @remind_loop.before_loop
    async def before_remind_loop(self):
        await self.bot.wait_until_ready()

    @commands.group(
        name="purge",
        description="Clear/purge amount of message in channel.\nIgnores pinned messages.",
        aliases=["clear"],
        invoke_without_command=True,
    )
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(1, commands.BucketType.channel)
    async def purge_command(self, ctx, member: Optional[discord.User], amount: int = 1):
        def member_check(message):
            return (
                not member
                and not message.pinned
                or message.author == member
                and not message.pinned
            )

        await self.purge.messages(ctx, amount, member_check)

    @purge_command.command(
        name="human",
        description="Clear amount of messages by a human",
        aliases=["humans"],
    )
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(1, commands.BucketType.channel)
    async def purge_human(self, ctx, amount: int = 1):
        def human_check(message):
            return not message.author.bot and not message.pinned

        await self.purge.messages(ctx, amount, human_check)

    @purge_command.command(
        name="bot",
        description="Removes a bot user's messages.",
        aliases=["bots"],
    )
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(1, commands.BucketType.channel)
    async def purge_bot(self, ctx, amount: int = 1):
        def bot_check(message):
            return message.author.bot and not message.pinned

        await self.purge.messages(ctx, amount, bot_check)

    @purge_command.command(
        name="embed",
        description="Removes messages with embed.",
        aliases=["embeds"],
    )
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(1, commands.BucketType.channel)
    async def purge_embed(self, ctx, amount: int = 1):
        def embed_check(message):
            return len(message.embeds) > 0 and not message.pinned

        await self.purge.messages(ctx, amount, embed_check)

    @purge_command.command(
        name="attachments",
        description="Removes messages with attachments.",
        aliases=["files", "file"],
    )
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(1, commands.BucketType.channel)
    async def purge_files(self, ctx, amount: int = 1):
        def atch_check(message):
            return len(message.attachments) > 0 and not message.pinned

        await self.purge.messages(ctx, amount, atch_check)

    @purge_command.command(
        name="mention",
        description="Removes messages with mentions in it.",
        aliases=["mentions"],
    )
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(1, commands.BucketType.channel)
    async def purge_mentions(self, ctx, amount: int = 1):
        def mention_check(message):
            return (
                len(message.mentions) or len(message.role_mentions)
            ) and not message.pinned

        await self.purge.messages(ctx, amount, mention_check)

    @purge_command.command(
        name="contains",
        description="Removes all messages containing a substring.\nThe substring must be at least 3 characters long.",
        aliases=["has"],
    )
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(1, commands.BucketType.channel)
    async def purge_contains(self, ctx, substr: str, amount: int = 1):
        if len(substr) < 3:
            return await ctx.send("The substring length must be at least 3 characters.")

        def contain_check(message):
            return substr in message.content and not message.pinned

        await self.purge.messages(ctx, amount, contain_check)

    @purge_command.command(
        name="reaction",
        description="Removes reactions in from a message.",
        aliases=["reactions"],
    )
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(1, commands.BucketType.channel)
    async def purge_reaction(self, ctx, amount: int = 1):
        await self.purge.reactions(ctx, amount)

    @purge_command.command(
        name="emoji",
        description="Removes messages with emojis in it.",
        aliases=["emojis"],
    )
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.max_concurrency(1, commands.BucketType.channel)
    async def purge_emoji(self, ctx, amount: int = 1):
        custom_emoji = re.compile(
            "(?:<a?:([a-zA-Z0-9_]{1,32}):(\d{17,21})>|:([a-zA-Z0-9_]{1,32}):)"
        )

        def emoji_check(message):
            return custom_emoji.search(message.content) and not message.pinned

        await self.purge.messages(ctx, amount, emoji_check)

    #   <------ purge after specified message id command is to be created here ------>

    @commands.command(
        name="nuke",
        description="Purges the whole channel by cloning and deleting the original.",
        aliases=["clone"],
    )
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
                custom_id="yes",
            ),
            Button(
                style=ButtonStyle.grey,
                emoji="<:disagreed:918425439960186930>",
                label="Cancel",
                custom_id="no",
            ),
        )
        embed = discord.Embed(
            color=self.bot.color,
            description="Are you sure you want to nuke/clone this channel?",
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
                    new_channel = await channel.clone(
                        reason=f"Channel Nuked By {ctx.author} (ID: {ctx.author.id})"
                    )
                    await channel.delete(
                        reason=f"Channel Nuked By {ctx.author} (ID: {ctx.author.id})"
                    )
                    await new_channel.edit(position=position)
                    await new_channel.send(
                        f"{ctx.author.mention} Successfully nuked the channel!"
                    )
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
        aliases=["slowmo"],
    )
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def slowmode_command(
        self, ctx, channel: Optional[discord.TextChannel], slowmode: TimeConverter
    ):
        channel = channel or ctx.channel

        if slowmode > 21600:
            slowmode = 21600

        await channel.edit(slowmode_delay=slowmode)
        await ctx.send(
            f"Set channel slowmode to {TimeHumanizer(channel.slowmode_delay)}."
        )

    @commands.command(
        name="mail",
        description="Mail/Dm a user through the bot because you're lazy ;-; to manually do it.",
        aliases=["dm"],
    )
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
            mail.set_footer(text=f"Mail from {ctx.author.name} | {ctx.guild.name}")
            await user.send(embed=mail)
            await ctx.send(f"Mailed {user} successfully!!")
        except:
            await ctx.message.delete()
            await ctx.send(f"{user} has their DMs closed!!", delete_after=3)

    @commands.group(
        name="remind",
        description="Reminds you do to something after specified time.",
        aliases=["reminder", "remindme"],
        invoke_without_command=True,
    )
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def remind_command(self, ctx, time: TimeConverter, *, task: str):
        try:
            data = await self.bot.remind.get(ctx.author.id)
        except Exception:
            data = None

        if data:
            remindin = TimeHumanizer(data["time"])
            task = data["task"]
            task = discord.utils.escape_mentions(task)
            return await ctx.reply(
                f"You will be reminded in {remindin} for **{task.lower()}**."
            )

        data = {
            "_id": ctx.author.id,
            "msgId": ctx.message.id,
            "guildId": ctx.guild.id,
            "channelId": ctx.channel.id,
            "startedAt": datetime.now(),
            "remindIn": time,
            "task": task,
        }
        task = discord.utils.escape_mentions(task)
        await ctx.reply(
            f"Ok, I will remind you <t:{round(datetime.timestamp(datetime.now()) + int(time))}:R> to **{task.lower()}**."
        )
        await self.bot.remind.upsert(data)

        if time <= 300:
            await asyncio.sleep(time)
            try:
                task = discord.utils.escape_mentions(task)
                await ctx.message.reply(
                    f"{ctx.author.mention} Reminder for **{task.lower()}**."
                )
            except discord.HTTPException:
                pass

            await self.bot.remind.delete(ctx.author.id)

    @remind_command.command(
        name="cancel",
        description="Cancel the reminder using this command.",
        aliases=["delete"],
    )
    async def remind_cancel(self, ctx):
        try:
            data = await self.bot.remind.find(ctx.author.id)
        except Exception:
            pass

        if not data:
            return await ctx.send("You've no reminder ongoing.")

        await self.bot.remind.delete(ctx.author.id)
        await ctx.reply("Cancelled reminder!")

    @commands.command(name="avatar", description="Gives the users avatar.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def avatar_command(self, ctx, member: Optional[discord.User]):
        member = member or ctx.author
        embed = discord.Embed(
            title=f"{member}'s Avatar!", colour=self.bot.colors["og_blurple"]
        )
        embed.set_image(url=member.avatar.url)
        await ctx.send(embed=embed)

    @commands.command(
        name="whois",
        description="Shows some interesting information about a member.",
        aliases=["userinfo", "ui"],
    )
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

        embed = discord.Embed(colour=member.color, timestamp=ctx.message.created_at)

        embed.set_footer(
            text=f"Requested by: {ctx.author}", icon_url=ctx.author.avatar.url
        )
        embed.set_author(
            name=member,
            icon_url=member.avatar.url if member.avatar else member.default_avatar.url,
        )
        embed.set_thumbnail(
            url=member.avatar.url if member.avatar else member.default_avatar.url
        )

        embed.add_field(
            name="__Information__",
            value=f"**Name:** {member}\n**ID:** {member.id}\n**Nick:** {member.display_name}\n**Status:** {str(member.status).title()}\n**Created At:** <t:{created_time}:f>\n**Joined At:** <t:{joined_time}:f>\n**Bot?** {member.bot}",
            inline=False,
        )
        embed.add_field(
            name="__Role Info__",
            value=f"**Highest Role:** {member.top_role.mention}\n**Roles:** {' **|** '.join([role.mention for role in roles])}\n**Color:** `{member.top_role.color}`",
            inline=False,
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

        embed = discord.Embed(
            colour=member.top_role.color, timestamp=ctx.message.created_at
        )

        embed.set_footer(
            text=f"Requested by: {ctx.author}", icon_url=ctx.author.avatar.url
        )
        embed.set_author(
            name=member,
            icon_url=member.avatar.url if member.avatar else member.default_avatar.url,
        )
        embed.set_thumbnail(
            url=member.avatar.url if member.avatar else member.default_avatar.url
        )

        embed.add_field(
            name="__Information__",
            remind=f"**Name:** {member}\n**ID:** {member.id}\n**Nick:** {member.display_name}\n**Status:** {str(member.status).title()}\n**Created At:** <t:{created_time}:f>\n**Joined At:** <t:{joined_time}:f>\n**Bot?** {member.bot}",
            inline=False,
        )
        embed.add_field(
            name="__Role Info__",
            remind=f"**Highest Role:** {member.top_role.mention}\n**Roles:** {' **|** '.join([role.mention for role in roles])}\n**Color:** `{member.top_role.color}`",
            inline=False,
        )
        await ctx.respond(embed=embed)

    @commands.group(name="afk", description="Shows this message.")
    @commands.guild_only()
    @commands.bot_has_permissions(manage_nicknames=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def afk(self, ctx):
        if ctx.invoked_subcommand:
            return

        await ctx.invoke(self.bot.get_command("help"), command_or_module="afk")

    @afk.command(
        name="set",
        description="Set an AFK status shown when you're mentioned, and display in nickname.",
    )
    @commands.guild_only()
    @commands.bot_has_permissions(manage_nicknames=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def afk_set(self, ctx, *, status: Optional[str]):
        if not status:
            await self.bot.afks.upsert(
                {"_id": ctx.author.id, "status": "AFK", "started_when": datetime.now()}
            )
        else:
            await self.bot.afks.upsert(
                {"_id": ctx.author.id, "status": status, "started_when": datetime.now()}
            )

        name = ctx.author.display_name
        try:
            await ctx.author.edit(nick=f"AFK | {name}")
        except discord.HTTPException:
            pass
        await ctx.send(
            f"{ctx.author.mention} Status set: {status if status else 'AFK'}"
        )

    @afk.command(
        name="ignore",
        description="Use it in a channel to not end AFK when talking in that channel.",
    )
    @commands.guild_only()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def afk_ignore(self, ctx, channel: Optional[discord.TextChannel]):
        channel = channel or ctx.channel
        self.bot.afk_allowed_channel[ctx.author.id] = [channel.id]
        await ctx.send(f"Added {channel.mention} to AFK ignored channels.")

    @afk.command(
        name="clear", description="Remove the AFK status of a member. (Moderators only)"
    )
    @commands.guild_only()
    @commands.bot_has_permissions(manage_nicknames=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def afk_clear(self, ctx, member: discord.Member):
        data = await self.bot.afks.find(member.id)
        if not data:
            return await ctx.send("Member doesn't have an AFK status.")

        await self.bot.afks.delete(member.id)
        await ctx.send(f"Removed AFK status for {member}.")

        try:
            self.bot.current_afks.pop(member.id)
        except KeyError:
            pass


def setup(bot):
    bot.add_cog(Utility(bot))
