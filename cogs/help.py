import discord
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.group(invoke_without_command=True, aliases=['commands'])
    @commands.guild_only()
    async def help(self, ctx):
        em = discord.Embed(title="Commands", description="Use `#help <command>` for extended information on a command.", colour=discord.Color.random())

        em.add_field(name=":gear: Moderation", value="`kick`, `ban`, `unban`, `mute`, `unmute`", inline=False)
        em.add_field(name=":tools: Utility", value="`purge`, `ping`, `avatar`, `whois`", inline=False)
        em.add_field(name=":smile: Fun", value="`8ball`, `pat`, `meme`, `dankmeme`, `kill`", inline=False)
        em.add_field(name=":tada: Giveaway", value="`gstart`, `gcreate`, `greroll`", inline=False)
        em.add_field(name=":dog: Animals", value="`cat`, `dog`", inline=False)

        await ctx.send(embed=em)

    @help.command()
    async def kick(self, ctx):

        em = discord.Embed(title="Kick",
                          description="Kicks a member from the server!",
                          colour=discord.Color.random())

        em.add_field(name="**Syntax**", value="#kick <member> [reason]", inline=False)
        em.add_field(name="**Example**",
                    value="#kick <@!624572769484668938> Too Cool!", inline=False)
        em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

        await ctx.send(embed=em)


    @help.command()
    async def ban(self, ctx):

        em = discord.Embed(title="Ban",
                          description="Bans a member from the server!",
                          colour=discord.Color.random())

        em.add_field(name="**Syntax**", value="#ban <member> [reason]", inline=False)
        em.add_field(name="**Example**",
                    value="#ban <@!624572769484668938> Too Cool!", inline=False)
        em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

        await ctx.send(embed=em)


    @help.command()
    async def mute(self, ctx):

        em = discord.Embed(title="Mute",
                          description="Mutes a member!",
                          colour=discord.Color.random())

        em.add_field(name="**Syntax**", value="#mute <member>", inline=False)
        em.add_field(name="**Example**", value="#mute <@!624572769484668938>", inline=False)
        em.set_footer(
            text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

        await ctx.send(embed=em)


    @help.command()
    async def unban(self, ctx):

        em = discord.Embed(title="Unban",
                          description="Unbans a member from the server!",
                          colour=discord.Color.random())

        em.add_field(name="**Syntax**", value="#unban <member_id>", inline=False)
        em.add_field(name="**Example**", value="#unban Mr.Natural#3549", inline=False)
        em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

        await ctx.send(embed=em)


    @help.command()
    async def purge(self, ctx):

        em = discord.Embed(title="Purge",
                           description="Deletes a number of messages from a channel!",
                           colour=discord.Color.random())

        em.add_field(name="**Syntax**", value="#purge <no_of_messages>", inline=False)
        em.add_field(name="**Aliases**", value="`clear`", inline=False)
        em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

        await ctx.send(embed=em)


    @help.command()
    async def unmute(self, ctx):

        em = discord.Embed(title="Unmute",
                          description="Unmutes a member!",
                          colour=discord.Color.random())

        em.add_field(name="**Syntax**", value="#unmute <member>", inline=False)
        em.add_field(name="**Example**", value="#unmute <@!624572769484668938>", inline=False)
        em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

        await ctx.send(embed=em)


    @help.command()
    async def ping(self, ctx):

        em = discord.Embed(title="Ping",
                          description="Displays the current latency!",
                          colour=discord.Color.random())

        em.add_field(name="**Syntax**", value="#ping", inline=False)
        em.add_field(name="**Aliases**", value="`pong`", inline=False)
        em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

        await ctx.send(embed=em)

    @help.command(aliases=['8ball'])
    async def _8ball(self, ctx):
        em = discord.Embed(title="8ball", description="Decides Something For You!", color=discord.Color.random())
        
        em.add_field(name="**Syntax**", value="#8ball <question>", inline=False)
        em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

        await ctx.send(embed=em)

    @help.command()
    async def pat(self, ctx):
        em = discord.Embed(title="Pat", description="Pats the user you mention!", color=discord.Color.random())
        
        em.add_field(name="**Syntax**", value="#pat <mention>", inline=False)
        em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

        await ctx.send(embed=em)

    @help.command()
    async def meme(self, ctx):
        em = discord.Embed(title="Meme", description="Shows a meme from r/memes!", color=discord.Color.random())
        
        em.add_field(name="**Syntax**", value="#meme", inline=False)
        em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

        await ctx.send(embed=em)

    @help.command(aliases=['dmeme', 'deme'])
    async def dankmeme(self, ctx):
        em = discord.Embed(title="Dank Meme", description="Shows a meme from r/dankmemes!", color=discord.Color.random())
        
        em.add_field(name="**Syntax**", value="#dankmeme", inline=False)
        em.add_field(name="**Aliases**", value="`dmeme`, `deme`", inline=False)
        em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

        await ctx.send(embed=em)

    @help.command()
    async def cat(self, ctx):
        em = discord.Embed(title="Cat", description="Shows a cat picture!", color=discord.Color.random())
        
        em.add_field(name="**Syntax**", value="#cat", inline=False)
        em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

        await ctx.send(embed=em)

    @help.command()
    async def dog(self, ctx):
        em = discord.Embed(title="Dog", description="Shows a dog picture!", color=discord.Color.random())
        
        em.add_field(name="**Syntax**", value="#dog", inline=False)
        em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

        await ctx.send(embed=em)

    @help.command()
    async def kill(self, ctx):
        em = discord.Embed(title="Kill", description="Kills The Person You Mention!", color=discord.Color.random())
        
        em.add_field(name="**Syntax**", value="#kill <member>", inline=False)
        em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

        await ctx.send(embed=em)

    @help.command(aliases=['userinfo', 'info'])
    async def whois(self, ctx):
        em = discord.Embed(title="Whois", description="Displays detailed information about the person!", color=discord.Color.random())
        
        em.add_field(name="**Syntax**", value="#whois <member>", inline=False)
        em.add_field(name="**Aliases**", value="`user-info`, `info`", inline=False)
        em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

        await ctx.send(embed=em)

    @help.command()
    async def avatar(self, ctx):
        em = discord.Embed(title="Avatar", description="Gives the discord avatar of the person!", color=discord.Color.random())
        
        em.add_field(name="**Syntax**", value="#avatar <member>", inline=False)
        em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

        await ctx.send(embed=em)

    @help.command()
    async def gstart(self, ctx):
        em = discord.Embed(title="Start Giveaway", description="Starts A Giveaway In Current Channel!\nI Would Recommend `#gcreate` Instead!", color=discord.Color.random())
        
        em.add_field(name="**Syntax**", value="#gstart <time(In Mins)> <prize>", inline=False)
        em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

        await ctx.send(embed=em)

    @help.command()
    async def gcreate(self, ctx):
        em = discord.Embed(title="Creates Giveaway", description="Creates A Giveaway!\nInteractive Setup!", color=discord.Color.random())
        
        em.add_field(name="**Syntax**", value="#gcreate", inline=False)
        em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

        await ctx.send(embed=em)
    
    @help.command()
    async def greroll(self, ctx):
        em = discord.Embed(title="ReRoll Giveaway", description="ReRolls An Ended Giveaway!", color=discord.Color.random())
        
        em.add_field(name="**Syntax**", value="#greroll <channel> <msg_id>", inline=False)
        em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

        await ctx.send(embed=em)

def setup(client):
    client.add_cog(Help(client))