from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (CallbackQueryHandler, CommandHandler,
                          ConversationHandler, Filters, MessageFilter,
                          MessageHandler, Updater)

import database as db
import main

from .admin import back_inline_keyboard, confirm_reply_markup


class IntFilter(MessageFilter):
    def filter(self, message):
        if hasattr(message, "text"):
            return message.text.isdigit()


int_filter = IntFilter()


def add_course(update, context, is_back=False):
    if not is_back and not (
        db.is_superadmin(update.message.from_user)
        or db.is_admin(update.message.from_user)
    ):
        return
    keyboards = []

    schools = db.list_schools()
    for school_id, school_code in schools:
        keyboards.append([InlineKeyboardButton(school_code, callback_data=school_id)])
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Choose School",
        reply_markup=InlineKeyboardMarkup(keyboards),
    )
    return 1


def save_school_id_2(update, context):
    query = update.callback_query
    query.answer()
    context.user_data["school_id"] = int(query.data)
    sch_id = context.user_data["school_id"]
    keyboards = []

    departments = db.list_departments(sch_id)
    for deparment_id, dept_code in departments:
        keyboards.append([InlineKeyboardButton(dept_code, callback_data=deparment_id)])
    keyboards.append(back_inline_keyboard)
    # context.bot.send_message(chat_id=update.effective_chat.id, text="What is Name of the Course")
    query.edit_message_text(
        text="Choose department",
        reply_markup=InlineKeyboardMarkup(keyboards),
    )
    return 2


def save_school_id_3(update, context):
    query = update.callback_query
    query.answer()
    if query.data == "back":
        return add_course(update, context, is_back=True)
    context.user_data["departmet_id"] = int(query.data)
    query.edit_message_text(text="What is Name of the course")
    return 3


def save_course_name(update, context):

    context.user_data["course_name"] = update.message.text
    update.message.reply_text("What is course code of the course")
    return 4


def save_course_code(update, context):
    context.user_data["course_code"] = update.message.text
    update.message.reply_text("Send year")
    return 5


def save_year(update, context):
    if int_filter.filter(update.message):
        context.user_data["year"] = update.message.text
        update.message.reply_text("Put the semester")
        return 6
    update.message.reply_text("Please send integer")
    return 5


def save_sem(update, context):
    context.user_data["semester"] = update.message.text
    update.message.reply_text("send the file")
    return 7


def save_file_id(update, context):
    sem = context.user_data["semester"]
    file_id = update.message.document.file_id
    context.user_data["semester"] = update.message.text
    course_name = context.user_data["course_name"]
    course_code = context.user_data["course_code"]
    dept_id = context.user_data["departmet_id"]
    year = context.user_data["year"]
    db.add_course(course_code, course_name, sem, file_id, year, dept_id)
    update.message.reply_text("Course added successfully")
    return ConversationHandler.END


def remove_course(update, context):
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


def save_sch_id_r(update, context):
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


def save_dept_id1(update, context):
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


def save_year1(update, context):
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


def save_sem1(update, context):
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


def remove_course_warning(update, context):
    query = update.callback_query
    query.answer()
    if query.data == "back":
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

    context.user_data["cid"] = query.data
    query.edit_message_text(
        text="Are you sure to delete the Course?", reply_markup=confirm_reply_markup
    )
    return 6


def delete_course(update, context):
    query = update.callback_query
    query.answer()
    if query.data == "yes":
        cid = context.user_data["cid"]
        db.remove_course(cid)
        query.edit_message_text(text="Course Deleted Successfully")
    else:
        query.edit_message_text(text="Successfully cancelled")
    return ConversationHandler.END


def cancel(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text="Conversation Canceled Successfully "
    )
    return ConversationHandler.END


course_ch = ConversationHandler(
    entry_points=[CommandHandler("add_course", add_course)],
    states={
        1: [CallbackQueryHandler(save_school_id_2)],
        2: [CallbackQueryHandler(save_school_id_3)],
        3: [MessageHandler(Filters.text & ~Filters.command, save_course_name)],
        4: [MessageHandler(Filters.text & ~Filters.command, save_course_code)],
        5: [MessageHandler(Filters.text & ~Filters.command, save_year)],
        6: [MessageHandler(Filters.text & ~Filters.command, save_sem)],
        7: [MessageHandler(Filters.document, save_file_id)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

rem_cou = ConversationHandler(
    entry_points=[CommandHandler("remove_course", remove_course)],
    states={
        1: [CallbackQueryHandler(save_sch_id_r)],
        2: [CallbackQueryHandler(save_dept_id1)],
        3: [CallbackQueryHandler(save_year1)],
        4: [CallbackQueryHandler(save_sem1)],
        5: [CallbackQueryHandler(remove_course_warning)],
        6: [CallbackQueryHandler(delete_course)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
