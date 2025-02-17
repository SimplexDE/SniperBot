"""
A commands.Bot wrapper to implement easy communication with the database
"""

import os

import discord
from discord.ext import commands

from database.mongodb import MongoDB

DATABASE_NAME = os.environ.get("DATABASE_NAME", "spongiper_dev")


class SpongiperClient:
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    async def get_guild(self, _id: int):
        g = self.bot.get_guild(_id)
        if g is None:
            g = await self.bot.fetch_guild(_id)
        return SpongiperGuild(g)

    def delete_guild(self, guild_id: int):
        db = self.database()
        db.delete_one("settings", {"_id": guild_id})

    @staticmethod
    def database():
        return MongoDB(DATABASE_NAME)

class SpongiperGuild:
    def __init__(self, guild: discord.Guild):
        self.guild: discord.Guild = guild

    @staticmethod
    def database():
        return MongoDB(DATABASE_NAME)

    @property
    def settings(self):
        db = self.database()
        settings = db.query_one("guilds", {"_id": self.guild.id})

        doc = {"_id": self.guild.id}

        if settings is None:
            db.insert("guilds", doc)
            return doc
        return settings

    @settings.setter
    def settings(self, mdb_document: dict):
        self.database().update("guilds", {"_id": self.guild.id}, mdb_document)