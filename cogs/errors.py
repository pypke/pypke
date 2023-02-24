import logging
import random
import string

import discord
from discord.ext import commands


class ErrorsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass  # Don't do anything if command is not found

        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.author.send(f"{ctx.command} can not be used in private messages.")

        elif isinstance(error, commands.MissingPermissions):
            missing_perms = ", ".join(error.missing_permissions)
            await ctx.send(f"You are missing the following permissions to run this command: {missing_perms}", delete_after=5)
            await ctx.message.delete()

        elif isinstance(error, commands.BotMissingPermissions):
            missing_perms = ", ".join(error.missing_permissions)
            await ctx.send(f"The bot doesn't have the following permissions: {missing_perms}", delete_after=5)
            await ctx.message.delete()

        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"You are missing a required argument: `{error.param.name}`")
            # Uncomment the following line if you want to automatically invoke the help command for the current command
            # await ctx.invoke(self.bot.get_command("help"), command_or_module=ctx.command.qualified_name)

        elif isinstance(error, commands.NotOwner):
            pass  # Don't do anything if user is not the owner of the bot

        elif isinstance(error, commands.UserNotFound):
            await ctx.send(f'The user "{error.argument}" does not exist. Please try again!')

        elif isinstance(error, commands.MemberNotFound):
            await ctx.send(f'The member "{error.argument}" is not in this server or does not exist. Please try again!')

        elif isinstance(error, commands.ChannelNotFound):
            await ctx.send(f'The channel "{error.argument}" does not exist. Please try again!')

        elif isinstance(error, commands.BadArgument):
            await ctx.send(str(error))

        elif isinstance(error, commands.BadUnionArgument):
            await ctx.send(str(error))

        elif isinstance(error, commands.MaxConcurrencyReached):
            await ctx.send(f"This command is already in progress.", delete_after=5)

        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"This command is on cooldown for `{round(error.retry_after)}` seconds.")

        elif isinstance(error, commands.CommandInvokeError):
            error_key = "".join(random.choices(string.hexdigits, k=10))
            embed = discord.Embed(
                title="Error Occurred",
                description=f"An error occurred while executing the command. Please consider reporting the error ID to the developers on the [support server](https://dsc.gg/pypke-support).",
                timestamp=discord.utils.utcnow(),
                color=self.bot.colors["og_blurple"],
            )
            embed.add_field(name="Error Type", value=error.__class__.__name__)
            embed.add_field(name="Error ID", value=f"`{error_key}`")
            await ctx.send(embed=embed, delete_after=30)
            self.bot.logger.log(
                logging.ERROR,
                f"[Id: {error_key}] {ctx.command.qualified_name} -> {str(error)}",
            )
            raise error


def setup(bot):
    bot.add_cog(ErrorsCog(bot))