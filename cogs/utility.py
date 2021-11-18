import asyncio
from datetime import datetime, timedelta
from typing import Optional, Union

import discord
from discord.ext import commands
from discord.ext.commands import Greedy
from dislash import ActionRow, Button, ButtonStyle, user_command


class Utility(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.group(name="purge", description="Clear/purge amount of message in channel.\nIgnores pinned messages.", aliases=['clear'], invoke_without_command=True)
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def purge_command(self, ctx, member: Optional[discord.User], amount: int = 1):
        def member_check(message):
            return not member and not message.pinned or message.author == member and not message.pinned
        
        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=amount, after=datetime.utcnow() -timedelta(days=14), check=member_check)
        
        if len(deleted) <= 1:
            return await ctx.send("No message was deleted! Make sure the messages aren't two weeks old.")
        elif 0 < amount <= 1000:
            embed = discord.Embed(
                title=f"{ctx.author.name} purged: {ctx.channel.name}",
                description=f"{len(deleted)} messages were cleared!",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed, delete_after=5)
        else:
            return await ctx.send("Amount should be less 1000 and more than 0.")

    @purge_command.command(name="human", description="Clear amount of messages by a human\nIgnores pinned messages.", aliases=["humans"])
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def purge_human(self, ctx, amount: int = 1):
        def human_check(message):
            return not message.author.bot and not message.pinned
        
        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=amount, after=datetime.utcnow() -timedelta(days=14), check=human_check)
        
        if len(deleted) <= 1:
            return await ctx.send("No message was deleted! Make sure the messages aren't two weeks old.")
        elif 0 < amount <= 1000:
            embed = discord.Embed(
                title=f"{ctx.author.name} purged: {ctx.channel.name}",
                description=f"{len(deleted)} messages were cleared!",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed, delete_after=5)
        else:
            return await ctx.send("Amount should be less 1000 and more than 0.")

    @purge_command.command(name="bot", description="Removes a bot user's messages.\nIgnores pinned messages.", aliases=["bots"])
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def purge_bot(self, ctx, amount: int = 1):
        def bot_check(message):
            return message.author.bot and not message.pinned
        
        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=amount, after=datetime.utcnow() -timedelta(days=14), check=bot_check)
        
        if len(deleted) <= 1:
            return await ctx.send("No message was deleted! Make sure the messages aren't two weeks old.")
        elif 0 < amount <= 1000:
            embed = discord.Embed(
                title=f"{ctx.author.name} purged: {ctx.channel.name}",
                description=f"{len(deleted)} messages were cleared!",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed, delete_after=5)
        else:
            return await ctx.send("Amount should be less 1000 and more than 0.")

    @purge_command.command(name="embed", description="Removes messages with embed.\nIgnores pinned messages.", aliases=["embeds"])
    @commands.guild_only()
    @commands.bot_has_permissions(manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def purge_embed(self, ctx, amount: int = 1):
        def embed_check(message):
            return len(message.embeds) > 0 and not message.pinned
        
        await ctx.message.delete()
        deleted = await ctx.channel.purge(limit=amount, after=datetime.utcnow() -timedelta(days=14), check=embed_check)
        
        if len(deleted) <= 1:
            return await ctx.send("No message was deleted! Make sure the messages aren't two weeks old.")
        elif 0 < amount <= 1000:
            embed = discord.Embed(
                title=f"{ctx.author.name} purged: {ctx.channel.name}",
                description=f"{len(deleted)} messages were cleared!",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed, delete_after=5)
        else:
            return await ctx.send("Amount should be less 1000 and more than 0.")

    @commands.command(name="nuke", description="Nukes the whole channel so you could start over.", aliases=["clone"])
    @commands.guild_only()
    @commands.has_permissions(manage_channels=True)
    @commands.cooldown(1, 10 , commands.BucketType.guild)
    async def nuke_command(self, ctx):
        confirm = ActionRow(
            Button(
                style=ButtonStyle.blurple,
                emoji="✅",
                custom_id="yes"
            ),
            Button(
                style=ButtonStyle.blurple,
                emoji="❌",
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
                    new_channel = await channel.clone(reason=f"Channel Nuked By {ctx.author} (ID: {ctx.author.id})")
                    await channel.delete(reason=f"Channel Nuked By {ctx.author} (ID: {ctx.author.id})")
                    await new_channel.send(f"{ctx.author.mention} Successfully nuked the channel!")
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

    @commands.command(name="mail", description="Mail/Dm a user through the bot because you're lazy ;-; to manually do it.", aliases=['dm'])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def mail_command(self, ctx, user: discord.User, *, msg):
        try:
            mail = discord.Embed(
                    title=f"Meow Mail Service",
                    description=f"```txt\n{msg}\n```", 
                    color=discord.Color.blurple(),

                 )
            mail.set_footer(text=f"Mail From {ctx.author.name}")
            await user.send(embed=mail)
            await ctx.send(f"Mailed {user} Successfully!!")
        except:
            await ctx.message.delete()
            await ctx.send(f"{user} has their DMs Closed!!", delete_after=5)

    @commands.command(name="avatar", description="Gives the users avatar.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def avatar(self, ctx, member : discord.User=None):
        member = ctx.author or member
        embed = discord.Embed(title=f"{member}'s Avatar!", colour=discord.Color.random(), timestamp=ctx.message.created_at)
        # embed.add_field(name="Links-", value=f"[jpg]({member.avatar.url_as(format=None, static_format='jpg', size=512)}) | [png]({member.avatar.url_as(format=None, static_format='png', size=512)}) | [webp]({member.avatar.url_as(format=None, static_format='webp', size=512)})")
        embed.set_image(url=member.avatar.url)
        await ctx.send(embed=embed)

    @commands.command(name="whois", description="Shows some interesting information about a member.",aliases=["userinfo"])
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

        embed = discord.Embed(colour=member.top_role.color, timestamp=ctx.message.created_at)

        embed.set_footer(text=f"Requested by: {ctx.author}", icon_url=ctx.author.avatar.url)
        embed.set_author(name=member, icon_url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)

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

        embed = discord.Embed(colour=member.top_role.color, timestamp=ctx.message.created_at)

        embed.set_footer(text=f"Requested by: {ctx.author}", icon_url=ctx.author.avatar.url)
        embed.set_author(name=member, icon_url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)

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
        await ctx.respond(embed=embed)
        
    @commands.command(
        name="prefix",
        aliases=["changeprefix", "setprefix"],
    )
    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild=True)
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def prefix(self, ctx, *, prefix=None):

        data = await self.client.config.get_by_id(ctx.guild.id)
        if not data or "prefix" not in data:
            current_prefix = "#"
        else:
            current_prefix = data["prefix"]

        if prefix == None:
            return await ctx.send(f"My current prefix for this server is `{current_prefix}`. Use `{current_prefix}prefix <prefix>` to change it")
            
        await self.client.config.upsert({"_id": ctx.guild.id, "prefix": prefix})
        await ctx.send(
            f"The guild prefix is changed to `{prefix}`. Use `{prefix}prefix [prefix]` to change it again!"
        )

    @commands.command(
        name='resetprefix',
        aliases=['deleteprefix'],
    )
    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild=True)
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def resetprefix(self, ctx):
        await self.client.config.delete(ctx.guild.id)
        await ctx.send("This guilds prefix is reset back to the default `#`")


    @commands.command(
        name='afk',
        description='Set Your Afk To Let People Know What Are You Doing.'
    )
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def afk(self, ctx, *, text: str=None):
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