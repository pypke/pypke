import discord
from discord.ext import commands

class Utility(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(aliases=['pong'])
    async def ping(self, ctx):
        await ctx.send(f":ping_pong: Pong! \nCurrent End-to-End latency is `{round(self.client.latency * 1000)}ms`")

    @commands.command(aliases=['purge'])
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
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
            await ctx.channel.purge(limit = 1)
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
    async def whois(self, ctx, member:discord.Member =  None):

        if member is None:
            member = ctx.author
            roles = [role for role in ctx.author.roles]

        else:
            roles = [role for role in member.roles]

        embed = discord.Embed(title=f"{member}", colour=discord.Color.random(), timestamp=ctx.message.created_at)
        embed.set_footer(text=f"Requested by: {ctx.author}", icon_url=ctx.author.avatar_url)
        embed.set_author(name="User Info: ")
        embed.add_field(name="ID:", value=member.id, inline=False)
        embed.add_field(name="User Name:",value=member.display_name, inline=False)
        embed.add_field(name="Discriminator:",value=member.discriminator, inline=False)
        embed.add_field(name="Current Status:", value=str(member.status).title(), inline=False)
        embed.add_field(name="Current Activity:", value=f"{str(member.activity.type).title().split('.')[1]} {member.activity.name}" if member.activity is not None else "None", inline=False)
        embed.add_field(name="Created At:", value=member.created_at.strftime("%a, %d, %B, %Y, %I, %M, %p UTC"), inline=False)
        embed.add_field(name="Joined At:", value=member.joined_at.strftime("%a, %d, %B, %Y, %I, %M, %p UTC"), inline=False)
        embed.add_field(name=f"Roles [{len(roles)}]", value=" **|** ".join([role.mention for role in roles]), inline=False)
        embed.add_field(name="Top Role:", value=member.top_role, inline=False)
        embed.add_field(name="Bot:", value=member.bot, inline=False)
        await ctx.send(embed=embed)
        return
    
    
    @commands.command(
        name="prefix",
        aliases=["changeprefix", "setprefix"],
    )
    @commands.guild_only()
    @commands.has_guild_permissions(manage_guild=True)
    async def prefix(self, ctx, *, prefix="#"):
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
    async def resetprefix(self, ctx):
        await self.client.config.delete(ctx.guild.id)
        await ctx.send("This guilds prefix is reset back to the default `#`")


def setup(client):
    client.add_cog(Utility(client))