from thefuzz import fuzz

import discord
from discord.ext import commands
from dislash import InteractionClient, ContextMenuInteraction, ApplicationCommandError

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
                        msg = msg + f"**[{i}].** `{cmd}`\n"
                        if i >= 10:
                            break
                    else:
                        continue
            if i != 0:
                await ctx.send(content=msg)
            else:
                await ctx.send(content=f"That's not a valid command! Do `{ctx.prefix}help` for the list of commands.")

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
            except discord.HTTPException:
                pass

        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(f"You are missing permissions to run this command.", delete_after=5)

        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(f"Bot doesn't have required permission to execute `{ctx.prefix}{ctx.command.qualified_name}` command.", delete_after=5)

        elif isinstance(error, commands.MissingRequiredArgument):
            # await ctx.send(f"Please enter the required argument!")
            await ctx.invoke(self.client.get_command("help"), command=ctx.command.qualified_name)

        elif isinstance(error, commands.NotOwner):
            await ctx.send("Lol, You should be owner of the bot to do this.")

        elif isinstance(error, commands.UserNotFound):
            await ctx.send("User doesn't exist. Try again!")

        # elif isinstance(error, commands.MemberNotFound):
        #     await ctx.send("Member is not in this server or doesn't exist. Try again!")

        elif isinstance(error, commands.ChannelNotFound):
            await ctx.send("Channel not found. Try again!")

        elif isinstance(error, commands.BadArgument):
            await ctx.send(str(error))

        elif isinstance(error, commands.BadUnionArgument):
            await ctx.send(str(error))

        elif isinstance(error, commands.CommandOnCooldown):
            time = ctx.command.get_cooldown_retry_after(ctx)
            await ctx.send(f"Chill! This command is on cooldown for `{time}` seconds.")

        elif isinstance(error, RuntimeWarning):
            return
        elif isinstance(error, commands.ExtensionNotLoaded):
            return
        elif isinstance(error, commands.ExtensionAlreadyLoaded):
            return
        elif isinstance(error, commands.ExtensionNotFound):
            return
        elif isinstance(error, commands.CommandInvokeError):
            if ctx.guild.id == 850732056790827020:
                await ctx.send(f"```py\n{error}\n```")
                raise error
            else:
                raise error
        else:
            raise error

    @commands.Cog.listener()
    async def on_message_command_error(inter, error):
        if isinstance(error, ApplicationCommandError):
            await inter.respond(f"Failed to execute {inter.message_command} due to {error}.")
            raise error
            
def setup(client):
    client.add_cog(ErrorsCog(client))