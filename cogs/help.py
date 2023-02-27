import math
from typing import Optional

import discord
from discord.ext import commands
from utils.pagination import Pagination


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
            title=cog.qualified_name + " Module",
            description=f"{cog.description if cog.description else ''}\n\n`{ctx.prefix}help <command>` for extended information on a command.\n",
            color=self.client.colors["og_blurple"],
        )
        commands = []

        for command in cog.get_commands():
            if not command.hidden:
                commands.append(f"`{command.qualified_name}`")

        embed.add_field(
            name="Commands",
            value=", ".join(command for command in commands),
            inline=False,
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
            subcommands = []
            for sub_cmd in cmd.walk_commands():
                if not sub_cmd.hidden:
                    subcommands.append(sub_cmd)
                    commands.append(
                        f"`{sub_cmd.qualified_name} {sub_cmd.signature}`\n{sub_cmd.description if sub_cmd.description else 'No help provided'}"
                    )

            # I Know there is surely a better way to do this but Idfk it.
            per_page = 3
            pages = math.ceil(len(commands) / per_page)
            page = 1
            embeds = []
            while page <= pages:
                start = (page - 1) * per_page
                end = start + per_page
                for command in commands[start:end]:
                    embed = discord.Embed(
                        title=self.get_syntax(cmd),
                        description=cmd.description if cmd.description else "No help provided",
                        color=self.client.colors["og_blurple"],
                    )
                    embed.set_author(
                        name=f"Page {page}/{pages} ({len(commands) + 1} Commands)"
                    )
                    embed.set_footer(
                        text=f'Use "?help command" for more info on a command.')
                    for sub_cmd in subcommands[start:end]:
                        embed.add_field(
                            name=sub_cmd.qualified_name + " " + sub_cmd.signature,
                            value=sub_cmd.description
                            if sub_cmd.description
                            else "No help provided",
                            inline=False,
                        )

                embeds.append(embed)
                page += 1

            return embeds

        embed = discord.Embed(
            title=self.get_syntax(cmd),
            description=cmd.description if cmd.description else "No help provided",
            color=self.client.colors["og_blurple"],
        )
        return embed

    @commands.command(
        name="help",
        description="wdym you need a help for help command? idiot",
        aliases=["commands"],
    )
    @commands.guild_only()
    async def help_command(self, ctx, *, command_or_module: Optional[str]):
        if not command_or_module:
            cogs = [
                "Moderation",
                "Utility",
                "Giveaway",
                "Images",
                "Fun",
                "Bot",
                "Misc",
            ]

            first = discord.Embed(
                description=f"Use `{ctx.prefix}help <command|module>` for more info.",
                color=self.client.colors["og_blurple"],
            )
            first.set_author(name=self.client.user.name +
                             " Help", url="https://docs.pypke.tk")
            first.set_thumbnail(url=self.client.user.avatar.url)
            first.add_field(
                name="Info",
                value=f"Server Prefix: `{ctx.prefix}`\nTotal Commands: `{len(self.client.all_commands)}`",
            )
            first.add_field(
                name="Links",
                value="[Invite Me](https://discord.com/oauth2/authorize?client_id=823051772045819905&permissions=8&scope=bot%20applications.commands)\n"
                "[Vote Here](https://top.gg/bot/823051772045819905)\n"
                "[Documentation](https://docs.pypke.tk)\n",
            )

            pages = [first]
            for i, cog in enumerate(cogs):
                cog = self.client.get_cog(cog)
                embed = self.cog_help(ctx, cog)
                embed.set_footer(text=f"Page {i + 2}/{len(cogs) + 1}")
                pages.append(embed)

            return await Pagination.paginate(self, ctx, pages)

        modules_aliases = {"mod": "moderation",
                           "utils": "utility", "image": "images"}
        if command_or_module.lower() in modules_aliases:
            command_or_module = modules_aliases[command_or_module]

        _entity = command_or_module.capitalize()
        entity_type = self.command_or_cog(_entity)

        if entity_type == "cog":
            cog = self.client.get_cog(_entity)
            embed = self.cog_help(ctx, cog)
            if not embed:
                return await ctx.send("That module doesn't exist.")

        elif entity_type == "command":
            command = self.client.get_command(_entity)
            if command.hidden and ctx.author.id != 624572769484668938:
                return await ctx.send(
                    f'No command called "{command_or_module.lower()}" found.'
                )
            embed = self.command_help(ctx, command)

            if not embed:
                return await ctx.send(
                    f'No command called "{command_or_module.lower()}" found.'
                )

            if isinstance(embed, list):
                if len(embed) > 1:
                    return await Pagination.paginate(self, ctx, embed)
                else:
                    embed = embed[0]

        else:
            return await ctx.send(f'No command called "{command_or_module.lower()}" found.')
        await ctx.send(embed=embed)


def setup(client):
    client.add_cog(HelpCog(client))
