import discord
from discord.ext import commands

import asyncio
import itertools
import sys
import traceback
import random
from async_timeout import timeout
from functools import partial
from youtube_dl import YoutubeDL, utils

ytdlopts = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # ipv6 addresses cause issues sometimes
}

ffmpegopts = {
    'before_options': '-nostdin',
    'options': '-vn'
}

ytdl = YoutubeDL(ytdlopts)
utils.bug_reports_message = lambda: ''

class VoiceConnectionError(commands.CommandError):
    """Custom Exception class for connection errors."""


class InvalidVoiceChannel(VoiceConnectionError):
    """Exception for cases of invalid Voice Channels."""


class YTDLSource(discord.PCMVolumeTransformer):

    def __init__(self, source, *, data, requester):
        super().__init__(source)
        self.requester = requester

        self.title = data.get('title')
        self.web_url = data.get('webpage_url')

        # YTDL info dicts (data) have other useful information you might want
        # https://github.com/rg3/youtube-dl/blob/master/README.md

    def __getitem__(self, item: str):
        """Allows us to access attributes similar to a dict.
        This is only useful when you are NOT downloading.
        """
        return self.__getattribute__(item)

    @classmethod
    async def create_source(cls, ctx, search: str, *, loop, download=False):
        loop = loop or asyncio.get_event_loop()

        to_run = partial(ytdl.extract_info, url=search, download=download)
        data = await loop.run_in_executor(None, to_run)

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        await ctx.send(f'Added `{data["title"]}` to Queue!')

        if download:
            source = ytdl.prepare_filename(data)
        else:
            return {'webpage_url': data['webpage_url'], 'requester': ctx.author, 'title': data['title']}

        return cls(discord.FFmpegPCMAudio(source), data=data, requester=ctx.author)

    @classmethod
    async def regather_stream(cls, data, *, loop):
        """Used for preparing a stream, instead of downloading.
        Since Youtube Streaming links expire."""
        loop = loop or asyncio.get_event_loop()
        requester = data['requester']

        to_run = partial(ytdl.extract_info, url=data['webpage_url'], download=False)
        data = await loop.run_in_executor(None, to_run)

        return cls(discord.FFmpegPCMAudio(data['url']), data=data, requester=requester)


class MusicPlayer:
    """A class which is assigned to each guild using the client for Music.
    This class implements a queue and loop, which allows for different guilds to listen to different playlists
    simultaneously.
    When the client disconnects from the Voice it's instance will be destroyed.
    """

    __slots__ = ('client', '_guild', '_channel', '_cog', 'queue', 'next', 'loop', 'current', 'np', 'volume')

    def __init__(self, ctx, client):
        self.client = client
        self._guild = ctx.guild
        self._channel = ctx.channel
        self._cog = ctx.cog

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()
        self.loop = False

        self.np = None  # Now playing message
        self.volume = 1
        self.current = None

        self.client.loop.create_task(self.player_loop())

    async def player_loop(self):
        """Our main player loop."""
        await self.client.wait_until_ready()

        while not self.client.is_closed():
            self.next.clear()
            
            if not self.loop:
                try:
                    # Wait for the next song. If we timeout cancel the player and disconnect...
                    async with timeout(300):  # 5 minutes...
                        source = await self.queue.get()
                except asyncio.TimeoutError:
                    return self.destroy(self._guild)
                except discord.errors.ClientException:
                    return

            if not isinstance(source, YTDLSource):
                # Source was probably a stream (not downloaded)
                # So we should regather to prevent stream expiration
                try:
                    source = await YTDLSource.regather_stream(source, loop=self.client.loop)
                except Exception:
                    await self._channel.send(f'That song can\' be played..')
                    continue
            
            if self.loop == True:
                source.volume = self.volume
                self.current = source
                # self._guild.voice_client.play(source, after=lambda _: self.client.loop.call_soon_threadsafe(self.next.set))
                self.np = await self._channel.send(f'**Playing:** :notes:`{source.title}` - Now! ') #Added by `{source.requester}`'
                return
            else:
                pass
            source.volume = self.volume
            self.current = source
            self._guild.voice_client.play(source, after=lambda _: self.client.loop.call_soon_threadsafe(self.next.set))
            self.np = await self._channel.send(f'**Playing:** :notes:`{source.title}` - Now! ') #Added by `{source.requester}`'
            await self.next.wait()

            # Make sure the FFmpeg process is cleaned up.
            source.cleanup()
            self.current = None

            try:
                # We are no longer playing this song...
                await self.np.delete()
            except discord.HTTPException:
                pass

    def destroy(self, guild):
        """Disconnect and cleanup the player."""
        return self.client.loop.create_task(self._cog.cleanup(guild))


