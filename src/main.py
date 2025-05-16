import os
from dotenv import load_dotenv
load_dotenv()

from sylvia_bot import SylviaBot

bot = SylviaBot()
bot.run(os.getenv("DISCORD_BOT_TOKEN"))