import discord
import dislash
from discord.ext import commands
from thefuzz import fuzz

class Errors(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            cmd_list = self.client.all_commands
            i = 0
            msg = "That's not a valid command! Do `#help` for the list of commands.\nDid you meant one of these?\n"
            for cmd in cmd_list:
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
                await ctx.send(content="That's not a valid command! Do `#help` for the list of commands.")

        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("You can't do that?.", delete_after=5)
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(f"Bot doesn't have required permission to execute `#{ctx.command.qualified_name}` command.", delete_after=5)
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Please enter the required argument!")
        elif isinstance(error, commands.NotOwner):
            await ctx.send("Only Owner Of The Bot Can Use This Command!!")
        elif isinstance(error, commands.UserNotFound):
            await ctx.send("User With That Name Not Found. Try Again!")
        elif isinstance(error, commands.MemberNotFound):
            await ctx.send("Member With That Name Not Found. Try Again!")
        elif isinstance(error, commands.ChannelNotFound):
            await ctx.send("Channel Not Found. Try Again!")
        elif isinstance(error, commands.CommandOnCooldown):
            time = round(ctx.command.get_cooldown_retry_after(ctx))
            await ctx.send(f"Chill! This Command Is On Cooldown For `{time}` seconds.")
        elif isinstance(error, RuntimeWarning):
            return
        elif isinstance(error, commands.ExtensionNotLoaded):
            return
        elif isinstance(error, commands.ExtensionAlreadyLoaded):
            return
        elif isinstance(error, commands.ExtensionNotFound):
            return
        elif isinstance(error, commands.CommandInvokeError):
            if ctx.channel.id == 887258899726606336:
                await ctx.send(f"Oops Looks Like Something Went Wrong!!\nDetails:-`{error}`", delete_after=5)
                raise error
            else:
                raise error
        else:
            raise error
            
def setup(client):
    client.add_cog(Errors(client))