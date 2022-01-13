import logging

from decouple import config
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    Filters,
    CallbackQueryHandler,
    MessageHandler,
    Updater,
)

import database as db

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
/add_course - to add course
/add_school - to add school
/add_department - to add department
"""
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)


def list_admins(update, context):
    if not db.is_superadmin(update.message.from_user):
        return
    admins = db.list_admins()
    msg = "Admins\n"
    for first_name, username in admins:
        msg += f"{first_name} - @{username}\n"
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)


def add_admin(update, context):
    if not db.is_superadmin(update.message.from_user):
        return
    for user in context.args:
        db.add_admin(user)
    if not context.args:
        update.message.reply_text("When you insert this command please insert the username or id next to the command ")
    else:
        update.message.reply_text("Admin Registered Successfully")


def remove_admin(update, context):
    if not db.is_superadmin(update.message.from_user):
        return
    for user in context.args:
        db.remove_admin(user)
    if not context.args:
        update.message.reply_text("When you insert this command please insert the username or id next to the command ")
    else:
        update.message.reply_text("Admin Deleted Successfully")


def add_school(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="What is the name the school?"
    )
    return 1


def save_school_name(update, context):
    context.user_data["school_name"] = update.message.text
    update.message.reply_text("What is  Short Name of the school")
    return 2


def save_school_short_name(update, context):
    school_name = context.user_data["school_name"]
    school_short_name = update.message.text
    db.add_school(school_name, school_short_name)
    update.message.reply_text("School added successfully")
    return ConversationHandler.END


def add_department(update, context):
    keybords = []
    schools = db.list_schools()
    for school_id, school_code in schools:
        keybords.append([InlineKeyboardButton(school_code, callback_data=school_id)])
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="Select School?",
        reply_markup=InlineKeyboardMarkup(keybords)
    )
    return 1

def save_school_id_1(update, context):
    query = update.callback_query
    query.answer()
    context.user_data['school_id'] = int(query.data)
    context.bot.send_message(chat_id=update.effective_chat.id, text="What is Name of the Department")
    return 2

def save_department_name(update, context):

    context.user_data["department_name"] = update.message.text
    update.message.reply_text("What is Short Name of the Department")
    return 3
    
def save_department_short_name(update, context):
    context.user_data["department_short_name"] = update.message.text
    update.message.reply_text("How many semesters")
    return 4


# def save_department_no_of_sem(update, context):
#     context.user_data["department_no_sem"] = update.message.text
#     update.message.reply_text("No of semesters")
#     return 6
def save_department_no_of_sem(update,context):
    dept_no_sem = update.message.text
    department_name = context.user_data["department_name"]
    dept_short_name = context.user_data["department_short_name"]
    school_id= context.user_data['school_id']
    db.add_department(department_name,dept_short_name,dept_no_sem, school_id)
    update.message.reply_text("Department added successfully")
    return ConversationHandler.END

# def add_course(update, context):
#     context.bot.send_message(
#         chat_id=update.effective_chat.id, text="What is the name the course?"
#     )
#     return 1


# def save_course_name(update, context):
#     context.user_data["course_name"] = update.message.text
#     update.message.reply_text("What is Short code of the course")
#     return 2


# def save_department_short_name(update, context):
#     # department_name = context.user_data['department_name']
#     context.user_data["department_short_name"] = update.message.text
#     # department_short_name = update.message.text
#     update.message.reply_text("How many semester does it have")
#     return 3


# def save_department_no_of_sem(update, context):
#     context.user_data["department_no_sem"] = update.message.text
#     update.message.reply_text("What is department id")
#     return 4


# def save_school_id(update, context):
#     school_id = update.message.text
#     department_name = context.user_data["department_name"]
#     dept_short_name = context.user_data["department_short_name"]
#     dept_no_sem = context.user_data["department_no_sem"]
#     db.add_deparment(department_name,dept_short_name,dept_no_sem,school_id)
#     update.message.reply_text("department added successfully")
#     return ConversationHandler.END


def cancel(update, context):
    return ConversationHandler.END


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
dispatcher.add_handler(
    ConversationHandler(
        entry_points=[CommandHandler("add_school", add_school)],
        states={
            1: [MessageHandler(Filters.text & ~Filters.command, save_school_name)],
            2: [
                MessageHandler(Filters.text & ~Filters.command, save_school_short_name)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
)
dispatcher.add_handler(
    ConversationHandler(
        entry_points=[CommandHandler("add_department", add_department)],
        states={
            1: [CallbackQueryHandler(save_school_id_1)],
            2: [
                MessageHandler(
                    Filters.text & ~Filters.command, save_department_name
                )
            ],
            3: [
                MessageHandler(
                    Filters.text & ~Filters.command, save_department_short_name
                )
            ],
            4: [MessageHandler(Filters.text & ~Filters.command, save_department_no_of_sem)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
)
if __name__ == "__main__":
    updater.start_polling()
    updater.idle()
