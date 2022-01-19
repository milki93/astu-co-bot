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


class IntFilter(MessageFilter):
    def filter(self, message):
        if hasattr(message, "text"):
            return message.text.isdigit()


int_filter = IntFilter()


ADMIN_MSG = """/add_admin - To add admins.
/list_admins - To list admin.
/remove_admin - To remove admin."""

SUPERADMIN_MSG = """/add_school - to add school.
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


# def remove_school(update, context):
#     if not db.is_superadmin(update.message.from_user):
#         return
#     keybords = []
#     schools = db.list_schools()
#     if schools == []:
#         context.bot.send_message(
#             chat_id=update.effective_chat.id, text="There are no Schools"
#         )
#     else:
#         for school_id, school_code in schools:
#             keybords.append([InlineKeyboardButton(school_code, callback_data=school_id)])
#         context.bot.send_message(
#             chat_id=update.effective_chat.id,
#             text="Select School?",
#             reply_markup=InlineKeyboardMarkup(keybords),
#         )
#         return 1

# def remove_school_warning(update, context):
#     query = update.callback_query
#     query.answer()
#     context.user_data["school_id"] = int(query.data)

#     query.edit_message_text(
#         text="Are you sure to delete the School?",
#         reply_markup=confirm_reply_markup
#     )
#     return 2

# def remove_school_id(update, context):
#     query = update.callback_query
#     query.answer()
#     if query.data == "yes":
#         school_id = context.user_data["school_id"]
#         db.remove_school(school_id)
#         query.edit_message_text(
#             text="School Deleted Successfully"
#         )
#     else:
#         query.edit_message_text(
#             text="Successfully cancelled"
#         )
#     return ConversationHandler.END


# def remove_department(update, context):
#     if not db.is_superadmin(update.message.from_user):
#         return
#     keybords = []
#     schools = db.list_schools()
#     if schools == []:
#         context.bot.send_message(
#             chat_id=update.effective_chat.id, text="There are no schools"
#         )
#     else:
#         for school_id, school_code in schools:
#             keybords.append([InlineKeyboardButton(school_code, callback_data=school_id)])
#         context.bot.send_message(
#                 chat_id=update.effective_chat.id,
#                 text="Select School?",
#                 reply_markup=InlineKeyboardMarkup(keybords),
#             )

#         return 1


# def save_school_id(update, context):
#     query = update.callback_query
#     query.answer()
#     context.user_data["school_id"] = int(query.data)
#     sch_id = context.user_data["school_id"]
#     keyboards = []
#     keyboards.append(back_inline_keyboard)
#     departments = db.list_departments(sch_id)
#     if departments == []:
#         query.edit_message_text(
#          text="There are no departments"
#         )
#     else:
#         for department_id, dept_code in departments:
#             keyboards.append([InlineKeyboardButton(dept_code, callback_data=department_id)])
#         query.edit_message_text(
#             text="Select department",
#             reply_markup=InlineKeyboardMarkup(keyboards),
#         )
#         return 2
# def remove_deparment_warning(update, context):
#     query = update.callback_query
#     query.answer()
#     if query.data == "back":
#         schools = db.list_schools()
#         keybords = []
#         for school_id, school_code in schools:
#             keybords.append([InlineKeyboardButton(school_code, callback_data=school_id)])
#             query.edit_message_text(
#             text="Select School?",
#             reply_markup=InlineKeyboardMarkup(keybords),
#         )
#         return 1
#     keyboards=[]
#     keyboards.append(back_inline_keyboard)
#     context.user_data["department_id"] = int(query.data)
#     query.edit_message_text(
#         text="Are you sure to delete the Department?",
#         reply_markup=confirm_reply_markup
#     )
#     return 3

# def remove_d_id(update, context):
#     query = update.callback_query
#     query.answer()
#     if query.data == "back":
#         departments = db.list_departments()
#         keybords = []
#         for deparment_id, dept_code in departments:
#             keybords.append([InlineKeyboardButton(dept_code, callback_data=deparment_id)])
#             query.edit_message_text(
#             text="Select department?",
#             reply_markup=InlineKeyboardMarkup(keybords),
#         )
#         return 1
#     if query.data == "yes":
#         dep_id = context.user_data["department_id"]
#         db.remove_department(dep_id)
#         query.edit_message_text(
#             text="Department Deleted Successfully"
#         )
#     else:
#         query.edit_message_text(
#             text="Successfully cancelled"
#         )
#     return ConversationHandler.END


# def add_school(update, context):
#     if not (
#         db.is_superadmin(update.message.from_user)
#         or db.is_admin(update.message.from_user)
#     ):
#         return
#     context.bot.send_message(
#         chat_id=update.effective_chat.id, text="What is the name the school?"
#     )
#     return 1


# def save_school_name(update, context):
#     context.user_data["school_name"] = update.message.text
#     update.message.reply_text("What is Short Name of the school")
#     return 2


# def save_school_short_name(update, context):
#     school_name = context.user_data["school_name"]
#     school_short_name = update.message.text
#     db.add_school(school_name, school_short_name)
#     update.message.reply_text("School added successfully")

#     return ConversationHandler.END


# def add_department(update, context):
#     if not (
#         db.is_superadmin(update.message.from_user)
#         or db.is_admin(update.message.from_user)
#     ):
#         return
#     keybords = []
#     schools = db.list_schools()
#     for school_id, school_code in schools:
#         keybords.append([InlineKeyboardButton(school_code, callback_data=school_id)])
#     context.bot.send_message(
#         chat_id=update.effective_chat.id,
#         text="Select School?",
#         reply_markup=InlineKeyboardMarkup(keybords),
#     )
#     return 1


# def save_school_id_1(update, context):
#     query = update.callback_query
#     query.answer()
#     context.user_data["school_id"] = int(query.data)
#     context.bot.send_message(
#         chat_id=update.effective_chat.id, text="What is Name of the Department"
#     )
#     return 2


# def save_department_name(update, context):

#     context.user_data["department_name"] = update.message.text
#     update.message.reply_text("What is Short Name of the Department")
#     return 3


# def save_department_short_name(update, context):
#     dept_short_name = update.message.text
#     department_name = context.user_data["department_name"]
#     school_id = context.user_data["school_id"]
#     db.add_department(department_name, dept_short_name, school_id)
#     update.message.reply_text("Department added successfully")
#     return ConversationHandler.END


# def cancel(update, context):
#     context.bot.send_message(
#         chat_id=update.effective_chat.id,
#         text="Conversation Canceled Successfully "
#     )
#     return ConversationHandler.END


# def add_course(update, context, is_back=False):
#     if not is_back and not (
#         db.is_superadmin(update.message.from_user)
#         or db.is_admin(update.message.from_user)
#     ):
#         return
#     keyboards = []

#     schools = db.list_schools()
#     for school_id, school_code in schools:
#         keyboards.append([InlineKeyboardButton(school_code, callback_data=school_id)])
#     context.bot.send_message(
#         chat_id=update.effective_chat.id,
#         text="Choose School",
#         reply_markup=InlineKeyboardMarkup(keyboards),
#     )
#     return 1


# def save_school_id_2(update, context):
#     query = update.callback_query
#     query.answer()
#     context.user_data["school_id"] = int(query.data)
#     sch_id = context.user_data["school_id"]
#     keyboards = []

#     departments = db.list_departments(sch_id)
#     for deparment_id, dept_code in departments:
#         keyboards.append([InlineKeyboardButton(dept_code, callback_data=deparment_id)])
#     keyboards.append(back_inline_keyboard)
#     # context.bot.send_message(chat_id=update.effective_chat.id, text="What is Name of the Course")
#     query.edit_message_text(
#         text="Choose department",
#         reply_markup=InlineKeyboardMarkup(keyboards),
#     )
#     return 2


# def save_school_id_3(update, context):
#     query = update.callback_query
#     query.answer()
#     if query.data == "back":
#         return add_course(update, context, is_back=True)
#     context.user_data["departmet_id"] = int(query.data)
#     query.edit_message_text(text="What is Name of the course")
#     return 3


# def save_course_name(update, context):

#     context.user_data["course_name"] = update.message.text
#     update.message.reply_text("What is course code of the course")
#     return 4


# def save_course_code(update, context):
#     context.user_data["course_code"] = update.message.text
#     update.message.reply_text("Send year")
#     return 5


# def save_year(update, context):
#     if int_filter.filter(update.message):
#         context.user_data["year"] = update.message.text
#         update.message.reply_text("Put the semester")
#         return 6
#     update.message.reply_text("Please send integer")
#     return 5


# def save_sem(update, context):
#     context.user_data["semester"] = update.message.text
#     update.message.reply_text("send the file")
#     return 7


# def save_file_id(update, context):
#     sem = context.user_data["semester"]
#     file_id = update.message.document.file_id
#     context.user_data["semester"] = update.message.text
#     course_name = context.user_data["course_name"]
#     course_code = context.user_data["course_code"]
#     dept_id = context.user_data["departmet_id"]
#     year = context.user_data["year"]
#     db.add_course(course_code, course_name, sem, file_id, year, dept_id)
#     update.message.reply_text("Course added successfully")
#     return ConversationHandler.END


school_ch = ConversationHandler(
    entry_points=[CommandHandler("add_school", add_school)],
    states={
        1: [MessageHandler(Filters.text & ~Filters.command, save_school_name)],
        2: [MessageHandler(Filters.text & ~Filters.command, save_school_short_name)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

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
rem_sch_ch = ConversationHandler(
    entry_points=[CommandHandler("remove_school", remove_school)],
    states={
        1: [CallbackQueryHandler(remove_school_warning)],
        2: [CallbackQueryHandler(remove_school_id)],
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
