import discord, random, asyncio
from discord.ext import commands
from dislash import ActionRow, Button, ButtonStyle
from datetime import datetime

class Help(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.group(invoke_without_command=True, aliases=['commands'])
    @commands.guild_only()
    async def help(self, ctx):
        # New Help Command Work In-Progress
        current_page = 0
        first_page = discord.Embed(
            title="Commands",
            description="Documentation is work in-progress. Take a look [here](https://docs.pypke.tk/)\n\n**Moderation Commands**\n`#help moderation`\n\n**Utility Commands**\n`#help utility`\n\n**Fun Commands**\n`#help fun`\n\n**Bot Commands**\n`#help bot`\n\n**Giveaway Commands**\n`#help giveaway`\n\n**Music Commands**\n`#help music`",
            color=random.choice(self.client.color_list),
            timestamp=datetime.now()
        )
        
        # GLobal Pages
        global mod_page
        global utils_page
        global fun_page
        global bot_page
        global gaway_page
        global music_page

        mod_page = discord.Embed(
                                 title="Moderation Commands",
                                 description="Use The Buttons Below To Change Pages.\nUse `#help <command>` for extended information on a command.\n\n:gear: Moderation Commands\n• `kick` - Kicks the user from the server.\n• `ban` - Bans the user from the server.\n• `unban` - Unbans the user from the server.\n• `mute` - Mute the member.\n• `ban` - Unmute the member.",
                                 color=random.choice(self.client.color_list),
                                 timestamp=datetime.now()
                                )

        utils_page = discord.Embed(
                                 title="Utilty Commands",
                                 description="Use The Buttons Below To Change Pages.\nUse `#help <command>` for extended information on a command.\n\n:tools: Utility Commands\n• `purge` - Deletes amount of messages from the used channel.\n• `avatar` - Get your's or anyone else's avatar.\n• `whois` - Shows info about the member.\n• `prefix` - Set a custom prefix for your server.\n• `resetprefix` - Reset the prefix back to '#' for your server.\n• `mail` - Mails a member for you.",
                                 color=random.choice(self.client.color_list),
                                 timestamp=datetime.now()
                                )
                                
        fun_page = discord.Embed(
                                 title="Fun Commands",
                                 description=f"Use The Buttons Below To Change Pages.\nUse `#help <command>` for extended information on a command.\n\n:smile: Fun Commands\n• `8ball` - Question the 8ball and it shall answer.\n• `pat` - Pat a user.\n• `meme` - See memes from r/memes.\n• `dankmeme` - See memes from r/dankmemes.\n• `kill` - Kill a user with words.\n• `cat` - Shows a cat image.\n• `dog` - Shows a dog image.",
                                 color=random.choice(self.client.color_list),
                                 timestamp=datetime.now()
                                )

        bot_page = discord.Embed(
                                 title="Bot Commands",
                                 description=f"Use The Buttons Below To Change Pages.\nUse `#help <command>` for extended information on a command.\n\n:robot: Bot Commands\n• `ping` - Ping to check the bot's latency.\n• `stats` - Check the bot's stats.\n• `uptime` - Check the bot's uptime.\n• `invite` - Invite me to your server.",
                                 color=random.choice(self.client.color_list),
                                 timestamp=datetime.now()
                                )

        gaway_page = discord.Embed(
                                 title="Giveaway Commands",
                                 description=f"Use The Buttons Below To Change Pages.\nUse `#help <command>` for extended information on a command.\n\n:tada: Giveaway Commands\n• `gstart` - Start a giveaway quickly.\n• `gcreate` - Start a giveaway but interactively.\n• `greroll` - Reroll a giveaway winner.\n• `gend` - End a giveaway.",
                                 color=random.choice(self.client.color_list),
                                 timestamp=datetime.now()
                                )

        music_page = discord.Embed(
                                 title="Music Commands",
                                 description=f"Use The Buttons Below To Change Pages.\nUse `#help <command>` for extended information on a command.\n\n:musical_note: Music Commands\n• `join` - Make the bot join your vc.\n• `play` - Play a song.\n• `disconnect` - Make the bot leave the vc.",
                                 color=random.choice(self.client.color_list),
                                 timestamp=datetime.now()
                                )
        
        pages = [first_page, mod_page, utils_page, bot_page, fun_page, gaway_page, music_page]
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
                    label = "Stop",
                    custom_id = "stop",
                    style = ButtonStyle.red
                ),
                Button(
                    label = "Next",
                    custom_id = "ahead",
                    style = ButtonStyle.blurple
                ))
        help_msg = await ctx.send(embed=pages[current_page], components=[page_btn])
        while True:
            # Try and except blocks to catch timeout and break
            def check(inter):
                return inter.message.id == help_msg.id and inter.author.id == ctx.author.id
                
            try:
                inter = await ctx.wait_for_button_click(check=check, timeout=15.0)
                
                if (inter.clicked_button.label.lower() == "back"):
                    current_page -= 1
                elif (inter.clicked_button.label.lower() == "next"):
                    current_page += 1
                elif (inter.clicked_button.label.lower() == "stop"):
                    await help_msg.edit(components=[])
                    break

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
                    label = "Stop",
                    custom_id = "stop",
                    style = ButtonStyle.red
                ),
                    Button(
                    label = "Next",
                    custom_id = "ahead",
                    style = ButtonStyle.blurple
                ))
                await inter.reply(type=7, embed=pages[current_page], components=[page_btn])

            except asyncio.TimeoutError:
                await help_msg.edit(components=[])
                break
            except:
                break
    
    # Pages Help
    @help.command()
    async def moderation(self, ctx):
        await ctx.send(embed=mod_page)

    @help.command()
    async def utility(self, ctx):
        await ctx.send(embed=utils_page)

    @help.command()
    async def fun(self, ctx):
        await ctx.send(embed=fun_page)

    @help.command()
    async def bot(self, ctx):
        await ctx.send(embed=bot_page)

    @help.command()
    async def giveaway(self, ctx):
        await ctx.send(embed=gaway_page)

    @help.command()
    async def music(self, ctx):
        await ctx.send(embed=music_page)
        
    # Moderation Command
    @help.command()
    async def kick(self, ctx):

        em = discord.Embed(title="Kick",
                          description="Kicks a member from the server!",
                          colour=discord.Color.random())

        em.add_field(name="**Syntax**", value="#kick <member> [reason]", inline=False)
        em.add_field(name="**Required Perms**", value="Kick Member", inline=False)
        em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

        await ctx.send(embed=em)


    @help.command()
    async def ban(self, ctx):

        em = discord.Embed(title="Ban",
                          description="Bans a member from the server!",
                          colour=discord.Color.random())

        em.add_field(name="**Syntax**", value="#ban <member> [reason]", inline=False)
        em.add_field(name="**Required Perms**", value="Ban Member", inline=False)
        em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

        await ctx.send(embed=em)


    @help.command()
    async def mute(self, ctx):

        em = discord.Embed(title="Mute",
                          description="Mutes a member!",
                          colour=discord.Color.random())

        em.add_field(name="**Syntax**", value="#mute <member> [time: (s|m|h|d)]", inline=False)
        em.add_field(name="**Required Perms**", value="Manage Roles", inline=False)
        em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

        await ctx.send(embed=em)


    @help.command()
    async def unban(self, ctx):

        em = discord.Embed(title="Unban",
                          description="Unbans a member from the server!",
                          colour=discord.Color.random())

        em.add_field(name="**Syntax**", value="#unban <member_id>", inline=False)
        em.add_field(name="**Required Perms**", value="Ban Member", inline=False)
        em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

        await ctx.send(embed=em)

    @help.command()
    async def unmute(self, ctx):

        em = discord.Embed(title="Unmute",
                          description="Unmutes a member!",
                          colour=discord.Color.random())

        em.add_field(name="**Syntax**", value="#unmute <member>", inline=False)
        em.add_field(name="**Required Perms**", value="Manage Roles", inline=False)
        em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

        await ctx.send(embed=em)

    # Bot Commands
    @help.command()
    async def ping(self, ctx):

        em = discord.Embed(title="Ping", description="Displays the current latency!", colour=discord.Color.random())

        em.add_field(name="**Syntax**", value="#ping", inline=False)
        em.add_field(name="**Aliases**", value="`pong`", inline=False)
        em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

        await ctx.send(embed=em)
    
    @help.command()
    async def invite(self, ctx):
        em = discord.Embed(title="Invite Command", description="Invite This Bot To Your Server!", color=discord.Color.random())
        
        em.add_field(name="**Syntax**", value="#invite", inline=False)
        em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

        await ctx.send(embed=em)

    @help.command()
    async def uptime(self, ctx):
        em = discord.Embed(title="Uptime Command", description="Check the bots uptime!", color=discord.Color.random())
        
        em.add_field(name="**Syntax**", value="#uptime", inline=False)
        em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

        await ctx.send(embed=em)
    
    @help.command()
    async def stats(self, ctx):
        em = discord.Embed(title="Stats Command", description="Get Stats Of The Bot!", color=discord.Color.random())
        
        em.add_field(name="**Syntax**", value="#stats", inline=False)
        em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

        await ctx.send(embed=em)

    # Utility Commands
    @help.command()
    async def purge(self, ctx):

        em = discord.Embed(title="Purge",
                           description="Deletes a number of messages from a channel!",
                           colour=discord.Color.random())

        em.add_field(name="**Syntax**", value="#purge <no_of_messages>", inline=False)
        em.add_field(name="**Required Perms**", value="Manage Messages", inline=False)
        em.add_field(name="**Aliases**", value="`clear`", inline=False)
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
        em.add_field(name="**Required Perms**", value="Manage Guild", inline=False)
        em.add_field(name="**Aliases**", value="`setprefix`, `changeprefix`", inline=False)
        em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

        await ctx.send(embed=em)

    @help.command(aliases=['resetprefix', 'delprefix'])
    async def deleteprefix(self, ctx):
        em = discord.Embed(title="Reset Prefix Command", description="Changes Back The Server Prefix To Default `#`!", color=discord.Color.random())
        
        em.add_field(name="**Syntax**", value="#deleteprefix", inline=False)
        em.add_field(name="**Required Perms**", value="Manage Guild", inline=False)
        em.add_field(name="**Aliases**", value="`resetprefix`, `delprefix`", inline=False)
        em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

        await ctx.send(embed=em)

    @help.command(aliases=['dm'])
    async def mail(self, ctx):
        em = discord.Embed(title="Mail Command", description="Mail The User Using Meow Mail Service!", color=discord.Color.blurple())
        
        em.add_field(name="**Syntax**", value="#mail <user> <your_message>", inline=False)
        em.add_field(name="**Required Perms**", value="Manage Guild", inline=False)
        em.add_field(name="**Aliases**", value="`dm`", inline=False)
        em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

        await ctx.send(embed=em)

    # Fun Commands
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
        
        em.add_field(name="**Syntax**", value="#gstart <time> [channel] <prize>", inline=False)
        em.add_field(name="**Required Perms**", value="Manage Guild", inline=False)
        em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

        await ctx.send(embed=em)

    @help.command()
    async def gcreate(self, ctx):
        em = discord.Embed(title="Creates Command", description="Creates A Giveaway!\nInteractive!", color=discord.Color.random())
        
        em.add_field(name="**Syntax**", value="#gcreate", inline=False)
        em.add_field(name="**Required Perms**", value="Manage Guild", inline=False)
        em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

        await ctx.send(embed=em)
    
    @help.command()
    async def greroll(self, ctx):
        em = discord.Embed(title="Reroll Giveaway Command", description="Rerolls A Giveaway To Get A New Winner!", color=discord.Color.random())
        
        em.add_field(name="**Syntax**", value="#greroll <channel> <msg_id>", inline=False)
        em.add_field(name="**Required Perms**", value="Manage Guild", inline=False)
        em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

        await ctx.send(embed=em)

    @help.command()
    async def gend(self, ctx):
        em = discord.Embed(title="End Giveaway Command", description="End A Giveaway To Get A Winner!", color=discord.Color.random())
        
        em.add_field(name="**Syntax**", value="#gend <msg_id>", inline=False)
        em.add_field(name="**Required Perms**", value="Manage Guild", inline=False)
        em.set_footer(text="<argument> : This means the argument is required.\n [argument] : This means the argument is optional.")

        await ctx.send(embed=em)

def setup(client):
    client.add_cog(Help(client))