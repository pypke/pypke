"""
From the python discord server's Sir Lancelot Bot
"""
import discord
from discord import commands

DROPDOWN_TIMEOUT = 60
STYLES = {
    "Epoch": ("",),
    "Short Time": (
        "t",
        "h:mm A",
    ),
    "Long Time": ("T", "h:mm:ss A"),
    "Short Date": ("d", "MM/DD/YYYY"),
    "Long Date": ("D", "MMMM D, YYYY"),
    "Short Date/Time": ("f", "MMMM D, YYYY h:mm A"),
    "Long Date/Time": ("F", "dddd, MMMM D, YYYY h:mm A"),
    "Relative Time": ("R",),
}


class TimestampMenuView(discord.ui.View):
    """View for the epoch command which contains a single `discord.ui.Select` dropdown component."""

    def __init__(self, ctx: commands.Context, formatted_times: list[str], epoch: int):
        super().__init__(timeout=DROPDOWN_TIMEOUT)
        self.ctx = ctx
        self.epoch = epoch
        self.dropdown: discord.ui.Select = self.children[0]
        for label, date_time in zip(STYLES.keys(), formatted_times):
            self.dropdown.add_option(label=label, description=date_time)

    @discord.ui.select(placeholder="Select the format of your timestamp")
    async def select_format(
        self, _: discord.ui.Select, interaction: discord.Interaction
    ) -> discord.Message:
        """Drop down menu which contains a list of formats which discord timestamps can take."""
        selected = interaction.data["values"][0]
        if selected == "Epoch":
            return await interaction.response.edit_message(content=f"`{self.epoch}`")
        return await interaction.response.edit_message(
            content=f"`<t:{self.epoch}:{STYLES[selected][0]}>`"
        )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Check to ensure that the interacting user is the user who invoked the command."""
        if interaction.user != self.ctx.author:
            embed = discord.Embed(
                description="Sorry, but this dropdown menu can only be used by the original author."
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
        return True
