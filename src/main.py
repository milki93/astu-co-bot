import logging
import queue

from decouple import config
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      InlineQueryResultCachedDocument)
from telegram.ext import (CallbackQueryHandler, CommandHandler,
                          ConversationHandler, Filters, InlineQueryHandler,
                          MessageHandler, Updater)

import database as db
from admin import *

# from admin import (add_admin, course_ch, department_ch, list_admins,rem_cou,
#                    rem_dept_ch, rem_sch_ch, remove_admin, school_ch, ADMIN_MSG, SUPERADMIN_MSG)


# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)


back_inline_keyboard = [InlineKeyboardButton("🔙Back", callback_data="back")]
confirm_keybords = [
    [
        InlineKeyboardButton("✅Yes", callback_data="yes"),
        InlineKeyboardButton("❌No", callback_data="no"),
    ]
]
confirm_reply_markup = InlineKeyboardMarkup(confirm_keybords)


def help(update):
    """Displays info on how to use the bot."""
    update.message.reply_text("Use /start to test this bot.")


def start(update, context):
    bot_first_name = context.bot.first_name
    bot_last_name = context.bot.last_name
    msg = f"𝖜𝖊𝖑𝖈𝖔𝖒𝖊 to {bot_first_name or ''} {bot_last_name or ''}.\n"
    user = update.message.from_user
    db.register_user(user)

    if db.is_superadmin(user):
        msg += SUPERADMIN_MSG
    if db.is_admin(user):
        msg += ADMIN_MSG
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)

    keybords = []
    schools = db.list_schools()
    for school_id, school_code in schools:
        keybords.append([InlineKeyboardButton(school_code, callback_data=school_id)])
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=("Select School?" if schools else "Sorry!, There is no available school."),
        reply_markup=InlineKeyboardMarkup(keybords),
    )

    return 1


def save_sch_id(update, context):
    query = update.callback_query
    query.answer()
    context.user_data["school_id"] = int(query.data)
    sch_id = context.user_data["school_id"]
    keyboards = []
    departments = db.list_departments(sch_id)
    if departments == []:
        query.edit_message_text(text="There are no departments")
    else:
        for deparment_id, dept_code in departments:
            keyboards.append(
                [InlineKeyboardButton(dept_code, callback_data=deparment_id)]
            )
        keyboards.append(back_inline_keyboard)
        query.edit_message_text(
            text="Select department",
            reply_markup=InlineKeyboardMarkup(keyboards),
        )
        return 2


def save_dept_id(update, context):
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
    context.user_data["department_id"] = int(query.data)
    dept_id = context.user_data["department_id"]
    keyboards = []
    years = db.list_year(dept_id)
    for year in years:
        keyboards.append(
            [InlineKeyboardButton(str(year[0]) + " Year", callback_data=year[0])]
        )
    keyboards.append(back_inline_keyboard)
    query.edit_message_text(
        text="Which year", reply_markup=InlineKeyboardMarkup(keyboards)
    )
    return 3


def save_year(update, context):
    query = update.callback_query
    query.answer()
    if query.data == "back":
        sch_id = context.user_data["school_id"]
        keyboards = []
        departments = db.list_departments(sch_id)
        for deparment_id, dept_code in departments:
            keyboards.append(
                [InlineKeyboardButton(dept_code, callback_data=deparment_id)]
            )
        keyboards.append(back_inline_keyboard)
        query.edit_message_text(
            text="Select department",
            reply_markup=InlineKeyboardMarkup(keyboards),
        )
        return 2

    context.user_data["year"] = int(query.data)
    year = context.user_data["year"]
    keyboards = []
    semsters = db.list_sem(year)
    if semsters == []:
        query.edit_message_text(text="There are no semesters")
    else:
        for semster in semsters:
            keyboards.append(
                [
                    InlineKeyboardButton(
                        str(semster[0]) + " semester", callback_data=semster[0]
                    )
                ]
            )
        keyboards.append(back_inline_keyboard)
        query.edit_message_text(
            text="Which semster?", reply_markup=InlineKeyboardMarkup(keyboards)
        )
        return 4


def save_sem(update, context):
    query = update.callback_query
    query.answer()
    if query.data == "back":
        dept_id = context.user_data["department_id"]
        keyboards = []
        years = db.list_year(dept_id)
        for year in years:
            keyboards.append(
                [InlineKeyboardButton(str(year[0]) + " Year", callback_data=year[0])]
            )
        keyboards.append(back_inline_keyboard)
        query.edit_message_text(
            text="Which year", reply_markup=InlineKeyboardMarkup(keyboards)
        )
        return 3

    context.user_data["sem"] = query.data
    semes = context.user_data["sem"]
    year = context.user_data["year"]
    dept_id = context.user_data["department_id"]
    keyboards = []
    courses = db.list_course(dept_id, year, semes)
    if courses == []:
        query.edit_message_text(text="There are no Courses")
    else:
        for cid, course in courses:
            keyboards.append([InlineKeyboardButton(course, callback_data=cid)])
        keyboards.append(back_inline_keyboard)
        query.edit_message_text(
            text="Which course", reply_markup=InlineKeyboardMarkup(keyboards)
        )
        return 5


def send_file_id(update, context):
    query = update.callback_query
    query.answer()
    if query.data == "back":
        year = context.user_data["year"]
        keyboards = []
        semsters = db.list_sem(year)
        for semster in semsters:
            keyboards.append(
                [
                    InlineKeyboardButton(
                        str(semster[0]) + " semester", callback_data=semster[0]
                    )
                ]
            )
        keyboards.append(back_inline_keyboard)
        query.edit_message_text(
            text="Which semster?", reply_markup=InlineKeyboardMarkup(keyboards)
        )
        return 4
    # query.message.delete()
    context.user_data["file_id"] = query.data
    file_id = context.user_data["file_id"]
    context.bot.send_document(
        chat_id=update.effective_chat.id, document=db.get_file_id(query.data)[0]
    )
    # query.message.reply_text("Thanks")
    return ConversationHandler.END


def cancel(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="Conversation Canceled Successfully "
    )
    return ConversationHandler.END


def course_inline_handler(update, context):
    query = update.inline_query.query
    if not query:
        return
    data = query.lower()
    result = []
    courses = db.search_courses()
    for name, course_code, file_id in courses:
        if data in name.lower() or data in course_code.lower():
            result.append(
                InlineQueryResultCachedDocument(
                    id=course_code, title=name, document_file_id=file_id
                )
            )
    update.inline_query.answer(result)


# Define Bot Token
TOKEN = config("TOKEN")


def main():
    # Define Bot Updater
    updater = Updater(TOKEN)

    # Define Bot Dispatcher
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler("list_admins", list_admins))
    dispatcher.add_handler(CommandHandler("add_admin", add_admin))
    dispatcher.add_handler(CommandHandler("remove_admin", remove_admin))
    dispatcher.add_handler(CommandHandler("help", help))
    dispatcher.add_handler(rem_sch_ch)
    dispatcher.add_handler(school_ch)
    dispatcher.add_handler(department_ch)
    dispatcher.add_handler(course_ch)
    dispatcher.add_handler(rem_dept_ch)

    dispatcher.add_handler(rem_cou)
    dispatcher.add_handler(InlineQueryHandler(course_inline_handler))
    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("start", start)],
            states={
                1: [CallbackQueryHandler(save_sch_id)],
                2: [CallbackQueryHandler(save_dept_id)],
                3: [CallbackQueryHandler(save_year)],
                4: [CallbackQueryHandler(save_sem)],
                5: [CallbackQueryHandler(send_file_id)],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
        )
    )

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