class NewMusic(commands.Cog):
    """Music related commands."""

    __slots__ = ('client', 'players')

    def __init__(self, client):
        self.client = client
        self.players = {}

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass

    async def __local_check(self, ctx):
        """A local check which applies to all commands in this cog."""
        if not ctx.guild:
            raise commands.NoPrivateMessage
        return True

    async def __error(self, ctx, error):
        """A local error handler for all errors arising from commands in this cog."""
        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send('This command can\'t be used in DMs.')
            except discord.HTTPException:
                pass
        elif isinstance(error, InvalidVoiceChannel):
            await ctx.send('Error connecting to Voice Channel. '
                           'Please make sure that you\'re in a vc.')

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    def get_player(self, ctx):
        """Retrieve the guild player, or generate one."""
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx, self.client)
            self.players[ctx.guild.id] = player

        return player

    @commands.command(name='connect', aliases=['join'])
    async def connect_(self, ctx, *, channel: discord.VoiceChannel=None):
        """Connect to voice.
        Parameters
        ------------
        channel: discord.VoiceChannel [Optional]
            The channel to connect to. If a channel is not specified, an attempt to join the voice channel you are in
            will be made.
        This command also handles moving the client to different channels.
        """
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                raise InvalidVoiceChannel("You're not connected to a voice channel.")

        vc = ctx.voice_client

        if vc:
            if vc.channel.id == channel.id:
                return
            try:
                await vc.move_to(channel)
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Error connecting to {channel.mention}')
        else:
            try:
                await channel.connect()
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Error connecting to {channel.mention}')

        await ctx.send(f'**Connected to:** {channel.mention}!!')

    @commands.command(name='play', aliases=['p'])
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def play_(self, ctx, *, search: str):
        """Request a song and add it to the queue.
        This command attempts to join a valid voice channel if the client is not already in one.
        Uses YTDL to automatically search and retrieve a song.
        Parameters
        ------------
        search: str [Required]
            The song to search and retrieve using YTDL. This could be a simple search, an ID or URL.
        """
        await ctx.trigger_typing()

        vc = ctx.voice_client

        if not vc:
            await ctx.invoke(self.connect_)

        player = self.get_player(ctx)

        # If download is False, source will be a dict which will be used later to regather the stream.
        # If download is True, source will be a discord.FFmpegPCMAudio with a VolumeTransformer.
        source = await YTDLSource.create_source(ctx, search, loop=self.client.loop, download=False)

        await player.queue.put(source)

    @commands.command(name='pause')
    async def pause_(self, ctx):
        """Pause the currently playing song."""
        vc = ctx.voice_client

        if not vc or not vc.is_playing():
            return await ctx.send('No song is currently playing!')
        elif vc.is_paused():
            return

        vc.pause()
        await ctx.send(f'Paused!')

    @commands.command(name='resume')
    async def resume_(self, ctx):
        """Resume the currently paused song."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('No song is currently playing!')
        elif not vc.is_paused():
            return

        vc.resume()
        await ctx.send(f'Resumed!')

    @commands.command(name='skip', aliases=['fs'])
    async def skip_(self, ctx):
        """Skip the song."""
        vc = ctx.voice_client
        if ctx.author != vc.source.requester:
            if ctx.channel.permissions_for(ctx.author).administrator or ctx.channel.permissions_for(ctx.author).manage_guild:
                pass
            else:
                return await ctx.send(f'Only song requester i.e. {vc.source.requester} or admin can skip this song!!')

        if not vc or not vc.is_connected():
            return await ctx.send('No Song is currently playing!')

        if vc.is_paused():
            pass
        elif not vc.is_playing():
            return

        vc.stop()
        await ctx.send(f'Skipped By {ctx.author}')

    # @commands.group(name='loop', invoke_without_command=True)
    # async def loop_(self, ctx):
    #     """Loop Group Command"""
    #     player = self.get_player(ctx)
    #     if player.loop == True:
    #         player.loop = False
    #         await ctx.send("Looping stopped!")
    #     else:
    #         player.loop = True
    #         await ctx.send("Looping this Song, Use `#loop` top stop!")
        

    # @loop_.command(name='queue', aliases=['all'])
    # async def all_(self, ctx):
    #     """Loop the whole queue."""
    #     vc = ctx.voice_client
    #     if not vc or not vc.is_connected():
    #         return await ctx.send('No Song is currently playing!')
        
    #     self.loop = True
    #     await ctx.send("Looping the Queue, Use `#loop` top stop!")

    @commands.command(name='queue', aliases=['q', 'playlist'])
    async def queue_(self, ctx):
        """Retrieve a basic queue of upcoming songs."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('Bot not connected to voice channel!')

        player = self.get_player(ctx)
        if player.queue.empty():
            return await ctx.send('Queue is empty. Add song by using `#play <song-name>`.')

        # Grab up to 5 entries from the queue...
        upcoming = list(itertools.islice(player.queue._queue, 0, 10))
        i = 0
        queue_list = ""
        for song in upcoming:
            i += 1
            queue_list = queue_list + ''.join(f'**[{i}].** `{song["title"]}`\n')
        embed = discord.Embed(title=f'Queue | {len(upcoming)} Songs:', description=queue_list, color=random.choice(self.client.color_list))

        await ctx.send(embed=embed)

    @commands.command(name='now_playing', aliases=['np', 'current', 'currentsong', 'playing'])
    async def now_playing_(self, ctx):
        """Display information about the currently playing song."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('Bot not connected to voice channel!')

        player = self.get_player(ctx)
        if not player.current:
            return await ctx.send('No song currently playing!')

        try:
            # Remove our previous now_playing message.
            await self.np.delete()
        except discord.HTTPException:
            pass

        player.np = await ctx.send(f'**Now Playing:** `{vc.source.title}`!')

    @commands.command(name='volume', aliases=['vol'])
    @commands.cooldown(1, 3, commands.BucketType.guild)
    async def volume_(self, ctx, *, vol: float):
        """Change the player volume.
        Parameters
        ------------
        volume: float or int [Required]
            The volume to set the player to in percentage. This must be between 1 and 200.
        """
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently connected to voice!')

        if not 0 < vol < 201:
            return await ctx.send('Please enter a value between 1 and 200.')

        player = self.get_player(ctx)

        if vc.source:
            vc.source.volume = vol / 100

        player.volume = vol / 100
        await ctx.send(f'Volume changed to **{vol}%** by {ctx.author}!')

    @commands.command(name='stop')
    async def stop_(self, ctx):
        """Stop the currently playing song and destroy the player.
        !Warning!
            This will destroy the player assigned to your guild, also deleting any queued songs and settings.
        """
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently playing anything!')

        await self.cleanup(ctx.guild)


def setup(client):
    client.add_cog(NewMusic(client))