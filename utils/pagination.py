import discord, asyncio
from dislash import ActionRow, Button, ButtonStyle

class Pagination:
    async def paginate(self, ctx, embeds: list):
        current_page = 0
        page_btn = ActionRow(
            Button(
                    label = "First",
                    custom_id = "first",
                    style = ButtonStyle.blurple
            ),
            Button(
                    label = "Back",
                    custom_id = "back",
                    style = ButtonStyle.blurple
            ),
            Button(
                    label = "Stop",
                    custom_id = "stop",
                    style = ButtonStyle.red
            ),
            Button(
                    label = "Next",
                    custom_id = "ahead",
                    style = ButtonStyle.blurple
            ),
            Button(
                    label = "Last",
                    custom_id = "last",
                    style = ButtonStyle.blurple
            ))
        help_msg = await ctx.send(embed=embeds[current_page], components=[page_btn])
        while True:
            # Try and except blocks to catch timeout and break
            def check(inter):
                return inter.message.id == help_msg.id and inter.author.id == ctx.author.id
                
            try:
                inter = await ctx.wait_for_button_click(check=check, timeout=20.0)
                
                if (inter.clicked_button.label.lower() == "back"):
                    current_page -= 1
                elif (inter.clicked_button.label.lower() == "next"):
                    current_page += 1
                elif (inter.clicked_button.label.lower() == "first"):
                    current_page = 0
                elif (inter.clicked_button.label.lower() == "last"):
                    current_page = -1
                elif (inter.clicked_button.label.lower() == "stop"):
                    await help_msg.edit(components=[])
                    break

                # If its out of index, go back to start / end
                if current_page == len(embeds):
                    current_page = 0
                elif current_page < 0:
                    current_page = len(embeds) - 1

                await inter.reply(type=7, embed=embeds[current_page], components=[page_btn])

            except asyncio.TimeoutError:
                await help_msg.edit(components=[])
                break
            except:
                break