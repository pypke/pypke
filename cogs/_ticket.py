import asyncio
from typing import Optional

import discord
from discord import commands, tasks
from dislash import ActionRow, ButtonStyle

# Under Devlopment


class Ticket(commands.Cog, hidden=True):
    def __init__(self, bot):
        self.bot = bot
        self.update_cache_task = self.update_cache.start()
        self.ticket_data_cache = {}

    def cog_unload(self):
        self.update_cache_task.cancel()

    async def ticket_create(self, inter, data):
        guild = self.bot.get_guild(int(data["_id"]))
        # Btw we don't need this as if we aren't in the guild we wont get the interaction ¯\_(ツ)_/¯
        if not guild:
            await self.bot.ticket_config.delete(data["_id"])
            return

        category = guild.get_channel(int(data["category_id"]))
        role = guild.get_role(int(data["role_id"]))
        victim = inter.author

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True),
            victim: discord.PermissionOverwrite(read_messages=True),
        }
        if role:
            overwrites[role] = discord.PermissionOverwrite(read_messages=True)

        ticket = await guild.create_text_channel(
            f"ticket-{int(data['ticket_no']) + 1}",
            overwrite=overwrites,
            category=category,
            reason=f"Ticket created by {victim}.",
            topic=f"Support ticket for {victim.mention} (Id: {victim.id})",
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
            "victim_id": victim.id,
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
            content=f"{victim.mention} Welcome", embed=embed, components=[close_btn]
        )
        if role:
            await ticket.send(f"{role.mention} has created a new ticket!")

        return await inter.respond(f"Ticket created - {ticket.mention}", ephemeral=True)

    async def ticket_close(self, inter, data):
        guild = self.bot.get_guild(int(data["guild_id"]))
        ticket = guild.get_channel(int(data["_id"]))
        victim = guild.get_member(int(data["victim_id"]))

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True),
            victim: discord.PermissionOverwrite(read_messages=None),
        }
        await ticket.edit(overwrites=overwrites)
        components = ActionRow()
        components.add_button(
            style=ButtonStyle.gray,
            label="Delete",
            emoji="🗑",
            custom_id=f"delete_ticket_{guild.id}",
        )
        components.add_button(
            style=ButtonStyle.gray,
            label="Transcript",
            custom_id=f"transcript_{guild.id}",
        )

        embed = discord.Embed(
            title="Ticket Closed",
            description=f"Ticket was closed by {inter.author}.",
            color=self.bot.colors["yellow"],
        )
        await ticket.send(embed=embed, components=[components])

    @tasks.loop(seconds=30)
    async def update_cache(self):
        data = await self.bot.ticket_config.get_all()
        for i in data:
            self.ticket_data_cache[int(i["_id"])] = i

    @commands.Cog.listener()
    async def on_button_click(self, inter):
        guild_id = int(inter.guild.id)

        if inter.component.custom_id == f"create_ticket_{guild_id}":
            await inter.respond(type=6)  # Ack the interaction

            data = self.ticket_data_cache[guild_id]
            if not inter.message.id == data["msg_id"]:
                return

            await self.ticket_create(inter, data)
        elif inter.component.custom_id == f"close_ticket_{guild_id}":
            await inter.respond(type=6)  # Ack the interaction

            data = await self.bot.active_tickets.find(inter.channel.id)
            await self.ticket_close(inter, data)
        elif inter.component.custom_id == f"delete_ticket_{guild_id}":
            await inter.respond(
                f"Ok {inter.author.mention}, This ticket will be deleted in 10 seconds."
            )
            await asyncio.sleep(10)
            await inter.channel.delete(
                reason=f"Ticket deleted by {inter.author} (ID: {inter.author.id})"
            )
        elif inter.component.custom_id == f"transcript_{guild_id}":
            pass

    @commands.group(
        name="ticket", description="Shows this message.", invoke_without_command=True
    )
    async def ticket(self, ctx):
        if ctx.invoked_subcommand:
            return

        await ctx.invoke(self.bot.get_command("help"), command_or_module="ticket")

    @ticket.command(name="setup", description="Setups ticketing in this server.")
    async def ticket_setup(self, ctx):
        pass
        questions = [
            f"Mention the channel like {ctx.channel.mention} for ticket panel creation.",
            f"Mention the support role for tickets. Reply `None` to for no role."
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
                await msg.delete()

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

        role_id = int(answers[1][2:-1])
        role = ctx.guild.get_role(role_id)

        category_id = int(answers[2][2:-1])
        category = ctx.guild.get_channel(category_id)

        ticket_panel = ActionRow()
        ticket_panel.add_button(
            style=ButtonStyle.grey,
            label="Create Ticket",
            emoji="📨",
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
            "role_id": role.id or None,
            "category_id": category.id or None,
        }
        await self.bot.ticket_config.upsert(ticket_setup_data)
        await ctx.send(
            embed=discord.Embed(
                description=f"Created ticket panel in {channel.mention}.",
                color=self.bot.colors["yellow"],
            )
        )


def setup(bot):
    bot.add_cog(Ticket(bot))
