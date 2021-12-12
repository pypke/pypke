from thefuzz import fuzz

import discord
from discord.ext import commands
# from dislash import InteractionClient, ContextMenuInteraction, ApplicationCommandError


class ErrorsCog(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            cmd_list = self.client.all_commands
            i = 0
            msg = f"That's not a valid command! Do `{ctx.prefix}help` for the list of commands.\nDid you meant one of these?\n"
            for cmd in cmd_list:
                command = self.client.get_command(cmd)
                if not command.hidden == True:
                    ratio = fuzz.ratio(ctx.message.content, cmd)
                    if ratio >= 59:
                        i += 1
                        msg = msg + f"**{i}.** `{cmd}`\n"
                        if i >= 10:
                            break
                    else:
                        continue
            if i != 0:
                await ctx.send(msg, delete_after=7)
            else:
                pass

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
            except discord.HTTPException:
                pass

        elif isinstance(error, commands.MissingPermissions):
            try:
                await ctx.send(f"You are missing `{', '.join(error.missing_permissions)}` permission(s) to run this command.", delete_after=5)
                await ctx.message.delete()
            except Exception:
                pass

        elif isinstance(error, commands.BotMissingPermissions):
            try:
                await ctx.send(f"Bot doesn't have the required `{', '.join(error.missing_permissions)}` permission(s).", delete_after=5)
                await ctx.message.delete()
            except Exception:
                pass

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"`{error.param.name}` is a required argument that is missing.")
            # await ctx.invoke(self.client.get_command("help"), command_or_module=ctx.command.qualified_name)

        elif isinstance(error, commands.NotOwner):
            await ctx.send("Lol, You should be owner of the bot to do this.")

        elif isinstance(error, commands.UserNotFound):
            await ctx.send(f"User \"{error.argument}\" doesn't exist. Try again!")

        elif isinstance(error, commands.MemberNotFound):
            await ctx.send(f"Member \"{error.argument}\" is not in this server or doesn't exist. Try again!")

        elif isinstance(error, commands.ChannelNotFound):
            await ctx.send(f"Channel \"{error.argument}\" not found. Try again!")

        elif isinstance(error, commands.BadArgument):
            await ctx.send(str(error))

        elif isinstance(error, commands.BadUnionArgument):
            await ctx.send(str(error))

        elif isinstance(error, commands.MaxConcurrencyReached):
            await ctx.send(f"Woah, This command is already in progress.", delete_after=5)

        elif isinstance(error, commands.CommandOnCooldown):
            time = ctx.command.get_cooldown_retry_after(ctx)
            await ctx.send(f"Chill! This command is on cooldown for `{round(time)}` seconds.")

        elif isinstance(error, RuntimeWarning):
            return

        elif isinstance(error, commands.CommandInvokeError):
            await ctx.send(f"```diff\n{error.original}\n\n- Looks like an error occured, pls consider reporting it on support server.\n```")
            raise error
        else:
            raise error


def setup(client):
    client.add_cog(ErrorsCog(client))
