from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (CallbackQueryHandler, CommandHandler,
                          ConversationHandler, Filters, MessageFilter,
                          MessageHandler)

import database as db

# from main import (save_sch_id,save_dept_id,save_year,save_sem)
back_inline_keyboard = [InlineKeyboardButton("🔙Back", callback_data="back")]

confirm_keybords = [
    [
        InlineKeyboardButton("✅Yes", callback_data="yes"),
        InlineKeyboardButton("❌No", callback_data="no"),
    ]
]
confirm_reply_markup = InlineKeyboardMarkup(confirm_keybords)


SUPERADMIN_MSG = """
/add_admin - To add admins.
/list_admins - To list admin.
/remove_admin - To remove admin."""

ADMIN_MSG = """
/add_school - to add school.
/add_department - to add department.
/add_course - to add course.
/remove_school - to remove school
/remove_department - to remove department
/remove_course - to remove course"""


def list_admins(update, context):
    if not db.is_superadmin(update.message.from_user):
        return
    admins = db.list_admins()
    if admins == []:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="There is no admins"
        )
        # a, b, c = map(int, input().split())
    else:
        msg = "Admins\n"
        for first_name, username in admins:
            msg += f"{first_name} - @{username}\n"
        context.bot.send_message(chat_id=update.effective_chat.id, text=msg)


def add_admin(update, context):
    if not db.is_superadmin(update.message.from_user):
        return
    flag = False
    for user in context.args:
        res = db.add_admin(user)
        if res:
            flag = True
    if not context.args:
        update.message.reply_text(
            "When you insert this command please insert like /add_admin @username "
        )
    elif flag:
        update.message.reply_text("Admin Registered Successfully")
    else:
        update.message.reply_text("The users are not the user of this bot ")


def remove_admin(update, context):
    if not db.is_superadmin(update.message.from_user):
        return
    for user in context.args:
        db.remove_admin(user)
    if db.remove_admin == []:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="There is no admins"
        )
    if not context.args:
        update.message.reply_text(
            "When you insert this command please insert like /remove_admin @username"
        )
    else:
        update.message.reply_text("Admin Deleted Successfully")
