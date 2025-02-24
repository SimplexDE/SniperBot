import discord
import os
import textwrap
import re
from unidecode import unidecode

from PIL import ImageFont, Image, ImageDraw

from util.constants import FONTS_SRC, IMAGES_SRC

class Quote:
    def __init__(self, *, message: discord.Message):
        self.message = message
    
    
    def _truncate_text(self, text, max_chars=100, suffix="..."):
        return text[:max_chars] + suffix if len(text) > max_chars else text
    
    def _replace_mentions(self, text: str, guild: discord.Guild):        
        pattern = "<(@|#|@&?)(\\d+)>"
        mentions = re.findall(pattern, text)
        
        for mention in mentions:
            match (mention[0]):
                case ("@&"):
                    text = text.replace(f"<{mention[0] + str(mention[1])}>", f"@{guild.get_role(int(mention[1])).name}")      
                case ("@"):
                    text = text.replace(f"<{mention[0] + str(mention[1])}>", f"@{guild.get_member(int(mention[1])).name}")
                case ("#"):
                    text = text.replace(f"<{mention[0] + str(mention[1])}>", f"#{guild.get_channel(int(mention[1])).name}") 
                case (_):
                    continue

        return text
    
    def _normalize_text(self, text: str):
        return unidecode(text)
    
    async def create(self) -> discord.File:
        if not os.path.exists(f"{IMAGES_SRC}/out"):
            os.mkdir(f"{IMAGES_SRC}/out")

        avatar_path = "images/out/avatar.png"

        avatar = self.message.author.display_avatar if self.message.author.display_avatar is not None else self.message.author.default_avatar
        await avatar.save(avatar_path)

        AVATAR_SIZE = (256, 256)
        BACKGROUND_SIZE = (256*2, 256)

        FONT_LARGE = ImageFont.truetype(font=f"{FONTS_SRC}/arial.ttf", size=24)
        FONT_SMALL = ImageFont.truetype(font=f"{FONTS_SRC}/arial.ttf", size=18)
        FONT_XSMALL = ImageFont.truetype(font=f"{FONTS_SRC}/arial.ttf", size=12)

        mask = Image.open(f"{IMAGES_SRC}/mask.png")
        background = Image.new("RGBA", BACKGROUND_SIZE, color=(0,0,0))
        avatar_image = Image.open(avatar_path).resize(AVATAR_SIZE)
        background.paste(avatar_image, mask=mask.convert("L").resize(AVATAR_SIZE))

        draw = ImageDraw.Draw(background)

        message_text = self._replace_mentions(self.message.content, self.message.guild)
        message_text = self._normalize_text(message_text)
        final_message = "\n".join(textwrap.wrap(message_text, 25))
        final_message = self._truncate_text(final_message)

        textbox_LARGE = draw.textbbox((0, 0), text=f"„{final_message}“", font=FONT_LARGE)
        textbox_SMALL = draw.textbbox((0, 0), text=self._normalize_text(self.message.author.display_name), font=FONT_SMALL)
        textbox_XSMALL = draw.textbbox((0, 0), text=self.message.author.name, font=FONT_XSMALL)

        textbox_middle_L = (textbox_LARGE[2] / 2, textbox_LARGE[3] / 2)
        textbox_middle_S = (textbox_SMALL[2] / 2, textbox_SMALL[3] / 2)
        textbox_middle_XS = (textbox_XSMALL[2] / 2, textbox_XSMALL[3] / 2)

        draw.text((512 / 2 - textbox_middle_L[0] + 90, 256 / 2 - textbox_middle_L[1]), font=FONT_LARGE, text=f"„{final_message}“", fill="white", align="center")
        draw.text((512 / 2 - textbox_middle_S[0] + 90, 256 / 2 - textbox_middle_S[1] + 90), font=FONT_SMALL, text=self._normalize_text(self.message.author.display_name), fill="white", align="center")
        draw.text((512 / 2 - textbox_middle_XS[0] + 90, 256 / 2 - textbox_middle_S[1] + 115), font=FONT_XSMALL, text=self.message.author.name, fill="gray", align="center")

        background.save(f"{IMAGES_SRC}/out/out.png")

        return discord.File(f"{IMAGES_SRC}/out/out.png")