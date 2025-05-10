import discord

class VIP:
    DEVELOPER = 579111799794958377
    BOT = 862859543700176896

class Emote:
    SPACER = "<:spacer:1226137637148950559>"
    INFO = "<:info:1226139199351296051>"
    RIGHT_ARROW = "<:helioschevronright:1267515447406887014>"
    MEDAL = "<:heliosmedal:1267515459012657245>"
    STAR = ":star:"
    WARNING = ":warning:"
    EDIT = "<:edit:1210725875625099304>"
    NSFW = ":underage:"
    CHECK = ":white_check_mark:"
    UNCHECK = ":x:"

FONTS_SRC = "./fonts"
IMAGES_SRC = "./images"
ATTACHMENTS_SRC = "./attachments"

COLORS = [
    discord.Color.blue(),
    discord.Color.red(),
    discord.Color.blurple(),
    discord.Color.gold(),
    discord.Color.green(),
    discord.Color.fuchsia(),
    discord.Color.yellow(),
    discord.Color.magenta(),
    discord.Color.random(),
]

ONLINE_PRESENCES = [
    discord.CustomActivity(name="Type s to snipe deleted messages"),
    discord.CustomActivity(name="Stalking for deleted messages"),
    discord.CustomActivity(name="Reviewing quotes"),
    discord.CustomActivity(name="Quoting people"),
    discord.CustomActivity(name="Danke Simplex"),
    discord.CustomActivity(name="Danke Don"),
    discord.CustomActivity(name="Danke Juox"),
    discord.CustomActivity(name="Danke ZS"),
    discord.CustomActivity(name="Pfennichfuchsen!"),
    discord.CustomActivity(name="BILLIG BILLIG BILLIG"),
    discord.CustomActivity(name="Sauferstoffcord"),
    discord.Activity(type=discord.ActivityType.playing, name="Aale und Rolltreppen"),
    discord.Activity(type=discord.ActivityType.watching, name="Don"),
    discord.Activity(type=discord.ActivityType.watching, name="Juox"),
    discord.Activity(type=discord.ActivityType.watching, name="Simplex"),
    discord.Activity(type=discord.ActivityType.watching, name="ZS"),
    discord.Activity(type=discord.ActivityType.watching, name="Spongebob Squarepants"),
    discord.Streaming(name="Technikstube", url="https://www.youtube.com/watch?v=d1YBv2mWll0"),
    discord.Streaming(name="Der Keller", url="https://www.youtube.com/watch?v=xvFZjo5PgG0"),
    discord.Streaming(name="Die Stube", url="https://www.youtube.com/watch?v=xvFZjo5PgG0"),
    discord.Streaming(name="Geizhalshandschlag", url="https://www.youtube.com/watch?v=Mzv6ZsEj8HE")
]

STARTUP_PRESENCES = [
    discord.CustomActivity(name="¯\\_(ツ)_/¯"),
    discord.CustomActivity(name="q(≧▽≦q)"),
    discord.CustomActivity(name="(^///^)"),
    discord.CustomActivity(name="\\^o^/"),
    discord.CustomActivity(name="(ಥ _ ಥ)"),
    discord.CustomActivity(name="◑﹏◐"),
    discord.CustomActivity(name="The purpose of our lives is to be happy. — Dalai Lama"),
    discord.CustomActivity(name="The healthiest response to life is joy. — Deepak Chopra"),
]