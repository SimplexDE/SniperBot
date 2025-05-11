from prometheus_client import start_http_server, Counter, Gauge, Enum

MESSAGES_SNIPED = Counter('sniper_bot_messages_sniped', 'Statistic about how many Messages Spongiper sniped')
# MESSAGES_IN_STARBOARD = Gauge('sniper_bot_starboard_messages', 'How many Starboard messages spongiper has stored')
# STARS = Gauge('sniper_bot_stars', 'Statistic how many stars spongiper has collected')
SERVER_COUNT = Gauge('sniper_bot_server_count', 'How many Servers Spongiper is in')
USER_COUNT = Gauge('sniper_bot_user_count', 'How many Users Spongiper has')
MESSAGES = Counter('sniper_bot_messages', 'Statistic how many message events were received')
BOT_LATENCY = Gauge('sniper_bot_latency', 'Snipers Latency')
BOT_UPTIME = Gauge('sniper_bot_uptime', 'Uptime of Sniper Bot')
BOT_STATUS = Enum('sniper_bot_state', 'The State Spongiper is currently in',
                    states=['starting', "running", 'stopped'])

start_http_server(4000)

