import math
import re
import aiohttp
import asyncio
from typing import Optional
from urllib.parse import quote_plus

import lavalink
import discord
from discord.ext import commands

url_rx = re.compile('https?:\\/\\/(?:www\\.)?.+')

class LavalinkVoiceClient(discord.VoiceClient):
    def __init__(self, client: discord.Client, channel: discord.abc.Connectable):
        self.client = client
        self.channel = channel
        # ensure there exists a client already
        if hasattr(self.client, 'lavalink'):
            self.lavalink = self.client.lavalink
        else:
            self.client.lavalink = lavalink.Client(client.user.id)
            self.client.lavalink.add_node(
                    'localhost',
                    2333,
                    'youshallnotpass',
                    'us',
                    'default-node')
            self.lavalink = self.client.lavalink

    async def on_voice_server_update(self, data):
        # the data needs to be transformed before being handed down to
        # voice_update_handler
        lavalink_data = {
                't': 'VOICE_SERVER_UPDATE',
                'd': data
                }
        await self.lavalink.voice_update_handler(lavalink_data)

    async def on_voice_state_update(self, data):
        # the data needs to be transformed before being handed down to
        # voice_update_handler
        lavalink_data = {
                't': 'VOICE_STATE_UPDATE',
                'd': data
                }
        await self.lavalink.voice_update_handler(lavalink_data)

    async def connect(self, *, timeout: float, reconnect: bool) -> None:
        """
        Connect the client to the voice channel and create a player_manager
        if it doesn't exist yet.
        """
        # ensure there is a player_manager when creating a new voice_client
        self.lavalink.player_manager.create(guild_id=self.channel.guild.id)
        await self.channel.guild.change_voice_state(channel=self.channel)

    async def disconnect(self, *, force: bool) -> None:
        """
        Handles the disconnect.
        Cleans up running player and leaves the voice client.
        """
        player = self.lavalink.player_manager.get(self.channel.guild.id)

        # no need to disconnect if we are not connected
        if not force and not player.is_connected:
            return

        # None means disconnect
        await self.channel.guild.change_voice_state(channel=None)

        # update the channel_id of the player to None
        # this must be done because the on_voice_state_update that
        # would set channel_id to None doesn't get dispatched after the 
        # disconnect
        player.channel_id = None
        self.cleanup()

