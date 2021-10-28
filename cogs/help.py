from datetime import datetime
from typing import Union, Optional

import discord, random, asyncio
from discord.ext import commands
from dislash import ActionRow, Button, ButtonStyle

class Help(commands.Cog):
    def __init__(self, client):
        self.client = client

    def get_syntax(self, command: commands.Command):
        aliases = "|".join(command.aliases)
        cmd_invoke = f"[{command.name}|{aliases}]" if command.aliases else command.name

        full_invoke = command.qualified_name.replace(command.name, "")

        signature = f"{full_invoke}{cmd_invoke} {command.signature}"
        return signature

    def cog_help(self, ctx, cog):
        embed = discord.Embed(
            title=cog.qualified_name,
            description=f"Use The Buttons Below To Change Pages.\nUse `{ctx.prefix}help <command>` for extended information on a command.\n\n",
            color=self.client.randcolor
        )
        commands = ", ".join(str(command) for command in cog.get_commands())
        embed.add_field(
            name="Commands",
            value=commands if commands else discord.Embed.Empty,
            inline=False
        )
        
        return embed

    @commands.command(name="testhelp", hidden=True)
    @commands.is_owner()
    async def testhelp(self, ctx, *, cog):
        cog = self.client.get_cog(cog)
        embed = self.cog_help(ctx, cog)
        await ctx.send(embed=embed)


    @commands.command(name="help", description="wdym you need a help for help command? idiot", aliases=['commands'])
    @commands.guild_only()
    async def help(self, ctx, *, command: str = None):
        # New Help Command Work In-Progress
        current = 0
        first_page = discord.Embed(
            title="Commands",
            description="Documentation is work in-progress. Take a look here\nhttps://docs.pypke.tk\n\nDo The Commands Below To View Specific Page.",
            color=self.client.randcolor,
            timestamp=datetime.now()
        )
        first_page.add_field(name="Moderation Commands", value="`#help moderation`")
        first_page.add_field(name="Utility Commands", value="`#help utility`")
        first_page.add_field(name="Fun Commands", value="`#help fun`")
        first_page.add_field(name="Bot Commands", value="`#help bot`")
        first_page.add_field(name="Giveaway Commands", value="`#help giveaway`")
        first_page.add_field(name="Music Commands", value="`#help music`")
        
        # GLobal Pages
        global mod
        global utility
        global fun
        global bot
        global giveaway
        global music

        mod = discord.Embed(
                                 title="Moderation Commands",
                                 description="Use The Buttons Below To Change Pages.\nUse `#help <command>` for extended information on a command.\n\n:gear: Moderation Commands\n• `kick` - Kicks the user from the server.\n• `ban` - Bans the user from the server.\n• `unban` - Unbans the user from the server.\n• `mute` - Mute the member.\n• `ban` - Unmute the member.",
                                 color=random.choice(self.client.color_list),
                                 timestamp=datetime.now()
                                )

        utility = discord.Embed(
                                 title="Utilty Commands",
                                 description="Use The Buttons Below To Change Pages.\nUse `#help <command>` for extended information on a command.\n\n:tools: Utility Commands\n• `purge` - Deletes amount of messages from the used channel.\n• `avatar` - Get your's or anyone else's avatar.\n• `whois` - Shows info about the member.\n• `prefix` - Set a custom prefix for your server.\n• `resetprefix` - Reset the prefix back to '#' for your server.\n• `mail` - Mails a member for you.",
                                 color=random.choice(self.client.color_list),
                                 timestamp=datetime.now()
                                )
                                
        fun = discord.Embed(
                                 title="Fun Commands",
                                 description=f"Use The Buttons Below To Change Pages.\nUse `#help <command>` for extended information on a command.\n\n:smile: Fun Commands\n• `8ball` - Question the 8ball and it shall answer.\n• `joke` - Sends you a joke.\n• `pokedex` - Search a pokemon's dex entry.\n• `pat` - Pat a user.\n• `meme` - See memes from r/memes.\n• `dankmeme` - See memes from r/dankmemes.\n• `kill` - Kill a user with words.\n• `cat` - Shows a cat image.\n• `dog` - Shows a dog image.",
                                 color=random.choice(self.client.color_list),
                                 timestamp=datetime.now()
                                )

        bot = discord.Embed(
                                 title="Bot Commands",
                                 description=f"Use The Buttons Below To Change Pages.\nUse `#help <command>` for extended information on a command.\n\n:robot: Bot Commands\n• `ping` - Ping to check the bot's latency.\n• `stats` - Check the bot's stats.\n• `uptime` - Check the bot's uptime.\n• `invite` - Invite me to your server.",
                                 color=random.choice(self.client.color_list),
                                 timestamp=datetime.now()
                                )

        giveaway = discord.Embed(
                                 title="Giveaway Commands",
                                 description=f"Use The Buttons Below To Change Pages.\nUse `#help <command>` for extended information on a command.\n\n:tada: Giveaway Commands\n• `gstart` - Start a giveaway quickly.\n• `gcreate` - Start a giveaway but interactively.\n• `greroll` - Reroll a giveaway winner.\n• `gend` - End a giveaway.",
                                 color=random.choice(self.client.color_list),
                                 timestamp=datetime.now()
                                )

        music = discord.Embed(
                                 title="Music Commands",
                                 description=f"Use The Buttons Below To Change Pages.\nUse `#help <command>` for extended information on a command.\n\n:musical_note: Music Commands\n• `join` - Make the bot join your vc.\n• `play` - Play a song.\n• `skip` - Skips current playing song.\n• `queue` - Shows you the songs currenly in queue.\n• `volume` - Change the bot's volume.\n• `stop` - Make the bot leave the vc.",
                                 color=random.choice(self.client.color_list),
                                 timestamp=datetime.now()
                                )
        
        pages = [first_page, mod, utility, bot, fun, giveaway, music]

        # if command != None and command.lower() in pages:
        #     await ctx.send(embed=command.lower())
        try:
            cmd = self.client.get_command(command)
            if not cmd:
                raise commands.CommandNotFound
                return
            
            cmd_embed = discord.Embed(
                title=f"{cmd.qualified_name} {cmd.signature}",
                description=cmd.description if cmd.description else "No Help Provided",
                color=self.client.color
            )
            return await ctx.send(embed=cmd_embed)
        except:
            pass

        page_btn = ActionRow(
            Button(
                    label = "Back",
                    custom_id = "back",
                    style = ButtonStyle.blurple
                ),
                Button(
                    label = f"Page {int(pages.index(pages[current])) + 1}/{len(pages)}",
                    custom_id = "cur",
                    style = ButtonStyle.gray,
                    disabled = True
                ),
                    Button(
                    label = "Stop",
                    custom_id = "stop",
                    style = ButtonStyle.red
                ),
                Button(
                    label = "Next",
                    custom_id = "ahead",
                    style = ButtonStyle.blurple
                ))
        help_msg = await ctx.send(embed=pages[current], components=[page_btn])
        while True:
            # Try and except blocks to catch timeout and break
            def check(inter):
                return inter.message.id == help_msg.id and inter.author.id == ctx.author.id
                
            try:
                inter = await ctx.wait_for_button_click(check=check, timeout=20.0)
                
                if (inter.clicked_button.label.lower() == "back"):
                    current -= 1
                elif (inter.clicked_button.label.lower() == "next"):
                    current += 1
                elif (inter.clicked_button.label.lower() == "stop"):
                    await help_msg.edit(components=[])
                    break

                # If its out of index, go back to start / end
                if current == len(pages):
                    current = 0
                elif current < 0:
                    current = len(pages) - 1

                # Redefination For Page Number
                page_btn = ActionRow(
                    Button(
                    label = "Back",
                    custom_id = "back",
                    style = ButtonStyle.blurple
                ),
                    Button(
                    label = f"Page {int(pages.index(pages[current])) + 1}/{len(pages)}",
                    custom_id = "cur",
                    style = ButtonStyle.gray,
                    disabled = True
                ),
                    Button(
                    label = "Stop",
                    custom_id = "stop",
                    style = ButtonStyle.red
                ),
                    Button(
                    label = "Next",
                    custom_id = "ahead",
                    style = ButtonStyle.blurple
                ))
                await inter.reply(type=7, embed=pages[current], components=[page_btn])

            except asyncio.TimeoutError:
                await help_msg.edit(components=[])
                break
            except:
                break
    
    # # Pages Help
    # @help.command()
    # async def moderation(self, ctx):
    #     await ctx.send(embed=mod)

    # @help.command()
    # async def utility(self, ctx):
    #     await ctx.send(embed=utility)

    # @help.command()
    # async def fun(self, ctx):
    #     await ctx.send(embed=fun)

    # @help.command()
    # async def bot(self, ctx):
    #     await ctx.send(embed=bot)

    # @help.command()
    # async def giveaway(self, ctx):
    #     await ctx.send(embed=giveaway)

    # @help.command()
    # async def music(self, ctx):
    #     await ctx.send(embed=music)
        
    # # Moderation Command
    # @help.command()
    # async def kick(self, ctx):

    #     em = discord.Embed(title="Kick",
    #                       description="Kicks a member from the server!",
    #                       colour=discord.Color.random())

    #     em.add_field(name="**Syntax**", value="#kick <member> [reason]", inline=False)
    #     em.add_field(name="**Required Perms**", value="Kick Member", inline=False)
    #     em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

    #     await ctx.send(embed=em)


    # @help.command()
    # async def ban(self, ctx):

    #     em = discord.Embed(title="Ban",
    #                       description="Bans a member from the server!",
    #                       colour=discord.Color.random())

    #     em.add_field(name="**Syntax**", value="#ban <member> [reason]", inline=False)
    #     em.add_field(name="**Required Perms**", value="Ban Member", inline=False)
    #     em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

    #     await ctx.send(embed=em)


    # @help.command()
    # async def mute(self, ctx):

    #     em = discord.Embed(title="Mute",
    #                       description="Mutes a member!",
    #                       colour=discord.Color.random())

    #     em.add_field(name="**Syntax**", value="#mute <member> [time: (s|m|h|d)]", inline=False)
    #     em.add_field(name="**Required Perms**", value="Manage Roles", inline=False)
    #     em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

    #     await ctx.send(embed=em)


    # @help.command()
    # async def unban(self, ctx):

    #     em = discord.Embed(title="Unban",
    #                       description="Unbans a member from the server!",
    #                       colour=discord.Color.random())

    #     em.add_field(name="**Syntax**", value="#unban <member_id>", inline=False)
    #     em.add_field(name="**Required Perms**", value="Ban Member", inline=False)
    #     em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

    #     await ctx.send(embed=em)

    # @help.command()
    # async def unmute(self, ctx):

    #     em = discord.Embed(title="Unmute",
    #                       description="Unmutes a member!",
    #                       colour=discord.Color.random())

    #     em.add_field(name="**Syntax**", value="#unmute <member>", inline=False)
    #     em.add_field(name="**Required Perms**", value="Manage Roles", inline=False)
    #     em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

    #     await ctx.send(embed=em)

    # # Bot Commands
    # @help.command()
    # async def ping(self, ctx):

    #     em = discord.Embed(title="Ping", description="Displays the current latency!", colour=discord.Color.random())

    #     em.add_field(name="**Syntax**", value="#ping", inline=False)
    #     em.add_field(name="**Aliases**", value="`pong`", inline=False)
    #     em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

    #     await ctx.send(embed=em)
    
    # @help.command()
    # async def invite(self, ctx):
    #     em = discord.Embed(title="Invite Command", description="Invite This Bot To Your Server!", color=discord.Color.random())
        
    #     em.add_field(name="**Syntax**", value="#invite", inline=False)
    #     em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

    #     await ctx.send(embed=em)

    # @help.command()
    # async def uptime(self, ctx):
    #     em = discord.Embed(title="Uptime Command", description="Check the bots uptime!", color=discord.Color.random())
        
    #     em.add_field(name="**Syntax**", value="#uptime", inline=False)
    #     em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

    #     await ctx.send(embed=em)
    
    # @help.command()
    # async def stats(self, ctx):
    #     em = discord.Embed(title="Stats Command", description="Get Stats Of The Bot!", color=discord.Color.random())
        
    #     em.add_field(name="**Syntax**", value="#stats", inline=False)
    #     em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

    #     await ctx.send(embed=em)

    # # Utility Commands
    # @help.command()
    # async def purge(self, ctx):

    #     em = discord.Embed(title="Purge",
    #                        description="Deletes a number of messages from a channel!",
    #                        colour=discord.Color.random())

    #     em.add_field(name="**Syntax**", value="#purge <no_of_messages>", inline=False)
    #     em.add_field(name="**Required Perms**", value="Manage Messages", inline=False)
    #     em.add_field(name="**Aliases**", value="`clear`", inline=False)
    #     em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")


    #     await ctx.send(embed=em)

    # @help.command(aliases=['userinfo', 'info'])
    # async def whois(self, ctx):
    #     em = discord.Embed(title="Whois", description="Displays detailed information about the person!", color=discord.Color.random())
        
    #     em.add_field(name="**Syntax**", value="#whois <member>", inline=False)
    #     em.add_field(name="**Aliases**", value="`user-info`, `info`", inline=False)
    #     em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

    #     await ctx.send(embed=em)

    # @help.command()
    # async def avatar(self, ctx):
    #     em = discord.Embed(title="Avatar", description="Gives the discord avatar of the person!", color=discord.Color.random())
        
    #     em.add_field(name="**Syntax**", value="#avatar <member>", inline=False)
    #     em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

    #     await ctx.send(embed=em)
        
    # @help.command(aliases=['setprefix', 'changeprefix'])
    # async def prefix(self, ctx):
    #     em = discord.Embed(title="Set Prefix Command", description="Sets Prefix For Your Server!", color=discord.Color.random())
        
    #     em.add_field(name="**Syntax**", value="#prefix <prefix>", inline=False)
    #     em.add_field(name="**Required Perms**", value="Manage Guild", inline=False)
    #     em.add_field(name="**Aliases**", value="`setprefix`, `changeprefix`", inline=False)
    #     em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

    #     await ctx.send(embed=em)

    # @help.command(aliases=['resetprefix', 'delprefix'])
    # async def deleteprefix(self, ctx):
    #     em = discord.Embed(title="Reset Prefix Command", description="Changes Back The Server Prefix To Default `#`!", color=discord.Color.random())
        
    #     em.add_field(name="**Syntax**", value="#deleteprefix", inline=False)
    #     em.add_field(name="**Required Perms**", value="Manage Guild", inline=False)
    #     em.add_field(name="**Aliases**", value="`resetprefix`, `delprefix`", inline=False)
    #     em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

    #     await ctx.send(embed=em)

    # @help.command(aliases=['dm'])
    # async def mail(self, ctx):
    #     em = discord.Embed(title="Mail Command", description="Mail The User Using Meow Mail Service!", color=discord.Color.blurple())
        
    #     em.add_field(name="**Syntax**", value="#mail <user> <your_message>", inline=False)
    #     em.add_field(name="**Required Perms**", value="Manage Guild", inline=False)
    #     em.add_field(name="**Aliases**", value="`dm`", inline=False)
    #     em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

    #     await ctx.send(embed=em)

    # # Fun Commands
    # @help.command(aliases=['8ball'])
    # async def _8ball(self, ctx):
    #     em = discord.Embed(title="8ball", description="Decides Something For You!", color=discord.Color.random())
        
    #     em.add_field(name="**Syntax**", value="#8ball <question>", inline=False)
    #     em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

    #     await ctx.send(embed=em)

    # @help.command()
    # async def pat(self, ctx):
    #     em = discord.Embed(title="Pat", description="Pats the user you mention!", color=discord.Color.random())
        
    #     em.add_field(name="**Syntax**", value="#pat <mention>", inline=False)
    #     em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

    #     await ctx.send(embed=em)

    # @help.command()
    # async def meme(self, ctx):
    #     em = discord.Embed(title="Meme", description="Shows a meme from r/memes!", color=discord.Color.random())
        
    #     em.add_field(name="**Syntax**", value="#meme", inline=False)
    #     em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

    #     await ctx.send(embed=em)

    # @help.command(aliases=['dmeme', 'deme'])
    # async def dankmeme(self, ctx):
    #     em = discord.Embed(title="Dank Meme", description="Shows a meme from r/dankmemes!", color=discord.Color.random())
        
    #     em.add_field(name="**Syntax**", value="#dankmeme", inline=False)
    #     em.add_field(name="**Aliases**", value="`dmeme`, `deme`", inline=False)
    #     em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

    #     await ctx.send(embed=em)

    # @help.command()
    # async def cat(self, ctx):
    #     em = discord.Embed(title="Cat", description="Shows a cat picture!", color=discord.Color.random())
        
    #     em.add_field(name="**Syntax**", value="#cat", inline=False)
    #     em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

    #     await ctx.send(embed=em)

    # @help.command()
    # async def dog(self, ctx):
    #     em = discord.Embed(title="Dog Image Command", description="Shows a dog picture!", color=discord.Color.random())
        
    #     em.add_field(name="**Syntax**", value="#dog", inline=False)
    #     em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

    #     await ctx.send(embed=em)

    # @help.command()
    # async def kill(self, ctx):
    #     em = discord.Embed(title="Kill Command", description="Kills The Person With words! Not Really", color=discord.Color.random())
        
    #     em.add_field(name="**Syntax**", value="#kill <member>", inline=False)
    #     em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

    #     await ctx.send(embed=em)

    # @help.command()
    # async def joke(self, ctx):
    #     em = discord.Embed(title="Joke Command", description="Sends you a joke!", color=discord.Color.random())
        
    #     em.add_field(name="**Syntax**", value="#joke", inline=False)
    #     em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

    #     await ctx.send(embed=em)

    # @help.command(aliases=['dex'])
    # async def pokedex(self, ctx):
    #     em = discord.Embed(title="Pokedex Command", description="Search a pokemon's pokedex entry for you!", color=discord.Color.random())
        
    #     em.add_field(name="**Syntax**", value="#pokedex <pokemon-name>", inline=False)
    #     em.add_field(name="**Aliases**", value="`dex`", inline=False)
    #     em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

    #     await ctx.send(embed=em)

    # # Giveaway Commands Help
    # @help.command()
    # async def gstart(self, ctx):
    #     em = discord.Embed(title="Start Giveaway", description="Starts A Giveaway In Current Channel!\nI Would Recommend `#gcreate` Instead!\nCause This Command Breaks Sometimes.", color=discord.Color.random())
        
    #     em.add_field(name="**Syntax**", value="#gstart <time> <channel> <prize>", inline=False)
    #     em.add_field(name="**Required Perms**", value="Manage Guild", inline=False)
    #     em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

    #     await ctx.send(embed=em)

    # @help.command()
    # async def gcreate(self, ctx):
    #     em = discord.Embed(title="Creates Command", description="Creates A Giveaway!\nInteractive!", color=discord.Color.random())
        
    #     em.add_field(name="**Syntax**", value="#gcreate", inline=False)
    #     em.add_field(name="**Required Perms**", value="Manage Guild", inline=False)
    #     em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

    #     await ctx.send(embed=em)
    
    # @help.command()
    # async def greroll(self, ctx):
    #     em = discord.Embed(title="Reroll Giveaway Command", description="Rerolls A Giveaway To Get A New Winner!", color=discord.Color.random())
        
    #     em.add_field(name="**Syntax**", value="#greroll <channel> <msg_id>", inline=False)
    #     em.add_field(name="**Required Perms**", value="Manage Guild", inline=False)
    #     em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

    #     await ctx.send(embed=em)

    # @help.command()
    # async def gend(self, ctx):
    #     em = discord.Embed(title="End Giveaway Command", description="End A Giveaway To Get A Winner!", color=discord.Color.random())
        
    #     em.add_field(name="**Syntax**", value="#gend <msg_id>", inline=False)
    #     em.add_field(name="**Required Perms**", value="Manage Guild", inline=False)
    #     em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

    #     await ctx.send(embed=em)

def setup(client):
    client.add_cog(Help(client))