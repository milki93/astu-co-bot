from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (CallbackQueryHandler, CommandHandler,
                          ConversationHandler, Filters, MessageHandler)

import database as db

from .admin import back_inline_keyboard, confirm_reply_markup


def add_department(update, context):
    if not (
        db.is_superadmin(update.message.from_user)
        or db.is_admin(update.message.from_user)
    ):
        return
    keybords = []
    schools = db.list_schools()
    for school_id, school_code in schools:
        keybords.append([InlineKeyboardButton(school_code, callback_data=school_id)])
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Select School?",
        reply_markup=InlineKeyboardMarkup(keybords),
    )
    return 1


def save_school_id_1(update, context):
    query = update.callback_query
    query.answer()
    context.user_data["school_id"] = int(query.data)
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="What is Name of the Department"
    )
    return 2


def save_department_name(update, context):

    context.user_data["department_name"] = update.message.text
    update.message.reply_text("What is Short Name of the Department")
    return 3


def save_department_short_name(update, context):
    dept_short_name = update.message.text
    department_name = context.user_data["department_name"]
    school_id = context.user_data["school_id"]
    db.add_department(department_name, dept_short_name, school_id)
    update.message.reply_text("Department added successfully")
    return ConversationHandler.END


def cancel(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="Conversation Canceled Successfully "
    )
    return ConversationHandler.END


def remove_department(update, context):
    if not db.is_superadmin(update.message.from_user):
        return
    keybords = []
    schools = db.list_schools()
    if schools == []:
        context.bot.send_message(
            chat_id=update.effective_chat.id, text="There are no schools"
        )
    else:
        for school_id, school_code in schools:
            keybords.append(
                [InlineKeyboardButton(school_code, callback_data=school_id)]
            )
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Select School?",
            reply_markup=InlineKeyboardMarkup(keybords),
        )

        return 1


def save_school_id(update, context):
    query = update.callback_query
    query.answer()
    context.user_data["school_id"] = int(query.data)
    sch_id = context.user_data["school_id"]
    keyboards = []
    keyboards.append(back_inline_keyboard)
    departments = db.list_departments(sch_id)
    if departments == []:
        query.edit_message_text(text="There are no departments")
    else:
        for department_id, dept_code in departments:
            keyboards.append(
                [InlineKeyboardButton(dept_code, callback_data=department_id)]
            )
        query.edit_message_text(
            text="Select department",
            reply_markup=InlineKeyboardMarkup(keyboards),
        )
        return 2


def remove_deparment_warning(update, context):
    query = update.callback_query
    query.answer()
    if query.data == "back":
        schools = db.list_schools()
        keybords = []
        for school_id, school_code in schools:
            keybords.append(
                [InlineKeyboardButton(school_code, callback_data=school_id)]
            )
            query.edit_message_text(
                text="Select School?",
                reply_markup=InlineKeyboardMarkup(keybords),
            )
        return 1
    keyboards = []
    keyboards.append(back_inline_keyboard)
    context.user_data["department_id"] = int(query.data)
    query.edit_message_text(
        text="Are you sure to delete the Department?", reply_markup=confirm_reply_markup
    )
    return 3


def remove_d_id(update, context):
    query = update.callback_query
    query.answer()
    if query.data == "back":
        departments = db.list_departments()
        keybords = []
        for deparment_id, dept_code in departments:
            keybords.append(
                [InlineKeyboardButton(dept_code, callback_data=deparment_id)]
            )
            query.edit_message_text(
                text="Select department?",
                reply_markup=InlineKeyboardMarkup(keybords),
            )
        return 1
    if query.data == "yes":
        dep_id = context.user_data["department_id"]
        db.remove_department(dep_id)
        query.edit_message_text(text="Department Deleted Successfully")
    else:
        query.edit_message_text(text="Successfully cancelled")
    return ConversationHandler.END


department_ch = ConversationHandler(
    entry_points=[CommandHandler("add_department", add_department)],
    states={
        1: [CallbackQueryHandler(save_school_id_1)],
        2: [MessageHandler(Filters.text & ~Filters.command, save_department_name)],
        3: [
            MessageHandler(Filters.text & ~Filters.command, save_department_short_name)
        ],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
rem_dept_ch = ConversationHandler(
    entry_points=[CommandHandler("remove_department", remove_department)],
    states={
        1: [CallbackQueryHandler(save_school_id)],
        2: [CallbackQueryHandler(remove_deparment_warning)],
        3: [CallbackQueryHandler(remove_d_id)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