class Music(commands.Cog):
    """Module to jam with."""

    def __init__(self, client):
        self.client = client
        self.channel = {}
        self.playing = {}

        if not hasattr(client, 'lavalink'):
            client.lavalink = lavalink.Client(823051772045819905)
            client.lavalink.add_node('lava.link', 80, 'youshallnotpass', 'eu', 'default-node')  # Host, Port, Password, Region, Name
            print("Success, Nodes Connected!")

        client.lavalink.add_event_hook(self.track_hook)

    def cog_unload(self):
        self.client.lavalink._event_hooks.clear()

    async def cog_before_invoke(self, ctx):
        guild_check = ctx.guild is not None
        if guild_check:
            await self.ensure_voice(ctx)
        return guild_check

    async def ensure_voice(self, ctx):
        """ This check ensures that the client and command author are in the same voicechannel. """
        player = self.client.lavalink.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
        should_connect = ctx.command.name in ('play',)

        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send('Join a voicechannel first.')

        if not player.is_connected:
            if not should_connect:
                await ctx.send("Not connected.")

            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if not permissions.connect or not permissions.speak:  # Check user limit too?
                await ctx.send("I need `connect` and `speak` permissions.")

            player.store('channel', ctx.channel.id)
            try:
                await ctx.author.voice.channel.connect(cls=LavalinkVoiceClient)
            except:
                player.queue.clear()
                await player.stop()
                await ctx.guild.voice_client.disconnect(force=True)
        else:
            if int(player.channel_id) != ctx.author.voice.channel.id:
                await ctx.send("You need to be in my voice channel.")

    async def track_hook(self, event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            await asyncio.sleep(20)
            player = event.player
            if not player.is_playing:
                guild_id = int(event.player.guild_id)
                guild = self.client.get_guild(guild_id)
                channel = self.channel[str(guild_id)]
                await channel.send("Disconnected cause you didn't wanted to play anything.")
                await guild.voice_client.disconnect(force=True)

        elif isinstance(event, lavalink.TrackStartEvent):
            channel = self.channel[event.player.guild_id]
            msg = await channel.send(f"Playing :notes:`{event.track.title}` - Now!")
            self.playing[event.player.guild_id] = msg

        elif isinstance(event, lavalink.TrackEndEvent):
            msg = self.playing[event.player.guild_id]
            try:
                await msg.delete()
            except Exception:
                pass

        elif isinstance(event, lavalink.TrackExceptionEvent):
            channel = self.channel[event.player.guild_id]
            raise commands.CommandInvokeError(event.exception)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.bot and after.channel is None:
            await asyncio.sleep(30)
            if not [m for m in before.channel.members if not m.bot]:
                player = self.client.lavalink.player_manager.get(member.guild.id)
                try:
                    await player.stop()
                    await member.guild.voice_client.disconnect(force=True)
                except AttributeError:
                    pass

                channel = self.channel[member.guild.id]
                try:
                    await channel.send("Disconnected cause everyone left.")
                except Exception:
                    pass

    @commands.command(
        name="play",
        description="Searches and plays a song from a given query.",
        aliases=['p']
    )
    async def play(self, ctx, *, query: str):
        player = self.client.lavalink.player_manager.get(ctx.guild.id)

        query = query.strip('<>')

        if not url_rx.match(query):
            query = f'ytsearch:{query}'

        results = await player.node.get_tracks(query)

        if not results or not results['tracks']:
            return await ctx.send('Something is wrong, No tracks with that name found.')

        embed = discord.Embed(color=self.client.colors["og_blurple"])

        if results['loadType'] == 'PLAYLIST_LOADED':
            tracks = results['tracks']

            for track in tracks:
                player.add(requester=ctx.author.id, track=track)

            embed.title = 'Playlist Queued!'
            embed.description = f'{results["playlistInfo"]["name"]} - {len(tracks)} tracks'
        else:
            track = results['tracks'][0]
            embed.title = 'Track Queued!'
            embed.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'

            track = lavalink.models.AudioTrack(track, ctx.author.id, recommended=True)
            player.add(requester=ctx.author.id, track=track)

        await ctx.send(embed=embed)
        self.channel[str(ctx.channel.guild.id)] = ctx.channel

        if not player.is_playing:
            await player.play()

    @commands.command(
        name="seek",
        description="Seeks to a given position in a track.",
        aliases=["forward"]
    )
    async def seek(self, ctx, *, seconds: int):
        player = self.client.lavalink.player_manager.get(ctx.guild.id)

        track_time = player.position + (seconds * 1000)
        await player.seek(track_time)

        await ctx.send(f'Seeked to `{lavalink.utils.format_time(track_time)}`')

    @commands.command(
        name="skip",
        description="Skips the current track.",
        aliases=['forceskip']
    )
    async def skip(self, ctx):
        player = self.client.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send('Not playing currently.')

        await player.skip()
        await ctx.send('⏭ | Skipped.')

    @commands.command(
        name="stop",
        description="Stops the player and clears its queue."
    )
    async def stop(self, ctx):
        player = self.client.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send('Not playing currently.')

        player.queue.clear()
        await player.stop()
        await ctx.send('⏹ | Stopped.')

    @commands.command(
        name="nowplaying",
        description="Shows some stats about the currently playing song.",
        aliases=['np', 'playing']
    )
    async def nowplaying(self, ctx):
        player = self.client.lavalink.player_manager.get(ctx.guild.id)

        if not player.current:
            return await ctx.send('Nothing playing currently.')

        position = lavalink.utils.format_time(player.position)
        if player.current.stream:
            duration = '🔴 LIVE'
        else:
            duration = lavalink.utils.format_time(player.current.duration)

        requester = await self.client.fetch_user(player.current.requester)    
        song = f'[{player.current.title}]({player.current.uri}) - `{requester}`\n`({position}/{duration})`'

        embed = discord.Embed(
            color=self.client.colors["og_blurple"],
            title='Now Playing!', 
            description=song
        )
        await ctx.send(embed=embed)

    @commands.command(
        name="queue",
        description="Shows the player's queue.",
        aliases=['q']
    )
    async def queue(self, ctx, page: int = 1):
        player = self.client.lavalink.player_manager.get(ctx.guild.id)

        if not player.queue:
            return await ctx.send('Nothing queued.')

        items_per_page = 10
        pages = math.ceil(len(player.queue) / items_per_page)

        start = (page - 1) * items_per_page
        end = start + items_per_page

        queue_list = ''
        for index, track in enumerate(player.queue[start:end], start=start):
            queue_list += f'`{index + 1}.` [{track.title}]({track.uri})\n'

        embed = discord.Embed(
            title=f"Queue Info | {len(player.queue)} Tracks",
            description=f'{queue_list}',
            colour=self.client.colors["og_blurple"]
        )
        embed.set_footer(text=f'Page {page}/{pages}')
        await ctx.send(embed=embed)

    @commands.command(
        name="pause",
        description="Pauses/Resumes the current track.",
        aliases=['resume']
    )
    async def pause(self, ctx):
        player = self.client.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send('Not playing.')

        if player.paused:
            await player.set_pause(False)
            await ctx.send('⏯ | Resumed')
        else:
            await player.set_pause(True)
            await ctx.send('⏯ | Paused')

    @commands.command(
        name="volume",
        description="Changes the player's volume (0-200).",
        aliases=['vol']
    )
    async def volume(self, ctx, volume: int):
        player = self.client.lavalink.player_manager.get(ctx.guild.id)

        try:
            volume = int(volume)
        except:
            volume = int(volume[:-1])

        if not volume:
            return await ctx.send(f'🔈 | {player.volume}%')
        if 0 > volume > 201:
            return await ctx.send(f'Volume should be 0-200.')
            
        await player.set_volume(volume)  # Values are automatically capped between, or equal to 0-200.
        await ctx.send(f'🔈 | Set to {player.volume}%')

    @commands.command(
        name="shuffle",
        description="Shuffles the current queue."
    )
    async def shuffle(self, ctx):
        player = self.client.lavalink.player_manager.get(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send('Nothing playing.')

        player.shuffle = not player.shuffle
        await ctx.send('🔀 | Shuffle ' + ('enabled' if player.shuffle else 'disabled'))

    @commands.command(
        name="repeat",
        description="Repeats the current song until the command is used again.",
        aliases=['loop', 'l']
    )
    async def repeat(self, ctx):
        player = self.client.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send('Nothing playing.')

        player.repeat = not player.repeat
        await ctx.send('🔁 | Repeat ' + ('enabled' if player.repeat else 'disabled'))

    @commands.command(
        name="remove",
        description="Removes an item from the player's queue with the given index."
    )
    async def remove(self, ctx, index: int):
        player = self.client.lavalink.player_manager.get(ctx.guild.id)

        if not player.queue:
            return await ctx.send('Nothing queued.')

        if index > len(player.queue) or index < 1:
            return await ctx.send(f'Index has to be **between** 1 and {len(player.queue)}')

        removed = player.queue.pop(index - 1)  # Account for 0-index.

        await ctx.send(f'Removed `{removed.title}` from the queue.')

    @commands.command(
        name="lyrics",
        description="Get lyrics for the current track playing or manual."
    )
    async def lyrics_command(self, ctx, name: Optional[str]):
        player = self.client.lavalink.player_manager.get(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send("Nothing playing.")

        name = name or player.current.title

        async with ctx.typing():
            async with aiohttp.request("GET", f"https://some-random-api.ml/lyrics?title={quote_plus(name)}", headers={}) as r:
                if not 200 <= r.status <= 299:
                    return await ctx.send(f"Lyrics not found. Try doing it manually `{ctx.prefix}lyrics [name]`.")

                data = await r.json()

                if len(data["lyrics"]) > 2000:
                    return await ctx.send(f"<{data['links']['genius']}>")

                embed = discord.Embed(
                    title=data["title"],
                    description=data["lyrics"],
                    colour=self.client.colors["og_blurple"],
                    url=data['links']['genius']
                )
                embed.set_thumbnail(url=data["thumbnail"]["genius"])
                embed.set_author(name=data["author"])
                await ctx.send(embed=embed)

    @commands.command(
        name="find",
        description="Lists the first 10 search results from a given query."
    )
    async def find(self, ctx, *, query):
        player = self.client.lavalink.player_manager.get(ctx.guild.id)

        if not query.startswith('ytsearch:') and not query.startswith('scsearch:'):
            query = 'ytsearch:' + query

        results = await player.node.get_tracks(query)

        if not results or not results['tracks']:
            return await ctx.send('Nothing found.')

        tracks = results['tracks'][:10]  # First 10 results

        o = ''
        for index, track in enumerate(tracks, start=1):
            track_title = track['info']['title']
            track_uri = track['info']['uri']
            o += f'`{index}.` [{track_title}]({track_uri})\n'

        embed = discord.Embed(color=self.client.colors["og_blurple"], description=o)
        await ctx.send(embed=embed)

    @commands.command(
        name="disconnect",
        description="Disconnects from the voice channel and clears the queue.",
        aliases=['dc']
    )
    async def disconnect(self, ctx):
        player = self.client.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_connected:
            return await ctx.send('Not connected.')

        if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
            return await ctx.send('You\'re not in my voice channel!')

        player.queue.clear()
        await player.stop()
        await ctx.voice_client.disconnect(force=True)
        await ctx.send('👋 | Disconnected.')

def setup(client):
    client.add_cog(Music(client))