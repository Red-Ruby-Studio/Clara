from time import sleep

import SaitamaRobot.modules.sql.users_sql as user_sql
from SaitamaRobot import DEV_USERS, OWNER_USERID, dispatcher
from SaitamaRobot.modules.helper_funcs.chat_status import dev_plus
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import BadRequest, Unauthorized
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    CommandHandler,
)


def get_invalid_chats(update: Update, context: CallbackContext, remove: bool = False):
    bot = context.bot
    chat_id = update.effective_chat.id
    chats = user_sql.get_all_chats()
    kicked_chats, progress = 0, 0
    chat_list = []
    progress_message = None

    for chat in chats:

        if ((100 * chats.index(chat)) / len(chats)) > progress:
            progress_bar = f"{progress}% completed in getting invalid chats."
            if progress_message:
                try:
                    bot.editMessageText(
                        progress_bar,
                        chat_id,
                        progress_message.message_id,
                    )
                except:
                    pass
            else:
                progress_message = bot.sendMessage(chat_id, progress_bar)
            progress += 5

        cid = chat.chat_id
        sleep(0.1)
        try:
            bot.get_chat(cid, timeout=60)
        except (BadRequest, Unauthorized):
            kicked_chats += 1
            chat_list.append(cid)
        except:
            pass

    try:
        progress_message.delete()
    except:
        pass

    if not remove:
        return kicked_chats
    else:
        for muted_chat in chat_list:
            sleep(0.1)
            user_sql.rem_chat(muted_chat)
        return kicked_chats


@dev_plus
def dbcleanup(update: Update, context: CallbackContext):
    msg = update.effective_message

    msg.reply_text("Getting invalid chat count ...")
    invalid_chat_count = get_invalid_chats(update, context)

    reply = f"Total invalid chats - {invalid_chat_count}\n"

    buttons = [[InlineKeyboardButton("Cleanup DB", callback_data="db_cleanup")]]

    update.effective_message.reply_text(
        reply,
        reply_markup=InlineKeyboardMarkup(buttons),
    )


def callback_button(update: Update, context: CallbackContext):
    bot = context.bot
    query = update.callback_query
    message = query.message
    chat_id = update.effective_chat.id
    query_type = query.data

    admin_list = [OWNER_USERID] + DEV_USERS

    bot.answer_callback_query(query.id)

    if query_type == "db_leave_chat":
        if query.from_user.id in admin_list:
            bot.editMessageText("Leaving chats ...", chat_id, message.message_id)
            chat_count = get_muted_chats(update, context, True)
            bot.sendMessage(chat_id, f"Left {chat_count} chats.")
        else:
            query.answer("You are not allowed to use this.")
    elif query_type == "db_cleanup":
        if query.from_user.id in admin_list:
            bot.editMessageText("Cleaning up DB ...", chat_id, message.message_id)
            invalid_chat_count = get_invalid_chats(update, context, True)
            reply = "Cleaned up {} chats from db.".format(invalid_chat_count)
            bot.sendMessage(chat_id, reply)
        else:
            query.answer("You are not allowed to use this.")


DB_CLEANUP_HANDLER = CommandHandler("dbcleanup", dbcleanup, run_async=True)
BUTTON_HANDLER = CallbackQueryHandler(callback_button, pattern="db_.*", run_async=True)

dispatcher.add_handler(DB_CLEANUP_HANDLER)
dispatcher.add_handler(BUTTON_HANDLER)

__mod_name__ = "DB Cleanup"
__handlers__ = [DB_CLEANUP_HANDLER, BUTTON_HANDLER]
