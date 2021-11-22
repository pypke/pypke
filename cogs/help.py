from datetime import datetime
from typing import Union, Optional
from utils.pagination import Pagination

import discord, random, asyncio
from discord.ext import commands
from dislash import ActionRow, Button, ButtonStyle

class HelpCog(commands.Cog):
    """HelpCog for all the help command stuff."""
    
    def __init__(self, client):
        self.client = client

    def command_or_cog(self, entity):
        """Is it a command or a cog?

        Args:
            entity (Entity Name): The command's or cog's name

        Raises:
            commands.CommandNotFound: The command with this name not found.

        Returns:
            Literal['cog', 'command'] | None: Returns if its a cog or command else None.
        """    
        entity = entity.capitalize()    
        cog = self.client.get_cog(entity)
        if cog:
            return "cog"
        else:
            entity = entity.lower()
            try:
                command = self.client.get_command(entity)
                if command:
                    return "command"
                else:
                    raise commands.CommandNotFound
            except Exception:
                return None

    def get_syntax(self, command: commands.Command):
        """Gives the command syntax.

        Args:
            command (commands.Command): The command object.

        Returns:
            syntax (str): The command usage syntax.
        """        
        aliases = "|".join(command.aliases)
        cmd_invoke = f"[{command.name}|{aliases}]" if command.aliases else command.name

        full_invoke = command.qualified_name.replace(command.name, "")

        signature = f"{full_invoke}{cmd_invoke} {command.signature}"
        return signature

    def cog_help(self, ctx, cog):
        """Gives the embed with given cog's help.

        Args:
            ctx (commands.Context): The command's context.
            cog (commands.Cog): The cog object.

        Returns:
            embed: The embed with cog's help.
        """        
        if len(cog.get_commands()) == 0:
            return None

        embed = discord.Embed(
            title=cog.qualified_name,
            description=f"Use `{ctx.prefix}help <command>` for extended information on a command.\n\n",
            color=0x2f3136
        )
        commands = []
        for command in cog.get_commands():
            if not command.hidden:
                commands.append(f"`{command.qualified_name}`")

        embed.add_field(
            name="Commands",
            value=", ".join(command for command in commands),
            inline=False
        )
        
        return embed

    def command_help(self, ctx, cmd):
        """Gives an embed with command's help.

        Args:
            ctx (commands.Context): The command's context.
            cmd (commands.Command): The command object.

        Returns:
            embed: The embed with command's help.
        """        
        commands = []       
        if hasattr(cmd, "walk_commands"):
            for sub_cmd in cmd.walk_commands():
                if not sub_cmd.hidden:
                    commands.append(f"`{sub_cmd.qualified_name} {sub_cmd.signature}`\n{sub_cmd.description if sub_cmd.description else 'No Help Provided'}")

            embed = discord.Embed(
                title=self.get_syntax(cmd),
                description=f"{cmd.description if cmd.description else 'No Help Provided'}\n\n" + "\n\n".join(commands),
                color=0x2f3136
            )
            return embed
        
        embed = discord.Embed(
            title=self.get_syntax(cmd),
            description=cmd.description if cmd.description else "No Help Provided",
            color=0x2f3136
        )
        return embed

    @commands.command(name="help", description="wdym you need a help for help command? idiot", aliases=['commands'])
    @commands.guild_only()
    async def help_command(self, ctx, *, command_or_module=None):     
        if not command_or_module:
            first = discord.Embed(
                description=f"• Server Prefix: `{ctx.prefix}`\n• [Support Server](https://discord.gg/mYXgu2NVzH) | [Invite Pypke](https://dsc.gg/pypke) | [Vote Here](https://top.gg/bot/823051772045819905/vote)\n• Use `{ctx.prefix}help <command-name | module-name>` for more info on that.",
                color=self.client.colors["orange"]
            )
            first.set_author(name=self.client.user.name, icon_url=self.client.user.avatar.url)
            first.set_thumbnail(url=self.client.user.avatar.url)
            first.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar.url)

            cogs = [
                "Moderation", "Utility", "Giveaway", "Music", "Fun", "Bot", "Misc"
            ]
            first.add_field(
                name="__Module__",
                value="• Moderation\n• Utility\n• Giveaway\n• Music\n• Fun\n• Bot\n• Misc"
            )
            pages = [first]
            for i, cog in enumerate(cogs):
                cog = self.client.get_cog(cog)
                embed = self.cog_help(ctx, cog)
                embed.set_footer(text=f"Page {i+2}/{len(cogs)+1}")
                pages.append(embed)

            return await Pagination.paginate(self, ctx, pages)

        _entity = command_or_module
        entity_type = self.command_or_cog(_entity)

        if entity_type == "cog":
            cog = self.client.get_cog(_entity)
            embed = self.cog_help(ctx, cog)
            if not embed:
                return await ctx.send("That module doesn't exist wdym?")

        elif entity_type == "command":
            command = self.client.get_command(_entity)
            embed = self.command_help(ctx, command)
            if not embed:
                raise commands.CommandNotFound
            
        else:
            return

        await ctx.send(embed=embed)

    # @commands.command(name="help", description="wdym you need a help for help command? idiot", aliases=['commands'])
    # @commands.guild_only()
    # async def help(self, ctx, *, command: str = None):
    #     # New Help Command Work In-Progress
    #     current = 0
    #     first_page = discord.Embed(
    #         title="Commands",
    #         description="Documentation is work in-progress. Take a look here\nhttps://docs.pypke.tk\n\nDo The Commands Below To View Specific Page.",
    #         color=self.client.randcolor,
    #         timestamp=datetime.now()
    #     )
    #     first_page.add_field(name="Moderation Commands", value="`#help moderation`")
    #     first_page.add_field(name="Utility Commands", value="`#help utility`")
    #     first_page.add_field(name="Fun Commands", value="`#help fun`")
    #     first_page.add_field(name="Bot Commands", value="`#help bot`")
    #     first_page.add_field(name="Giveaway Commands", value="`#help giveaway`")
    #     first_page.add_field(name="Music Commands", value="`#help music`")

    #     mod = discord.Embed(
    #                              title="Moderation Commands",
    #                              description="Use The Buttons Below To Change Pages.\nUse `#help <command>` for extended information on a command.\n\n:gear: Moderation Commands\n• `kick` - Kicks the user from the server.\n• `ban` - Bans the user from the server.\n• `unban` - Unbans the user from the server.\n• `mute` - Mute the member.\n• `ban` - Unmute the member.",
    #                              color=random.choice(self.client.color_list),
    #                              timestamp=datetime.now()
    #                             )

    #     utility = discord.Embed(
    #                              title="Utilty Commands",
    #                              description="Use The Buttons Below To Change Pages.\nUse `#help <command>` for extended information on a command.\n\n:tools: Utility Commands\n• `purge` - Deletes amount of messages from the used channel.\n• `avatar` - Get your's or anyone else's avatar.\n• `whois` - Shows info about the member.\n• `prefix` - Set a custom prefix for your server.\n• `resetprefix` - Reset the prefix back to '#' for your server.\n• `mail` - Mails a member for you.",
    #                              color=random.choice(self.client.color_list),
    #                              timestamp=datetime.now()
    #                             )
                                
    #     fun = discord.Embed(
    #                              title="Fun Commands",
    #                              description=f"Use The Buttons Below To Change Pages.\nUse `#help <command>` for extended information on a command.\n\n:smile: Fun Commands\n• `8ball` - Question the 8ball and it shall answer.\n• `joke` - Sends you a joke.\n• `pokedex` - Search a pokemon's dex entry.\n• `pat` - Pat a user.\n• `meme` - See memes from r/memes.\n• `dankmeme` - See memes from r/dankmemes.\n• `kill` - Kill a user with words.\n• `cat` - Shows a cat image.\n• `dog` - Shows a dog image.",
    #                              color=random.choice(self.client.color_list),
    #                              timestamp=datetime.now()
    #                             )

    #     bot = discord.Embed(
    #                              title="Bot Commands",
    #                              description=f"Use The Buttons Below To Change Pages.\nUse `#help <command>` for extended information on a command.\n\n:robot: Bot Commands\n• `ping` - Ping to check the bot's latency.\n• `stats` - Check the bot's stats.\n• `uptime` - Check the bot's uptime.\n• `invite` - Invite me to your server.",
    #                              color=random.choice(self.client.color_list),
    #                              timestamp=datetime.now()
    #                             )

    #     giveaway = discord.Embed(
    #                              title="Giveaway Commands",
    #                              description=f"Use The Buttons Below To Change Pages.\nUse `#help <command>` for extended information on a command.\n\n:tada: Giveaway Commands\n• `gstart` - Start a giveaway quickly.\n• `gcreate` - Start a giveaway but interactively.\n• `greroll` - Reroll a giveaway winner.\n• `gend` - End a giveaway.",
    #                              color=random.choice(self.client.color_list),
    #                              timestamp=datetime.now()
    #                             )

    #     music = discord.Embed(
    #                              title="Music Commands",
    #                              description=f"Use The Buttons Below To Change Pages.\nUse `#help <command>` for extended information on a command.\n\n:musical_note: Music Commands\n• `join` - Make the bot join your vc.\n• `play` - Play a song.\n• `skip` - Skips current playing song.\n• `queue` - Shows you the songs currenly in queue.\n• `volume` - Change the bot's volume.\n• `stop` - Make the bot leave the vc.",
    #                              color=random.choice(self.client.color_list),
    #                              timestamp=datetime.now()
    #                             )
        
    #     pages = [first_page, mod, utility, bot, fun, giveaway, music]

    #     # if command != None and command.lower() in pages:
    #     #     await ctx.send(embed=command.lower())
    #     try:
    #         cmd = self.client.get_command(command)
    #         if not cmd:
    #             raise commands.CommandNotFound
    #             return
            
    #         cmd_embed = discord.Embed(
    #             title=f"{cmd.qualified_name} {cmd.signature}",
    #             description=cmd.description if cmd.description else "No Help Provided",
    #             color=self.client.color
    #         )
    #         return await ctx.send(embed=cmd_embed)
    #     except Exception:
    #         pass

    #     page_btn = ActionRow(
    #         Button(
    #                 label = "Back",
    #                 custom_id = "back",
    #                 style = ButtonStyle.blurple
    #             ),
    #             Button(
    #                 label = f"Page {int(pages.index(pages[current])) + 1}/{len(pages)}",
    #                 custom_id = "cur",
    #                 style = ButtonStyle.gray,
    #                 disabled = True
    #             ),
    #                 Button(
    #                 label = "Stop",
    #                 custom_id = "stop",
    #                 style = ButtonStyle.red
    #             ),
    #             Button(
    #                 label = "Next",
    #                 custom_id = "ahead",
    #                 style = ButtonStyle.blurple
    #             ))
    #     help_msg = await ctx.send(embed=pages[current], components=[page_btn])
    #     while True:
    #         # Try and except blocks to catch timeout and break
    #         def check(inter):
    #             return inter.message.id == help_msg.id and inter.author.id == ctx.author.id
                
    #         try:
    #             inter = await ctx.wait_for_button_click(check=check, timeout=20.0)
                
    #             if (inter.clicked_button.label.lower() == "back"):
    #                 current -= 1
    #             elif (inter.clicked_button.label.lower() == "next"):
    #                 current += 1
    #             elif (inter.clicked_button.label.lower() == "stop"):
    #                 await help_msg.edit(components=[])
    #                 break

    #             # If its out of index, go back to start / end
    #             if current == len(pages):
    #                 current = 0
    #             elif current < 0:
    #                 current = len(pages) - 1

    #             # Redefination For Page Number
    #             page_btn = ActionRow(
    #                 Button(
    #                 label = "Back",
    #                 custom_id = "back",
    #                 style = ButtonStyle.blurple
    #             ),
    #                 Button(
    #                 label = f"Page {int(pages.index(pages[current])) + 1}/{len(pages)}",
    #                 custom_id = "cur",
    #                 style = ButtonStyle.gray,
    #                 disabled = True
    #             ),
    #                 Button(
    #                 label = "Stop",
    #                 custom_id = "stop",
    #                 style = ButtonStyle.red
    #             ),
    #                 Button(
    #                 label = "Next",
    #                 custom_id = "ahead",
    #                 style = ButtonStyle.blurple
    #             ))
    #             await inter.reply(type=7, embed=pages[current], components=[page_btn])

    #         except asyncio.TimeoutError:
    #             await help_msg.edit(components=[])
    #             break
    #         except Exception:
    #             break

def setup(client):
    client.add_cog(HelpCog(client))