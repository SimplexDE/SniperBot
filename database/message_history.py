"""
Write-through cache of recently seen messages, used as a fallback source for the
snipe feature when discord.py's own in-memory message cache no longer holds a
deleted message (e.g. after a bot restart). Entries expire automatically after
TTL_SECONDS via a MongoDB TTL index, so this never needs manual cleanup.
"""

import datetime

import discord

from database.mongodb import MongoDB
from database.mongoclient import DATABASE_NAME

COLLECTION_NAME = "message_history"
TTL_SECONDS = 60 * 60 * 24  # 24h


class MessageHistory:
    def __init__(self):
        self.db = MongoDB(DATABASE_NAME)

    def ensure_index(self):
        self.db.collection(COLLECTION_NAME).create_index("created_at", expireAfterSeconds=TTL_SECONDS)

    def remember(self, message: discord.Message):
        self.db.collection(COLLECTION_NAME).update_one(
            {"_id": message.id},
            {"$set": {
                "channel_id": message.channel.id,
                "guild_id": message.guild.id,
                "author_id": message.author.id,
                "content": message.content,
                "has_embeds": bool(message.embeds),
                "created_at": datetime.datetime.now(datetime.timezone.utc),
            }},
            upsert=True,
        )

    def get(self, message_id: int) -> dict:
        return self.db.query_one(COLLECTION_NAME, {"_id": message_id})
