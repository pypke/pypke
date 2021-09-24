import discord
from discord.ext import commands
from dislash import ActionRow, Button, ButtonStyle
from datetime import datetime

class Utility(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['pong'])
    async def ping(self, ctx):
        await ctx.send(f":ping_pong: Pong! \nCurrent End-to-End latency is `{round(self.client.latency * 1000)}ms`")

    @commands.command(aliases=['purge'])
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def clear(self, ctx, amount=1):
        if amount > 1000:
            await ctx.channel.purge(limit=1)
            await ctx.send("You Can't Purge/Clear Message Over `1000`!", delete_after=3)
            return
        await ctx.channel.purge(limit=amount + 1)
        embed = discord.Embed(
            title=f"{ctx.author.name} purged: {ctx.channel.name}",
            description=f"```\n{amount} messages were cleared\n```",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed, delete_after=2)

    @commands.command(aliases=['mail'])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def dm(self, ctx, user: discord.User, *, msg):
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

    @commands.command()
    async def avatar(self, ctx, member : discord.User=None):
        if member == None:
            member = ctx.author
            embed = discord.Embed(title=f"{member}'s Avatar!", colour=discord.Color.random(), timestamp=ctx.message.created_at)
            embed.add_field(name="Links-", value=f"[jpg]({member.avatar_url_as(format=None, static_format='jpg', size=512)}) | [png]({member.avatar_url_as(format=None, static_format='png', size=512)}) | [webp]({member.avatar_url_as(format=None, static_format='webp', size=512)})")
            embed.set_image(url=member.avatar_url)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title=f"{member}'s Avatar!", colour=discord.Color.random(), timestamp=ctx.message.created_at)
            embed.add_field(name="Links-", value=f"[jpg]({member.avatar_url_as(format=None, static_format='jpg', size=512)}) | [png]({member.avatar_url_as(format=None, static_format='png', size=512)}) | [webp]({member.avatar_url_as(format=None, static_format='webp', size=512)})")
            embed.set_image(url=member.avatar_url)
            await ctx.send(embed=embed)

    @commands.command(aliases=['user-info', 'info'])
    @commands.guild_only()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def whois(self, ctx, member:discord.Member =  None):

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

        embed = discord.Embed(title=f"{member}", colour=discord.Color.random(), timestamp=ctx.message.created_at)
        embed.set_footer(text=f"Requested by: {ctx.author}", icon_url=ctx.author.avatar_url)
        embed.set_author(name="User Info: ")
        embed.add_field(name="ID:", value=member.id, inline=False)
        embed.add_field(name="Nickname:", value=member.display_name, inline=False)
        embed.add_field(name="Current Status:", value=str(member.status).title(), inline=False)
        embed.add_field(name="Created At:", value=f"<t:{created_time}:f>", inline=False)
        embed.add_field(name="Joined At:", value=f"<t:{joined_time}:f>", inline=False)
        embed.add_field(name=f"Roles [{len(roles)}]", value=" **|** ".join([role.mention for role in roles]), inline=False)
        embed.add_field(name="Highest Role:", value=member.top_role, inline=False)
        embed.add_field(name="Bot?", value=member.bot, inline=False)
        await ctx.send(embed=embed)
        
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

    @commands.command(description="Get a link to invite this bot")
    async def invite(self, inter):
        invite_btn = ActionRow(Button(
                style=ButtonStyle.link,
                label="Invite",
                url= "https://discord.com/oauth2/authorize?client_id=823051772045819905&permissions=8&scope=bot%20applications.commands"
            ))
        embed = discord.Embed(title="Pypke Bot", description="You Can Invite The Bot By Clicking The Button Below!", color=discord.Color.blurple(), timestamp=datetime.now())
        embed.set_footer(text="Bot by Mr.Natural#3549")

        await inter.send(content="This Bot Is Still In Development You May Experience Downtime!!\n", embed=embed, components=[invite_btn])

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