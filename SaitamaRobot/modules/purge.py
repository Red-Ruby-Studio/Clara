import asyncio

from more_itertools import chunked

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import MessageDeleteForbidden

from SaitamaRobot import pyrogram_app, PREFIX
from SaitamaRobot.modules.helper_funcs.pyro.chatstatus import is_user_admin


@pyrogram_app.on_message(filters.command("purge", PREFIX))
async def purge(client: Client, msg: Message):
    chat_id = msg.chat.id

    if not await is_user_admin(msg):
        await msg.reply_text("Only Admins are allowed to use this command")
        return

    if not (reply := msg.reply_to_message):
        await msg.reply_text(
            "Reply to a message to select where to start purging from."
        )
        return

    count = 0
    try:
        to_delete = msg.id - 1  # don't delete the command user sent
        from_delete = reply.id - 1  # delete the reply itself
        for m_ids in chunked(range(to_delete, from_delete, -1), 100):
            count += len(m_ids)
            await client.delete_messages(chat_id, m_ids)

        await msg.reply_text(f"Purged {count} messages.")

    except MessageDeleteForbidden:
        await msg.reply_text(
            "Failed to delete messages.\nSelected messages may be too old or you haven't given me enough admin rights!"
        )


@pyrogram_app.on_message(filters.command("del", PREFIX))
async def delete(_: Client, msg: Message) -> None:
    if is_user_admin(msg) and (reply := msg.reply_to_message):
        await reply.delete()
        await msg.delete()
    else:
        await msg.reply_text("Reply the command to some message.")


__help__ = """
Deleting a selected amount of messages are easy with this command. \
Bot purges messages all together or individually.
*Admin only:*
 × /purge: Deletes all messages between this and the replied to message.
 × /del: Deletes the messages replied to.
"""

__mod_name__ = "Purge"
