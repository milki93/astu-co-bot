import logging

from decouple import config
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, Updater

import database as db
from admin import (add_admin, course_ch, department_ch, list_admins,
                   remove_admin, school_ch)

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


def start(update, context):
    bot_first_name = context.bot.first_name
    bot_last_name = context.bot.last_name
    msg = f"𝖜𝖊𝖑𝖈𝖔𝖒𝖊 to {bot_first_name or ''} {bot_last_name or ''}.\n"
    user = update.message.from_user
    db.register_user(user)

    if db.is_superadmin(user):
        msg += """
/add_admin - To add admins.
/list_admins - To list admin.
/remove_admin - To remove admin.
"""
    if db.is_admin(user):
        msg += """
/add_school - to add school.
/add_department - to add department.
/add_course - to add course.
"""
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)


# Define Bot Token
TOKEN = config("TOKEN")

# Define Bot Updater
updater = Updater(TOKEN)

# Define Bot Dispatcher
dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("list_admins", list_admins))
dispatcher.add_handler(CommandHandler("add_admin", add_admin))
dispatcher.add_handler(CommandHandler("remove_admin", remove_admin))
# dispatcher.add_handler(CommandHandler("add_school",add_school ))
# dispatcher.add_handler(CommandHandler("add_department", add_department))
dispatcher.add_handler(school_ch)
dispatcher.add_handler(department_ch)
dispatcher.add_handler(course_ch)

if __name__ == "__main__":
    updater.start_polling()
    updater.idle()
