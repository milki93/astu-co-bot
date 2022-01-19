from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (CallbackQueryHandler, CommandHandler,
                          ConversationHandler, Filters, MessageHandler)

import database as db

from .admin import confirm_reply_markup


def add_school(update, context):
    if not db.is_admin(update.message.from_user):
        return
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="What is the name the school?"
    )
    return 1


def save_school_name(update, context):
    context.user_data["school_name"] = update.message.text
    update.message.reply_text(
        "What is Short Name of the school\n\n/cancel adding school. "
    )
    return 2


def save_school_short_name(update, context):
    school_name = context.user_data["school_name"]
    school_short_name = update.message.text
    db.add_school(school_name, school_short_name)
    update.message.reply_text("School added successfully!")
    return ConversationHandler.END


def remove_school(update, context):
    if not db.is_admin(update.message.from_user):
        return
    schools = db.list_schools()
    if not schools:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="There are no Schools"
        )
        return ConversationHandler.END

    keyboards = []
    for school_id, school_code in schools:
        keyboards.append([InlineKeyboardButton(school_code, callback_data=school_id)])

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Select School",
        reply_markup=InlineKeyboardMarkup(keyboards),
    )
    return 1


def remove_school_warning(update, context):
    query = update.callback_query
    query.answer()
    context.user_data["school_id"] = int(query.data)

    query.edit_message_text(
        text="Are you sure to delete the School?", reply_markup=confirm_reply_markup
    )
    return 2


def remove_school_id(update, context):
    query = update.callback_query
    query.answer()
    if query.data == "yes":
        school_id = context.user_data["school_id"]
        db.remove_school(school_id)
        query.edit_message_text(text="School Deleted Successfully")
    else:
        query.edit_message_text(text="Successfully cancelled")
    return ConversationHandler.END


def cancel(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="Operation canceled successfully "
    )
    return ConversationHandler.END


school_ch = ConversationHandler(
    entry_points=[CommandHandler("add_school", add_school)],
    states={
        1: [MessageHandler(Filters.text & ~Filters.command, save_school_name)],
        2: [MessageHandler(Filters.text & ~Filters.command, save_school_short_name)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

rem_sch_ch = ConversationHandler(
    entry_points=[CommandHandler("remove_school", remove_school)],
    states={
        1: [CallbackQueryHandler(remove_school_warning)],
        2: [CallbackQueryHandler(remove_school_id)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
