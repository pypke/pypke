import io
import asyncio
from typing import Optional

import discord
import chat_exporter
from discord.ext import commands, tasks
from dislash import ActionRow, ButtonStyle

# Under Devlopment


class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.update_cache_task = self.update_cache.start()
        self.ticket_data_cache = {}
        self.hidden = True

        chat_exporter.init_exporter(self.bot)

    def cog_unload(self):
        self.update_cache_task.cancel()

    async def ticket_create(self, inter, data):
        guild: discord.Guild = self.bot.get_guild(int(data["_id"]))
        # Btw we don't need this as if we aren't in the guild we wont get the interaction ¯\_(ツ)_/¯
        if not guild:
            await self.bot.ticket_config.delete(data["_id"])
            return

        data_check = await self.bot.active_tickets.find_if(
            {"created_by": inter.author.id, "guild_id": inter.guild.id}
        )
        if data_check:
            return await inter.respond(
                f"There is already a ticket opened by you.", ephemeral=True
            )

        category = guild.get_channel(
            int(data["category_id"]) if data["category_id"] else None
        )
        role = guild.get_role(int(data["role_id"]) if data["role_id"] else None)
        member: discord.Member = inter.author

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True),
            member: discord.PermissionOverwrite(read_messages=True),
        }
        if role:
            overwrites[role] = discord.PermissionOverwrite(read_messages=True)

        ticket_no = str(data["ticket_no"]) if int(data["ticket_no"]) < 9999 else "0"
        zeroes = 4 - len(ticket_no)

        ticket = await guild.create_text_channel(
            f"ticket-{'0' * zeroes}{int(ticket_no) + 1}",
            overwrites=overwrites,
            category=category,
            reason=f"Ticket created by {member}.",
            topic=f"Support ticket for {member.mention} (Id: {member.id})",
        )

        close_btn = ActionRow()
        close_btn.add_button(
            style=ButtonStyle.grey,
            label="Close",
            emoji="🔒",
            custom_id=f"close_ticket_{guild.id}",
        )

        embed = discord.Embed(
            color=self.bot.colors["yellow"],
            description="Support will be with you shortly.\nTo close this ticket click the 🔒 button.",
        )
        embed.set_footer(
            text=f"{self.bot.user.name} - Ticketing without clutter",
            icon_url=self.bot.user.avatar.url,
        )

        ticket_data = {
            "_id": ticket.id,
            "guild_id": guild.id,
            "created_by": member.id,
        }
        await self.bot.active_tickets.upsert(ticket_data)

        older_data_update = {
            "_id": data["_id"],
            "ticket_no": int(data["ticket_no"]) + 1,
            "msg_id": data["msg_id"],
            "channel_id": data["channel_id"],
            "role_id": data["role_id"] or None,
            "category_id": data["category_id"] or None,
        }
        await self.bot.ticket_config.update(older_data_update)

        await ticket.send(
            content=f"{member.mention} Welcome", embed=embed, components=[close_btn]
        )
        if role:
            await ticket.send(
                f"{role.mention} support ticket is created by {member.mention}"
            )

        return await inter.respond(f"Ticket created - {ticket.mention}", ephemeral=True)

    async def ticket_close(self, data):
        guild: discord.Guild = self.bot.get_guild(int(data["guild_id"]))
        ticket = guild.get_channel(int(data["_id"]))
        member = guild.get_member(int(data["created_by"]))

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True),
            member: discord.PermissionOverwrite(read_messages=None),
        }
        await ticket.edit(
            name=ticket.name.replace("ticket-", "closed-"), overwrites=overwrites
        )
        return ticket

    @tasks.loop(seconds=2)
    async def update_cache(self):
        data = await self.bot.ticket_config.get_all()
        for i in data:
            self.ticket_data_cache[int(i["_id"])] = i

    @commands.Cog.listener()
    async def on_button_click(self, inter):
        guild_id = int(inter.guild.id)

        if inter.component.custom_id == f"create_ticket_{guild_id}":
            # await inter.respond(type=6)  # Ack the interaction

            data = self.ticket_data_cache[guild_id]
            if not inter.message.id == data["msg_id"]:
                return

            await self.ticket_create(inter, data)

        elif inter.component.custom_id == f"close_ticket_{guild_id}":
            await inter.respond(type=6)  # Ack the interaction

            data = await self.bot.active_tickets.find(inter.channel.id)
            ticket = await self.ticket_close(inter, data)

            components = ActionRow()
            components.add_button(
                style=ButtonStyle.gray,
                label="Delete",
                emoji="⛔",
                custom_id=f"delete_ticket_{inter.guild.id}",
            )
            components.add_button(
                style=ButtonStyle.gray,
                label="Transcript",
                emoji="📝",
                custom_id=f"transcript_{inter.guild.id}",
            )

            embed = discord.Embed(
                title="Ticket Closed",
                description=f"Ticket was closed by {inter.author}.",
                color=self.bot.colors["yellow"],
            )
            await ticket.send(embed=embed, components=[components])

        elif inter.component.custom_id == f"delete_ticket_{guild_id}":
            await inter.respond(
                f"Ok {inter.author.mention}, This ticket will be deleted in 10 seconds."
            )
            await asyncio.sleep(10)
            await self.bot.active_tickets.delete(inter.channel.id)
            await inter.channel.delete(
                reason=f"Ticket deleted by {inter.author} (ID: {inter.author.id})"
            )

        elif inter.component.custom_id == f"transcript_{guild_id}":
            await inter.respond(type=6)  # Ack the interaction
            transcript = await chat_exporter.export(inter.channel)

            if transcript is None:
                return await inter.channel.send(
                    "Something is wrong are you sure this channel isn't empty?"
                )

            file = discord.File(
                io.BytesIO(transcript.encode()),
                filename=f"transcript-{inter.channel.name}.html",
            )

            await inter.channel.send(
                content="Here is the transcript for this channel.", file=file
            )

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if member.bot:
            return

        data = await self.bot.active_tickets.get_if(
            {
                "created_by": member.id,
                "guild_id": member.guild.id,
            }
        )
        if data:
            settings = self.bot.ticket_settings.get(member.guild.id)
            if settings and settings["close_on_leave"] == True:
                ticket = await self.ticket_close(data)

                components = ActionRow()
                components.add_button(
                    style=ButtonStyle.gray,
                    label="Delete",
                    emoji="⛔",
                    custom_id=f"delete_ticket_{member.guild.id}",
                )
                components.add_button(
                    style=ButtonStyle.gray,
                    label="Transcript",
                    emoji="📝",
                    custom_id=f"transcript_{member.guild.id}",
                )

                embed = discord.Embed(
                    title="Ticket Closed",
                    description=f"Ticket was closed because {member} left this server.",
                    color=self.bot.colors["yellow"],
                )
                await ticket.send(embed=embed, components=[components])
            else:
                pass

    @commands.group(
        name="ticket", description="Shows this message.", invoke_without_command=True
    )
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def ticket(self, ctx):
        if ctx.invoked_subcommand:
            return await ctx.invoke(self.bot.get_command("help"), command_or_module="ticket")

    @ticket.command(name="setup", description="Setups ticketing in this server.")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def ticket_setup(self, ctx):
        data = await self.bot.ticket_config.get(ctx.guild.id)
        if data:
            return await ctx.send(
                f"You already have a ticket panel setup. Use `{ctx.prefix}ticket delete` before creating one again."
            )

        questions = [
            f"Mention the channel like {ctx.channel.mention} for ticket panel creation.",
            f"Mention the support role for tickets. Reply `None` to for no role.",
            f"Give the category id to create tickets in. Reply `None` to create ticket at top of every channel.",
        ]
        embeds = []
        for question in questions:
            embed = discord.Embed(
                title="Ticketing", description=question, color=self.bot.colors["yellow"]
            )
            embeds.append(embed)

        answers = []

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        ques_msg = None
        for embed in embeds:
            if not ques_msg:
                ques_msg = await ctx.send(embed=embed)
            await ques_msg.edit(embed=embed)

            try:
                msg = await self.bot.wait_for("message", timeout=30.0, check=check)
            except asyncio.TimeoutError:
                await ctx.send("Time's Up, please be quicker next time!")
                return
            else:
                answers.append(msg.content)
                await asyncio.sleep(3)
                await msg.delete()

        await ques_msg.delete()

        try:
            channel_id = int(answers[0][2:-1])
            channel = ctx.guild.get_channel(channel_id)
            if channel:
                pass
            else:
                await ctx.send(f"Channel should be in this guild!!")
                return
        except:
            await ctx.send(
                f"You didn't mention a channel properly. Do it like this {ctx.channel.mention} next time."
            )
            return

        if not answers[1] in ["None", "no", "none"]:
            role_id = int(answers[1][3:-1])
            role = ctx.guild.get_role(role_id)
        else:
            role = None

        if not answers[2] in ["None", "no", "none"]:
            category_id = int(answers[2])
            category = ctx.guild.get_channel(category_id)
        else:
            category = None

        ticket_panel = ActionRow()
        ticket_panel.add_button(
            style=ButtonStyle.grey,
            label="Create Ticket",
            emoji="📩",
            custom_id=f"create_ticket_{ctx.guild.id}",
        )
        panel_embed = discord.Embed(
            color=self.bot.colors["yellow"],
            title="Create a Ticket!",
            description="Create a Ticket to get help, or support.",
        )
        panel_embed.set_footer(
            text="Ticketing without clutter.", icon_url=self.bot.user.avatar.url
        )

        msg = await channel.send(embed=panel_embed, components=[ticket_panel])

        ticket_setup_data = {
            "_id": ctx.guild.id,
            "ticket_no": 0000,
            "msg_id": msg.id,
            "channel_id": channel_id,
            "role_id": role.id if role else None,
            "category_id": category.id if category else None,
        }
        await self.bot.ticket_config.upsert(ticket_setup_data)
        await ctx.send(
            embed=discord.Embed(
                description=f"Created ticket panel in {channel.mention}.",
                color=self.bot.colors["yellow"],
            )
        )

    @ticket.command(
        name="destroy", description="Destroys the ticket panel for this server."
    )
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def ticket_destroy(self, ctx):
        data = await self.bot.ticket_config.get(ctx.guild.id)
        if not data:
            return await ctx.send(
                f"You haven't setup the ticket panel yet, please use `{ctx.prefix}ticket setup` to setup the panel."
            )

        await self.bot.ticket_config.delete(ctx.guild.id)
        await ctx.reply("Destroyed the ticket panel, you can now safely delete the message.")

    @ticket.command(name="add", description="Add a member to the current active ticket.")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def ticket_add(
        self, ctx, member: discord.Member, ticket: Optional[discord.TextChannel]
    ):
        channel = ticket or ctx.channel

        data = await self.bot.active_tickets.get(channel.id)
        if not data:
            return await ctx.send(
                f"This command can only be used inside a ticket, or pls specify the ticket channel mention/id."
            )

        overwrites = {
            member: discord.PermissionOverwrite(read_messages=True),
        }
        await channel.edit(overwrites=overwrites)
        await channel.send(
            f"{member.mention}, you were added to this ticket by {ctx.author}."
        )
        await ctx.send("Done!")

    @ticket.command(
        name="remove",
        description="Remove a member from the current active ticket.",
        aliases=["rm"],
    )
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def ticket_remove(
        self, ctx, member: discord.Member, ticket: Optional[discord.TextChannel]
    ):
        channel = ticket or ctx.channel

        data = await self.bot.active_tickets.get(channel.id)
        if not data:
            return await ctx.send(
                f"This command can only be used inside a ticket, or pls specify the ticket channel mention/id."
            )

        overwrites = {
            member: discord.PermissionOverwrite(read_messages=None),
        }
        await channel.edit(overwrites=overwrites)
        await ctx.send("Done!")

    @ticket.command(
        name="setting",
        description="Set some settings for tickets. Provide the index parameter to toggle on",
        aliases=["config", "settings"],
    )
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def ticket_setting(self, ctx, index: Optional[int]):
        data = await self.bot.ticket_settings.get(ctx.guild.id)

        if not index:
            if not data:
                close_on_leave = "<:disagreed:918425439960186930>"
                delete_after = "<:disagreed:918425439960186930>"
            else:
                close_on_leave = (
                    "<:disagreed:918425439960186930>"
                    if data["close_on_leave"] == False
                    else "<:agreed:918425367251935242>"
                )
                delete_after = (
                    "<:disagreed:918425439960186930>"
                    if data["delete_after"] == False
                    else "<:agreed:918425367251935242>"
                )

            embed = discord.Embed(title="Ticket Settings", color=self.bot.colors["yellow"])
            embed.add_field(
                name=f"1) Close on member leave {close_on_leave}",
                value="Closes the ticket if the ticket creator leaves.",
                inline=False,
            )
            embed.add_field(
                name=f"2) Delete after 7 days {delete_after}",
                value="Delete closed tickets after 7 days.",
                inline=False,
            )

            embed.set_thumbnail(url=self.bot.user.avatar.url)
            await ctx.send(embed=embed)

        settings = ["close_on_leave", "delete_after"]
        if not data:
            data = {
                "_id": ctx.guild.id,
                "close_on_leave": False,
                "delete_after": False,
            }

            data[settings[index - 1]] = True
            await self.bot.ticket_settings.upsert(data)
            await ctx.send(f"Toggled {settings[index - 1]} to True.")

        if data[settings[index - 1]] == False:
            data[settings[index - 1]] = True
        else:
            data[settings[index - 1]] = False

        await self.bot.ticket_settings.upsert(data)
        await ctx.send(f"Toggled {settings[index - 1]} to {data[settings[index - 1]]}.")


def setup(bot):
    bot.add_cog(Ticket(bot))
