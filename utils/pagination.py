import discord
import asyncio
from dislash import ActionRow, Button, ButtonStyle


class Pagination:
    async def paginate(self, ctx, embeds: list):
        """Paginator to paginate a list of embeds.

        Args:
            ctx (commands.Context): The command context.
            embeds (list): The list of embeds to paginate.

        Returns:
            None: Returns nothing
        """
        current_page = 0
        page_btn = ActionRow(
            Button(
                emoji="⏮",
                custom_id="first",
                style=ButtonStyle.grey,
                disabled=True if current_page == 0 else False
            ),
            Button(
                emoji="◀",
                custom_id="back",
                style=ButtonStyle.grey,
                disabled=True if current_page == 0 else False
            ),
            # Button(
            #         emoji="⏹",
            #         custom_id = "stop",
            #         style = ButtonStyle.grey
            # ),
            Button(
                emoji="▶",
                custom_id="next",
                style=ButtonStyle.grey,
                # disabled = True if current_page == -1 else False
            ),
            Button(
                emoji="⏭",
                custom_id="last",
                style=ButtonStyle.grey,
                # disabled = True if current_page == -1 else False
            ))
        help_msg = await ctx.send(embed=embeds[current_page], components=[page_btn])
        while True:
            # Try and except blocks to catch timeout and break
            def check(inter):
                # if inter.message.id == help_msg.id and inter.author.id != ctx.author.id:
                #     await inter.respond("You can't control this pagination!", ephemeral=True)
                #     return False

                return inter.message.id == help_msg.id and inter.author.id == ctx.author.id

            try:
                inter = await ctx.wait_for_button_click(check=check, timeout=30.0)

                if (inter.clicked_button.custom_id.lower() == "back"):
                    current_page -= 1
                elif (inter.clicked_button.custom_id.lower() == "next"):
                    current_page += 1
                elif (inter.clicked_button.custom_id.lower() == "first"):
                    current_page = 0
                elif (inter.clicked_button.custom_id.lower() == "last"):
                    current_page = -1
                elif (inter.clicked_button.custom_id.lower() == "stop"):
                    await help_msg.edit(components=[])
                    break

                # If its out of index, go back to start / end
                if current_page == len(embeds):
                    current_page = 0
                elif current_page < 0:
                    current_page = len(embeds) - 1

                page_btn = ActionRow(
                    Button(
                        emoji="⏮",
                        custom_id="first",
                        style=ButtonStyle.grey,
                        disabled=True if current_page == 0 else False
                    ),
                    Button(
                        emoji="◀",
                        custom_id="back",
                        style=ButtonStyle.grey,
                        disabled=True if current_page == 0 else False
                    ),
                    # Button(
                    #         emoji="⏹",
                    #         custom_id = "stop",
                    #         style = ButtonStyle.grey
                    # ),
                    Button(
                        emoji="▶",
                        custom_id="next",
                        style=ButtonStyle.grey,
                        disabled=True if current_page == len(
                            embeds) - 1 else False
                    ),
                    Button(
                        emoji="⏭",
                        custom_id="last",
                        style=ButtonStyle.grey,
                        disabled=True if current_page == len(
                            embeds) - 1 else False
                    ))
                await inter.reply(type=7, embed=embeds[current_page], components=[page_btn])

            except asyncio.TimeoutError:
                disabled_btn = ActionRow(
                    Button(
                        emoji="⏮",
                        custom_id="first",
                        style=ButtonStyle.grey,
                        disabled=True
                    ),
                    Button(
                        emoji="◀",
                        custom_id="back",
                        style=ButtonStyle.grey,
                        disabled=True
                    ),
                    # Button(
                    #         emoji="⏹",
                    #         custom_id = "stop",
                    #         style = ButtonStyle.grey
                    # ),
                    Button(
                        emoji="▶",
                        custom_id="next",
                        style=ButtonStyle.grey,
                        disabled=True
                    ),
                    Button(
                        emoji="⏭",
                        custom_id="last",
                        style=ButtonStyle.grey,
                        disabled=True
                    ))
                await help_msg.edit(components=[disabled_btn])
                break
            except Exception:
                break
