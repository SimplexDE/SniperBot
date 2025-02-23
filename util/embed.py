import discord
import datetime
from typing import Union

class Embed:
    def __init__(
                self,
                *,
                title: str = "",
                alt_title: str = "",
                title_url: str = "",
                title_icon_url: str = "",
                description: str = "",
                footer: str = "",
                footer_icon_url: str = "",
                fields: list[tuple] = [],
                image_url: str = "",
                color: Union[int, discord.Colour] = discord.Color.light_gray(),
                timestamp: datetime.datetime = datetime.datetime.now()
                ):
        self.title = title
        self.alt_title = alt_title
        self.description = description
        self.color = color
        self.title_url = title_url
        self.footer = footer
        self.title_icon_url = title_icon_url
        self.fields = fields
        self.timestamp = timestamp
        self.footer_icon_url = footer_icon_url
        self.image_url = image_url
        
    def BigEmbed(self) -> discord.Embed:
        """'Bigger' embed, requires Banner URL"""
        out = discord.Embed(title=self.alt_title, description=self.description, color=self.color, timestamp=self.timestamp)
        out.set_author(name=self.title, icon_url=self.title_icon_url, url=self.title_url)
        out.set_footer(text=self.footer, icon_url=self.footer_icon_url)
        
        if len(self.image_url) == 0:
            raise Exception("No Banner set")
        out.set_image(url=self.image_url)
        
        if len(self.fields) != 0:
            for _field in self.fields:
                out.add_field(name=_field[0], value=_field[1], inline=_field[2])
        
        return out

    def StandardEmbed(self) -> discord.Embed:
        """Standardized Embed"""
        out = discord.Embed(title="", description=self.description, color=self.color, timestamp=self.timestamp)
        out.set_author(name=self.title, icon_url=self.title_icon_url, url=self.title_url)
        out.set_footer(text=self.footer, icon_url=self.footer_icon_url)
        
        if len(self.fields) != 0:
            for _field in self.fields:
                out.add_field(name=_field[0], value=_field[1], inline=_field[2])
        
        return out

    def MinimalEmbed(self) -> discord.Embed:
        """Only uses Description"""
        if len(self.description) == 0:
            raise Exception("No Description set")
    
        return discord.Embed(title="", description=self.description, color=self.color)

