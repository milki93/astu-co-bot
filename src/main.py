import logging
import queue

from decouple import config
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup,
                      InlineQueryResultCachedDocument)
from telegram.ext import (CallbackQueryHandler, CommandHandler,
                          ConversationHandler, InlineQueryHandler,
                          MessageHandler, Updater)

import database as db
from admin import (add_admin, course_ch, department_ch, list_admins,
                   rem_dept_ch, rem_sch_ch, remove_admin, school_ch)

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
            /remove_school - to remove school
            /remove_department - to remove department
            /remove_course - to remove course
        """
    context.bot.send_message(chat_id=update.effective_chat.id, text=msg)

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


def save_sch_id(update, context):
    query = update.callback_query
    query.answer()
    context.user_data["school_id"] = int(query.data)
    sch_id = context.user_data["school_id"]
    keyboards = []
    departments = db.list_departments(sch_id)
    for deparment_id, dept_code in departments:
        keyboards.append([InlineKeyboardButton(dept_code, callback_data=deparment_id)])
    # context.bot.send_message(chat_id=update.effective_chat.id, text="What is Name of the Course")
    query.edit_message_text(
        text="Select department",
        reply_markup=InlineKeyboardMarkup(keyboards),
    )
    return 2


def save_dept_id(update, context):
    query = update.callback_query
    query.answer()
    context.user_data["department_id"] = int(query.data)
    dept_id = context.user_data["department_id"]
    keyboards = []
    years = db.list_year(dept_id)
    for year in years:
        keyboards.append([InlineKeyboardButton(str(year[0]) + " Year", callback_data=year[0])])
    query.edit_message_text(
        text="Which year", reply_markup=InlineKeyboardMarkup(keyboards)
    )
    return 3


def save_year(update, context):
    query = update.callback_query
    query.answer()
    context.user_data["year"] =int(query.data)
    year = context.user_data["year"]
    keyboards = []
    semsters = db.list_sem(year)
    for semster in semsters:
        keyboards.append(
            [InlineKeyboardButton(str(semster[0]) + "semester", callback_data=semster[0])]
        )
    query.edit_message_text(
        text="Which semster", reply_markup=InlineKeyboardMarkup(keyboards)
    )
    return 4


def save_sem(update, context):
    query = update.callback_query
    query.answer()
    context.user_data["sem"] = query.data
    semes = context.user_data["sem"]
    year = context.user_data["year"]
    dept_id = context.user_data["department_id"]
    keyboards = []
    courses = db.list_course(dept_id, year, semes)
    for cid, course in courses:
        keyboards.append([InlineKeyboardButton(course, callback_data=cid)])
    query.edit_message_text(
        text="Which course", reply_markup=InlineKeyboardMarkup(keyboards)
    )
    return 5


def send_file_id(update, context):
    query = update.callback_query
    query.answer()
    query.message.delete()
    context.user_data["file_id"] = query.data
    file_id = context.user_data["file_id"]
    context.bot.send_document(
        chat_id=update.effective_chat.id, document=db.get_file_id(query.data)[0]
    )
    # query.message.reply_text("Thanks")
    return ConversationHandler.END


def cancel(update, context):
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
def remove_course(update,context):
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
def delete_course(update, context):
    query = update.callback_query
    query.answer()
    db.remove_course(query.data)
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="course Deleted Successfully"
    )
    return ConversationHandler.END
# def update_admin(update,context):
#     keybords = [
#         [InlineKeyboardButton(user_name,callback_data=)]
#     ]
#     for school_id, school_code in schools:
#         keybords.append([InlineKeyboardButton(school_code, callback_data=school_id)])
#     context.bot.send_message(
#         chat_id=update.effective_chat.id,
#         text="Select School?",
#         reply_markup=InlineKeyboardMarkup(keybords),
#     )

#     return 1



# Define Bot Token
TOKEN = config("TOKEN")


def main():
    # Define Bot Updater
    updater = Updater(TOKEN)

    # Define Bot Dispatcher
    dispatcher = updater.dispatcher
    # dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("list_admins", list_admins))
    dispatcher.add_handler(CommandHandler("add_admin", add_admin))
    dispatcher.add_handler(CommandHandler("remove_admin", remove_admin))
    dispatcher.add_handler(rem_sch_ch)
    dispatcher.add_handler(school_ch)
    dispatcher.add_handler(department_ch)
    dispatcher.add_handler(course_ch)
    dispatcher.add_handler(rem_dept_ch)
    dispatcher.add_handler(InlineQueryHandler(course_inline_handler))
    # dispatcher.add_handler(rem_course)
    # dispatcher.add_handler(rem_course)
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
    dispatcher.add_handler(
        ConversationHandler(
            entry_points=[CommandHandler("remove_course", remove_course)],
            states={
                1: [CallbackQueryHandler(save_sch_id)],
                2: [CallbackQueryHandler(save_dept_id)],
                3: [CallbackQueryHandler(save_year)],
                4: [CallbackQueryHandler(save_sem)],
                5: [CallbackQueryHandler(delete_course)],
            },
            fallbacks=[CommandHandler("cancel", cancel)],
        )
    )  
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()
