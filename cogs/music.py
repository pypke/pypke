import asyncio
import math
import re
from typing import Optional
from urllib.parse import quote_plus

import aiohttp
import discord
import lavalink
from discord.ext import commands
from utils.pagination import Pagination

yt_url = re.compile(
    r"(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?(?P<id>[A-Za-z0-9\-=_]{11})"
)
# spotify link support soon
spotify_url = re.compile(r"(https?://)?(www\.)?(open\.)?spotify\.com/.+")
url_rx = re.compile(r"(https?://.*)")


class LavalinkVoiceClient(discord.VoiceClient):
    def __init__(self, client: discord.Client, channel: discord.abc.Connectable):
        self.client = client
        self.channel = channel
        # ensure there exists a client already
        if hasattr(self.client, "lavalink"):
            self.lavalink = self.client.lavalink
        else:
            self.client.lavalink = lavalink.Client(client.user.id)
            self.client.lavalink.add_node(
                "localhost", 2333, "youshallnotpass", "us", "default-node"
            )
            self.lavalink = self.client.lavalink

    async def on_voice_server_update(self, data):
        # the data needs to be transformed before being handed down to
        # voice_update_handler
        lavalink_data = {"t": "VOICE_SERVER_UPDATE", "d": data}
        await self.lavalink.voice_update_handler(lavalink_data)

    async def on_voice_state_update(self, data):
        # the data needs to be transformed before being handed down to
        # voice_update_handler
        lavalink_data = {"t": "VOICE_STATE_UPDATE", "d": data}
        await self.lavalink.voice_update_handler(lavalink_data)

    async def connect(self, *, timeout: float, reconnect: bool) -> None:
        # ensure there is a player_manager when creating a new voice_client
        self.lavalink.player_manager.create(guild_id=self.channel.guild.id)
        await self.channel.guild.change_voice_state(channel=self.channel)

    async def disconnect(self, *, force: bool) -> None:
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
        self.playing = {}

        if not hasattr(client, "lavalink"):
            client.lavalink = lavalink.Client(823051772045819905)
            client.lavalink.add_node(
                "lava.link", 80, "youshallnotpass", "eu", "default-node"
            )  # Host, Port, Password, Region, Name

        client.lavalink.add_event_hook(self.track_hook)

    def cog_unload(self):
        self.client.lavalink._event_hooks.clear()

    async def cog_before_invoke(self, ctx):
        guild_check = ctx.guild is not None
        if guild_check:
            await self.ensure_voice(ctx)
        return guild_check

    async def ensure_voice(self, ctx):
        """This check ensures that the client and command author are in the same voicechannel."""
        player = self.client.lavalink.player_manager.create(
            ctx.guild.id, endpoint=str(ctx.guild.region)
        )
        should_connect = ctx.command.name in ("play",)

        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("Join a voicechannel first.")

        if not player.is_connected:
            if not should_connect:
                await ctx.send("Not connected.")

            permissions = ctx.author.voice.channel.permissions_for(ctx.me)

            if not permissions.connect or not permissions.speak:  # Check user limit too?
                await ctx.send("I need `connect` and `speak` permissions.")

            player.store("channel", ctx.channel)
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
            await asyncio.sleep(30)
            player = event.player
            if not player.is_playing:
                guild_id = int(event.player.guild_id)
                guild = self.client.get_guild(guild_id)
                player = event.player
                channel = player.fetch("channel")
                if isinstance(channel, int):
                    channel = guild.get_channel(channel)

                await channel.send(
                    "Disconnected cause you didn't wanted to play anything."
                )
                await guild.voice_client.disconnect(force=True)

        elif isinstance(event, lavalink.TrackStartEvent):
            player = event.player
            channel = player.fetch("channel")
            if isinstance(channel, int):
                guild_id = int(event.player.guild_id)
                guild = self.client.get_guild(guild_id)
                channel = guild.get_channel(channel)

            await asyncio.sleep(3)
            msg = await channel.send(f"Playing :notes:`{event.track.title}` - Now!")
            self.playing[event.player.guild_id] = msg

        elif isinstance(event, lavalink.TrackEndEvent):
            try:
                msg = self.playing[event.player.guild_id]
                await msg.delete()
            except Exception:
                pass

        elif isinstance(event, lavalink.TrackExceptionEvent):
            raise commands.CommandInvokeError(event.exception)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.bot and after.channel is None:
            await asyncio.sleep(30)
            if not [m for m in before.channel.members if not m.bot]:
                player = self.client.lavalink.player_manager.get(
                    member.guild.id)
                try:
                    await player.stop()
                    await member.guild.voice_client.disconnect(force=True)
                except AttributeError:
                    pass

    @commands.command(
        name="play",
        description="Searches and plays a song from a given query.",
        aliases=["p"],
    )
    async def play(self, ctx, *, query: str):
        player = self.client.lavalink.player_manager.get(ctx.guild.id)

        query = query.strip("<>")

        if not yt_url.match(query):
            if url_rx.match(query):
                return await ctx.send("That doesn't look like a valid Youtube URL. PS: Spotify support comming soon.")
            else:
                query = f"ytsearch:{query}"

        results = await player.node.get_tracks(query)

        if not results or not results["tracks"]:
            return await ctx.send("Something is wrong, No tracks with that name found.")

        embed = discord.Embed(color=self.client.colors["og_blurple"])

        if results["loadType"] == "PLAYLIST_LOADED":
            tracks = results["tracks"]

            for track in tracks:
                player.add(requester=ctx.author.id, track=track)

            embed.title = "Playlist Queued!"
            embed.description = (
                f'{results["playlistInfo"]["name"]} - {len(tracks)} tracks'
            )
        else:
            track = results["tracks"][0]
            embed.title = "Track Queued!"
            embed.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'

            track = lavalink.models.AudioTrack(
                track, ctx.author.id, recommended=True)
            player.add(requester=ctx.author.id, track=track)

        await ctx.send(embed=embed)

        if not player.is_playing:
            await player.play()

    @commands.command(
        name="seek",
        description="Seeks to a given position in a track.",
        aliases=["forward"],
    )
    async def seek(self, ctx, seconds: int):
        player = self.client.lavalink.player_manager.get(ctx.guild.id)

        track_time = player.position + (seconds * 1000)
        await player.seek(track_time)

        await ctx.send(f"Seeked to `{lavalink.utils.format_time(track_time)}`")

    @commands.command(
        name="skip", description="Skips the current track.", aliases=["forceskip"]
    )
    async def skip(self, ctx):
        player = self.client.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send("Not playing currently.")

        await player.skip()
        await ctx.send("⏭ | Skipped.")

    @commands.command(name="stop", description="Stops the player and clears its queue.")
    async def stop(self, ctx):
        player = self.client.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send("Not playing currently.")

        player.queue.clear()
        await player.stop()
        await ctx.send("⏹ | Stopped.")

    @commands.command(
        name="nowplaying",
        description="Shows some stats about the currently playing song.",
        aliases=["np", "playing"],
    )
    async def nowplaying(self, ctx):
        player = self.client.lavalink.player_manager.get(ctx.guild.id)

        if not player.current:
            return await ctx.send("Nothing playing currently.")

        position = lavalink.utils.format_time(player.position)
        if player.current.stream:
            duration = "🔴 LIVE"
        else:
            duration = lavalink.utils.format_time(player.current.duration)

        requester = await self.client.fetch_user(player.current.requester)
        song = f"[{player.current.title}]({player.current.uri}) - `({position}/{duration})`\nRequester: `{requester}`"

        embed = discord.Embed(
            color=self.client.colors["og_blurple"],
            title="Now Playing!",
            description=song,
        )
        await ctx.send(embed=embed)

    @commands.group(name="queue", description="Shows the player's queue.", aliases=["q"])
    async def queue(self, ctx):
        if ctx.invoked_subcommand:
            return

        player = self.client.lavalink.player_manager.get(ctx.guild.id)

        if not player.queue:
            return await ctx.send("Nothing queued.")

        # I Know there is surely a better way to do this but Idfk it.
        per_page = 10
        pages = math.ceil(len(player.queue) / per_page)
        page = 1
        embeds = []
        while page <= pages:
            start = (page - 1) * per_page
            end = start + per_page

            queue_list = ""
            for index, track in enumerate(player.queue[start:end], start=start):
                queue_list += f"`{index + 1}.` [{track.title}]({track.uri})\n"

            embed = discord.Embed(
                title=f"Queue Info | {len(player.queue)} Tracks",
                description=f"{queue_list}",
                colour=self.client.colors["og_blurple"],
            )
            embed.set_footer(text=f"Page {page}/{pages}")
            embeds.append(embed)
            page += 1

        if len(embeds) > 1:
            await Pagination.paginate(self, ctx, embeds)
        else:
            await ctx.send(embed=embeds[0])

    @queue.command(name="clear", description="Clears the current queue.")
    async def queue_clear(self, ctx):
        player = self.client.lavalink.player_manager.get(ctx.guild.id)

        player.queue.clear()
        await ctx.send("Cleared the queue.")

    @commands.command(
        name="pause", description="Pauses/Resumes the current track.", aliases=["resume"]
    )
    async def pause(self, ctx):
        player = self.client.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send("Not playing.")

        if player.paused:
            await player.set_pause(False)
            await ctx.send("⏯ | Resumed")
        else:
            await player.set_pause(True)
            await ctx.send("⏯ | Paused")

    @commands.command(
        name="volume",
        description="Changes the player's volume (0-200).",
        aliases=["vol"],
    )
    async def volume(self, ctx, volume: Optional[int]):
        player = self.client.lavalink.player_manager.get(ctx.guild.id)

        try:
            volume = int(volume)
        except:
            volume = int(volume[:-1])

        if not volume:
            return await ctx.send(f"🔈 | {player.volume}%")
        if 0 > volume > 201:
            return await ctx.send(f"Volume should be 0-200.")

        await player.set_volume(
            volume
        )  # Values are automatically capped between, or equal to 0-200.
        await ctx.send(f"🔈 | Set to {player.volume}%")

    @commands.command(name="shuffle", description="Shuffles the current queue.")
    async def shuffle(self, ctx):
        player = self.client.lavalink.player_manager.get(ctx.guild.id)
        if not player.is_playing:
            return await ctx.send("Nothing playing.")

        player.shuffle = not player.shuffle
        await ctx.send("🔀 | Shuffle " + ("enabled" if player.shuffle else "disabled"))

    @commands.command(
        name="repeat",
        description="Repeats the current song until the command is used again.",
        aliases=["loop", "l"],
    )
    async def repeat(self, ctx):
        player = self.client.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_playing:
            return await ctx.send("Nothing playing.")

        player.repeat = not player.repeat
        await ctx.send("🔁 | Repeat " + ("enabled" if player.repeat else "disabled"))

    @commands.command(
        name="remove",
        description="Removes an item from the player's queue with the given index.",
    )
    async def remove(self, ctx, index: int):
        player = self.client.lavalink.player_manager.get(ctx.guild.id)

        if not player.queue:
            return await ctx.send("Nothing queued.")

        if index > len(player.queue) or index < 1:
            return await ctx.send(
                f"Index has to be **between** 1 and {len(player.queue)}"
            )

        removed = player.queue.pop(index - 1)  # Account for 0-index.

        await ctx.send(f"Removed `{removed.title}` from the queue.")

    @commands.command(
        name="lyrics", description="Get lyrics for the current track playing or manual."
    )
    async def lyrics_command(self, ctx, name: Optional[str]):
        player = self.client.lavalink.player_manager.get(ctx.guild.id)
        if not player.is_playing and not name:
            return await ctx.send("Nothing playing.")

        name = name or player.current.title

        async with ctx.typing():
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://some-random-api.ml/lyrics?title={quote_plus(name)}"
                ) as r:
                    if 300 > r.status >= 200:
                        data = await r.json()
                    else:
                        return await ctx.send(
                            f"Lyrics not found. Try doing it manually `{ctx.prefix}lyrics [name]`."
                        )

                    if len(data["lyrics"]) > 2000:
                        return await ctx.send(f"<{data['links']['genius']}>")

                    embed = discord.Embed(
                        title=data["title"],
                        description=data["lyrics"],
                        colour=self.client.colors["og_blurple"],
                        url=data["links"]["genius"],
                    )
                    embed.set_thumbnail(url=data["thumbnail"]["genius"])
                    embed.set_author(name=data["author"])
                    await ctx.send(embed=embed)

    @commands.command(
        name="equalizer",
        default="Equalizers to improve your experience.",
        aliases=["eq"],
        hidden=True,
    )
    async def equalizer(self, ctx, *args):
        player = self.client.lavalink.player_manager.get(ctx.guild.id)

        if len(args) == 0:
            return await ctx.send(
                f"Type `{ctx.prefix}equalizer --list` for all presets."
            )
        elif len(args) == 1:
            presets = {
                "reset": "Default",
                "bassboost": [
                    0.08,
                    0.12,
                    0.2,
                    0.18,
                    0.15,
                    0.1,
                    0.05,
                    0.0,
                    0.02,
                    -0.04,
                    -0.06,
                    -0.08,
                    -0.10,
                    -0.12,
                    -0.14,
                ],
                "jazz": [
                    -0.13,
                    -0.11,
                    -0.1,
                    -0.1,
                    0.14,
                    0.2,
                    -0.18,
                    0.0,
                    0.24,
                    0.22,
                    0.2,
                    0.0,
                    0.0,
                    0.0,
                    0.0,
                ],
                "treble": [
                    -0.1,
                    -0.12,
                    -0.12,
                    -0.12,
                    -0.08,
                    -0.04,
                    0.0,
                    0.3,
                    0.34,
                    0.4,
                    0.35,
                    0.3,
                    0.3,
                    0.3,
                    0.3,
                ],
            }

            preset = args[0].lower()
            if preset in ["reset", "default"]:
                await player.reset_equalizer()
                return await ctx.send("Equalizer reset.")
            elif preset in presets:
                gain_list = enumerate(presets[preset])
                await player.set_gains(*gain_list)
                return await ctx.send(f"Equalizer set to {preset}.")

            elif preset == "--list":
                em = discord.Embed(
                    title="Equalizer Presets",
                    color=self.client.colors["og_blurple"],
                    description=", ".join(presets.keys()),
                )
                return await ctx.send(embed=em)
            else:
                return await ctx.send(
                    f"Invalid preset specified!\nType `{ctx.prefix}equalizer --list` for all presets."
                )
        # elif len(args) == 2:
        #     try:
        #         band = int(args[0])
        #         gain = float(args[1])
        #         await player.set_gain(band, gain)
        #     except ValueError:
        #         return await ctx.send('Specify valid `band gain` values.')
        else:
            return await ctx.send(
                f"Type `{ctx.prefix}equalizer --list` for all presets."
            )

    @commands.command(
        name="find",
        description="Lists the first 10 search results from a given query.",
        hidden=True,
    )
    async def find(self, ctx, *, query):
        player = self.client.lavalink.player_manager.get(ctx.guild.id)

        if not query.startswith("ytsearch:") and not query.startswith("scsearch:"):
            query = "ytsearch:" + query

        results = await player.node.get_tracks(query)

        if not results or not results["tracks"]:
            return await ctx.send("Nothing found.")

        tracks = results["tracks"][:10]  # First 10 results

        o = ""
        for index, track in enumerate(tracks, start=1):
            track_title = track["info"]["title"]
            track_uri = track["info"]["uri"]
            o += f"`{index}.` [{track_title}]({track_uri})\n"

        embed = discord.Embed(
            color=self.client.colors["og_blurple"], description=o)
        await ctx.send(embed=embed)

    @commands.command(
        name="disconnect",
        description="Disconnects from the voice channel and clears the queue.",
        aliases=["dc"],
    )
    async def disconnect(self, ctx):
        player = self.client.lavalink.player_manager.get(ctx.guild.id)

        if not player.is_connected:
            return await ctx.send("Not connected.")

        if not ctx.author.voice or (
            player.is_connected and ctx.author.voice.channel.id != int(
                player.channel_id)
        ):
            return await ctx.send("You're not in my voice channel!")

        player.queue.clear()
        await player.stop()
        await ctx.voice_client.disconnect(force=True)
        await ctx.send("👋 | Disconnected.")


def setup(client):
    client.add_cog(Music(client))
