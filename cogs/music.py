import asyncio
import discord
import youtube_dl
import math

from discord.ext import commands

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ""


ytdl_format_options = {
    "format": "bestaudio/best",
    "outtmpl": "%(extractor)s-%(id)s-%(title)s.%(ext)s",
    "restrictfilenames": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "quiet": True,
    "no_warnings": True,
    "default_search": "auto",
    "source_address": "0.0.0.0",  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {"options": "-vn"}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=1):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get("title")
        self.url = data.get("url")

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(
            None, lambda: ytdl.extract_info(url, download=not stream)
        )

        if "entries" in data:
            # take first item from a playlist
            data = data["entries"][0]

        filename = data["url"] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.states = []

    @commands.command(aliases=['connect'])
    @commands.guild_only()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """Joins a voice channel"""

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()
        await ctx.send("Connected")

    @commands.command()
    @commands.guild_only()
    async def play(self, ctx, *, url):
        """Plays from a url (almost anything youtube_dl supports)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop)
            ctx.voice_client.play(
                player, after=lambda e: print(f"Player error: {e}") if e else None
            )

        await ctx.send(f"Now playing: `{player.title}`")

    @commands.command()
    @commands.guild_only()
    async def stream(self, ctx, *, url):
        """Streams from a url (same as yt, but doesn't predownload)"""

        async with ctx.typing():
            player = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
            ctx.voice_client.play(
                player, after=lambda e: print(f"Player error: {e}") if e else None
            )

        await ctx.send(f"Now playing: `{player.title}`")

    @commands.command(aliases=["resume", "p"])
    @commands.guild_only()
    async def pause(self, ctx):
        """Pauses any currently playing audio."""
        bot = ctx.guild.voice_client
        self._pause_audio(bot)

    def _pause_audio(self, bot):
        if bot.is_paused():
            bot.resume()
        else:
            bot.pause()

    @commands.command()
    @commands.guild_only()
    async def volume(self, ctx, volume: int):
        """Change the volume of currently playing audio (values 0-250)."""
        state = self.get_state(ctx.guild)

        if volume < 0:
            volume = 0

        max_vol = 250
        if max_vol > -1:            
            if volume > max_vol:
                volume = max_vol

        client = ctx.guild.voice_client

        state.volume = float(volume) / 100.0
        client.source.volume = state.volume
        await ctx.send(f"Volume Set To **{volume}%**")

    @commands.command(aliases=['disconnect'])
    @commands.guild_only()
    async def stop(self, ctx):
        """Stops and disconnects the bot from voice"""

        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected")

    @commands.command(aliases=['fs'])
    @commands.guild_only()
    async def skip(self, ctx):
        """Skips the currently playing song, or votes to skip it."""
        state = self.get_state(ctx.guild)
        client = ctx.guild.voice_client
        if ctx.channel.permissions_for(
                ctx.author).administrator or state.is_requester(ctx.author):
            # immediately skip if requester or admin
            client.stop()
        else:
            channel = client.channel
            self._vote_skip(channel, ctx.author)
            # announce vote
            users_in_channel = len([member for member in channel.members if not member.bot])
            required_votes = math.ceil(0.5 * users_in_channel)
            await ctx.send(f"{ctx.author.mention} voted to skip ({len(state.skip_votes)}/{required_votes} votes)")

    @play.before_invoke
    @stream.before_invoke
    @volume.before_invoke
    @pause.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                await ctx.author.voice.channel.connect()
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
        elif ctx.voice_client.is_playing():
            ctx.voice_client.stop()

    def _vote_skip(self, channel, member):
        """Register a vote for `member` to skip the song playing."""
        channel.send(f"{member.name} votes to skip")
        state = self.get_state(channel.guild)
        state.skip_votes.add(member)
        users_in_channel = len([member for member in channel.members if not member.bot])
        if (float(len(state.skip_votes)) / users_in_channel) >= 0.5:
            channel.send(f"Enough votes, skipping...")
            channel.guild.voice_client.stop()

    def get_state(self, guild):
        """Gets the state for `guild`, creating it if it does not exist."""
        if guild.id in self.states:
            return self.states[guild.id]
        else:
            self.states[guild.id] = GuildState()
            return self.states[guild.id]

class GuildState:
    """Helper class managing per-guild state."""

    def __init__(self):
        self.volume = 1.0
        self.playlist = []
        self.skip_votes = set()
        self.now_playing = None

    def is_requester(self, user):
        return self.now_playing.requested_by == user
            
def setup(bot):
    bot.add_cog(Music(bot))