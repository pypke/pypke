import discord, random, asyncio
from discord.ext import commands
from dislash import ActionRow, Button, ButtonStyle, InteractionType
from datetime import datetime

class Help(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.group(invoke_without_command=True, aliases=['commands'])
    @commands.guild_only()
    async def help(self, ctx):
        em = discord.Embed(title="Commands", description="Use `#help <command>` for extended information on a command.", colour=discord.Color.random())

        em.add_field(name=":gear: Moderation", value="`kick`, `ban`, `unban`, `mute`, `unmute`", inline=False)
        em.add_field(name=":tools: Utility", value="`purge`, `ping`, `avatar`, `whois`, `prefix`, `resetprefix`, `mail`", inline=False)
        em.add_field(name=":smile: Fun", value="`8ball`, `pat`, `meme`, `dankmeme`, `kill`, `cat`, `dog`", inline=False)
        em.add_field(name=":tada: Giveaway", value="`gstart`, `gcreate`, `greroll`", inline=False)

        old_msg = await ctx.send(embed=em, content="Website is currently work in-progress!! Take a look here\nhttps://docs.pypke.tk")

        if ctx.author.id == 624572769484668938:
            await old_msg.delete()
        else:
            return

        # New Help Command Work In-Progress
        current_page = 0
        mod_page = discord.Embed(
                                 title="Moderation Commands",
                                 description=f"""
                                 Use The Buttons Below To Change Pages.
                                 Use `#help <command>` for extended information on a command.

                                 :gear: Moderation Commands
                                 • `kick` - Kicks the user from the server.
                                 • `ban` - Bans the user from the server.
                                 • `unban` - Unbans the user from the server.
                                 • `mute` - Mute the member.
                                 • `ban` - Unmute the member.
                                 """,
                                 color=random.choice(self.client.color_list),
                                 timestamp=datetime.now()
                                )

        utils_page = discord.Embed(
                                 title="Utilty Commands",
                                 description=f"""
                                 Use The Buttons Below To Change Pages.
                                 Use `#help <command>` for extended information on a command.

                                 :tools: Utility Commands
                                 • `purge` - Deletes amount of messages from the used channel.
                                 • `ping` - Check the bot's ping.
                                 • `avatar` - Get your's or anyone else's avatar.
                                 • `whois` - Shows info about the member.
                                 • `prefix` - Set a custom prefix for your server.
                                 • `resetprefix` - Reset the prefix back to '#' for your server.
                                 • `mail` - Mails a member for you.
                                 """,
                                 color=random.choice(self.client.color_list),
                                 timestamp=datetime.now()
                                )

        pages = [mod_page, utils_page]
        page_btn = ActionRow(
            Button(
                    label = "Back",
                    custom_id = "back",
                    style = ButtonStyle.blurple
                ),
                Button(
                    label = f"Page {int(pages.index(pages[current_page])) + 1}/{len(pages)}",
                    custom_id = "cur",
                    style = ButtonStyle.gray,
                    disabled = True
                ),
                Button(
                    label = "Next",
                    custom_id = "ahead",
                    style = ButtonStyle.blurple
                ))
        help_msg = await ctx.send(embed=pages[current_page], components=[page_btn])
        while True:
            # Try and except blocks to catch timeout and break
            try:
                interaction = await self.client.wait_for(
                "button_click",
                check = lambda i: i.component.id in ["back", "ahead"], # You can add more
                timeout = 20.0 # 20 seconds of inactivity
            )
                # Getting the right list index
                if interaction.component.id == "back":
                    current_page -= 1
                elif interaction.component.id == "ahead":
                    current_page += 1
                # If its out of index, go back to start / end
                if current_page == len(pages):
                    current_page = 0
                elif current_page < 0:
                    current_page = len(pages) - 1

                # Redefination For Page Number
                page_btn = ActionRow(
                    Button(
                    label = "Back",
                    custom_id = "back",
                    style = ButtonStyle.blurple
                ),
                    Button(
                    label = f"Page {int(pages.index(pages[current_page])) + 1}/{len(pages)}",
                    custom_id = "cur",
                    style = ButtonStyle.gray,
                    disabled = True
                ),
                    Button(
                    label = "Next",
                    custom_id = "ahead",
                    style = ButtonStyle.blurple
                ))
                await interaction.respond(type=7, embed=pages[current_page], components=[page_btn])

            except asyncio.TimeoutError:
                disabled_page_btn = ActionRow(
                    Button(
                    label = "Back",
                    custom_id = "back",
                    style = ButtonStyle.blurple,
                    disabled=True
                ),
                    Button(
                    label = f"Page {int(pages.index(pages[current_page])) + 1}/{len(pages)}",
                    custom_id = "cur",
                    style = ButtonStyle.gray,
                    disabled = True
                ),
                    Button(
                    label = "Next",
                    custom_id = "ahead",
                    style = ButtonStyle.blurple,
                    disabled=True
                ))
                await help_msg.edit(components=[disabled_page_btn])
                break

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

        em.add_field(name="**Syntax**", value="#mute <member> [time: (s|m|h|d)]", inline=False)
        em.add_field(name="**Example**", value="#mute <@!624572769484668938> 10h", inline=False)
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
        
    @help.command(aliases=['setprefix', 'changeprefix'])
    async def prefix(self, ctx):
        em = discord.Embed(title="Set Prefix Command", description="Sets Prefix For Your Server!", color=discord.Color.random())
        
        em.add_field(name="**Syntax**", value="#prefix <prefix>", inline=False)
        em.add_field(name="**Aliases**", value="`setprefix`, `changeprefix`", inline=False)
        em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

        await ctx.send(embed=em)

    @help.command(aliases=['resetprefix', 'delprefix'])
    async def deleteprefix(self, ctx):
        em = discord.Embed(title="Reset Prefix Command", description="Changes Back The Server Prefix To Default `#`!", color=discord.Color.random())
        
        em.add_field(name="**Syntax**", value="#deleteprefix", inline=False)
        em.add_field(name="**Aliases**", value="`resetprefix`, `delprefix`", inline=False)
        em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

        await ctx.send(embed=em)

    @help.command(aliases=['dm'])
    async def mail(self, ctx):
        em = discord.Embed(title="Mail Command", description="Mail The User Using Meow Mail Service!", color=discord.Color.blurple())
        
        em.add_field(name="**Syntax**", value="#mail <user> <your_message>", inline=False)
        em.add_field(name="**Aliases**", value="`dm`", inline=False)
        em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

        await ctx.send(embed=em)

    @help.command()
    async def invite(self, ctx):
        em = discord.Embed(title="Invite Command", description="Invite This Bot To Your Server!", color=discord.Color.random())
        
        em.add_field(name="**Syntax**", value="#invite", inline=False)
        em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

        await ctx.send(embed=em)

    @help.command()
    async def stats(self, ctx):
        em = discord.Embed(title="Stats Command", description="Get Stats Of The Bot!", color=discord.Color.random())
        
        em.add_field(name="**Syntax**", value="#stats", inline=False)
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

    @help.command()
    async def gstart(self, ctx):
        em = discord.Embed(title="Start Giveaway", description="Starts A Giveaway In Current Channel!\nI Would Recommend `#gcreate` Instead!", color=discord.Color.random())
        
        em.add_field(name="**Syntax**", value="#gstart <time(In Mins)> <prize>", inline=False)
        em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

        await ctx.send(embed=em)

    @help.command()
    async def gcreate(self, ctx):
        em = discord.Embed(title="Creates Command", description="Creates A Giveaway!\nInteractive!", color=discord.Color.random())
        
        em.add_field(name="**Syntax**", value="#gcreate", inline=False)
        em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

        await ctx.send(embed=em)
    
    @help.command()
    async def greroll(self, ctx):
        em = discord.Embed(title="Re-roll Command", description="Re-rolls An Ended Giveaway!", color=discord.Color.random())
        
        em.add_field(name="**Syntax**", value="#greroll <channel> <msg_id>", inline=False)
        em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

        await ctx.send(embed=em)

def setup(client):
    client.add_cog(Help(client))