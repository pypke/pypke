import re
from discord.ext import commands

# Time Variables
time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"s": 1, "m": 60, "h": 3600, "d": 86400}


class TimeConverter(commands.Converter):
    """TimeConverter Class

    Attributes:
      - convert: The converter itself.
    """
    async def convert(self, ctx, argument):
        """Converts the value i.e. "1h 32m" to secs.

        Args:
            ctx (commands.Context): The command context.
            argument (argument): The value to convert to seconds.

        Raises:
            commands.BadArgument: The value is invalid, (s|m|h|d) are valid keys.
            commands.BadArgument: The key is not a number.

        Returns:
            seconds: No. of seconds.
        """
        args = argument.lower()
        matches = re.findall(time_regex, args)
        time = 0
        for key, value in matches:
            try:
                time += time_dict[value] * float(key)
            except KeyError:
                raise commands.BadArgument(
                    f"{value} is an invalid time key! s|m|h|d are valid arguments")
            except ValueError:
                raise commands.BadArgument(f"{key} is not a number!")
        return round(time)


class TimeHumanizer:
    def convert(self, *, time):
        if time <= 0:
            raise commands.BadArgument(f"Time cannot be negative.")

        minutes, seconds = divmod(time, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        duration = ""

        if days:
            duration = duration + f"{days} day(s) "
        if hours:
            duration = duration + f"{hours} hour(s) "
        if minutes:
            duration = duration + f"{minutes} minute(s) "
        if seconds:
            duration = duration + f"{seconds} second(s) "

        return duration
