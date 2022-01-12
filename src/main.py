import logging

from decouple import config
from telegram.ext import Updater

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

# Define Bot Token
TOKEN = config("TOKEN")

# Define Bot Updater
updater = Updater(TOKEN)

# Define Bot Dispatcher
dispatcher = updater.dispatcher

if __name__ == "__main__":
    updater.start_polling()
    updater.idle()
