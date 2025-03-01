# Don't Remove Credit @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot @Tech_VJ
# Ask Doubt on telegram @KingVJ01

import os
import string
import logging
import random
import asyncio
import time
import datetime
import re
import sys
import json
import base64

from Script import script
from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import *
from database.ia_filterdb import (
    col, sec_col, get_file_details, unpack_new_file_id, get_bad_files
)
from database.users_chats_db import (
    db, delete_all_referal_users, get_referal_users_count, get_referal_all_users, referal_add_user
)
from database.join_reqs import JoinReqs
from info import (
    CLONE_MODE, OWNER_LNK, REACTIONS, CHANNELS, REQUEST_TO_JOIN_MODE, TRY_AGAIN_BTN,
    ADMINS, SHORTLINK_MODE, PREMIUM_AND_REFERAL_MODE, STREAM_MODE, AUTH_CHANNEL,
    REFERAL_PREMEIUM_TIME, REFERAL_COUNT, PAYMENT_TEXT, PAYMENT_QR, LOG_CHANNEL, PICS,
    BATCH_FILE_CAPTION, CUSTOM_FILE_CAPTION, PROTECT_CONTENT, CHNL_LNK, GRP_LNK,
    REQST_CHANNEL, SUPPORT_CHAT, MAX_B_TN, VERIFY, SHORTLINK_API, SHORTLINK_URL,
    TUTORIAL, VERIFY_TUTORIAL, IS_TUTORIAL, URL
)
from utils import (
    get_settings, pub_is_subscribed, get_size, is_subscribed, save_group_settings, temp,
    verify_user, check_token, check_verification, get_token, get_shortlink, get_tutorial, get_seconds
)
from database.connections_mdb import active_connection
from urllib.parse import quote_plus
from TechVJ.util.file_properties import get_name, get_hash, get_media_file_size

logger = logging.getLogger(__name__)

BATCH_FILES = {}
join_db = JoinReqs

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    try:
        await message.react(emoji=random.choice(REACTIONS), big=True)
    except:
        pass

    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        buttons = [
            [
                InlineKeyboardButton(
                    '⤬ Add Me To Your Group ⤬',
                    url=f'http://t.me/{temp.U_NAME}?startgroup=true'
                )
            ],
            [
                InlineKeyboardButton('Support Group', url=f'https://t.me/{SUPPORT_CHAT}'),
                InlineKeyboardButton('Movie Group', url=GRP_LNK)
            ],
            [
                InlineKeyboardButton('Join Update Channel', url=CHNL_LNK)
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply(
            script.START_TXT.format(
                message.from_user.mention if message.from_user else message.chat.title,
                temp.U_NAME,
                temp.B_NAME
            ),
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
        await asyncio.sleep(2)

        if not await db.get_chat(message.chat.id):
            total = await client.get_chat_members_count(message.chat.id)
            await client.send_message(LOG_CHANNEL, script.LOG_TEXT_G.format(
                message.chat.title, message.chat.id, total, "Unknown"
            ))
            await db.add_chat(message.chat.id, message.chat.title)
        return
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(
            message.from_user.id, message.from_user.mention
        ))

    if len(message.command) != 2:
        buttons = [
            [
                InlineKeyboardButton(
                    '⤬ Add Me To Your Group ⤬',
                    url=f'http://t.me/{temp.U_NAME}?startgroup=true'
                )
            ],
            [
                InlineKeyboardButton('Movie Group', url=GRP_LNK)
            ],
            [
                InlineKeyboardButton('Help', callback_data='help'),
                InlineKeyboardButton('About', callback_data='about')
            ],
            [
                InlineKeyboardButton('Join Update Channel', url=CHNL_LNK)
            ]
        ]
        
        if CLONE_MODE:
            buttons.append([InlineKeyboardButton('Create Own Clone Bot', callback_data='clone')])

        reply_markup = InlineKeyboardMarkup(buttons)
        
        sticker_msg = await message.reply_sticker("CAACAgUAAxkBAAEKVaxlCWGs1Ri6ti45xliLiUeweCnu4AACBAADwSQxMYnlHW4Ls8gQMAQ")
        await asyncio.sleep(1)
        await sticker_msg.delete()

        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(
                message.from_user.mention, temp.U_NAME, temp.B_NAME
            ),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return

    if AUTH_CHANNEL and not await is_subscribed(client, message):
        try:
            invite_link = await client.create_chat_invite_link(
                chat_id=int(AUTH_CHANNEL),
                creates_join_request=REQUEST_TO_JOIN_MODE
            )
        except Exception as e:
            print(e)
            await message.reply_text("Make sure Bot is admin in Force-subscribe channel")
            return

        btn = [[InlineKeyboardButton("Backup Channel", url=invite_link.invite_link)]]

        if message.command[1] != "subscribe":
            try:
                kk, file_id = message.command[1].split("_", 1)
                btn.append([InlineKeyboardButton("↻ Try Again", callback_data=f"checksub#{kk}#{file_id}")])
            except (IndexError, ValueError):
                btn.append([InlineKeyboardButton("↻ Try Again", url=f"https://t.me/{temp.U_NAME}?start={message.command[1]}")])

        text = "**🕵️ You have not joined the backup channel. First, join the channel then try again.**"

        await client.send_message(
            chat_id=message.from_user.id,
            text=text,
            reply_markup=InlineKeyboardMarkup(btn),
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return
    if len(message.command) == 2 and message.command[1] in ["subscribe", "error", "okay", "help"]:
        buttons = [
            [
                InlineKeyboardButton(
                    '⤬ Add Me To Your Group ⤬',
                    url=f'http://t.me/{temp.U_NAME}?startgroup=true'
                )
            ],
            [
                InlineKeyboardButton('Movie Group', url=GRP_LNK)
            ],
            [
                InlineKeyboardButton('Help', callback_data='help'),
                InlineKeyboardButton('About', callback_data='about')
            ],
            [
                InlineKeyboardButton('Join Update Channel', url=CHNL_LNK)
            ]
        ]

        if CLONE_MODE:
            buttons.append([InlineKeyboardButton('Create Own Clone Bot', callback_data='clone')])

        reply_markup = InlineKeyboardMarkup(buttons)

        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(
                message.from_user.mention, temp.U_NAME, temp.B_NAME
            ),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        return

    data = message.command[1]

    if data.split("-", 1)[0] == "VJ":
        user_id = int(data.split("-", 1)[1])
        vj = await referal_add_user(user_id, message.from_user.id)

        if vj and PREMIUM_AND_REFERAL_MODE:
            await message.reply(f"<b>You have joined using the referral link of user with ID {user_id}\n\nSend /start again to use the bot</b>")
            num_referrals = await get_referal_users_count(user_id)

            await client.send_message(
                chat_id=user_id,
                text=f"<b>{message.from_user.mention} started the bot with your referral link\n\nTotal Referrals - {num_referrals}</b>"
            )

            if num_referrals == REFERAL_COUNT:
                expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=await get_seconds(REFERAL_PREMEIUM_TIME))
                user_data = {"id": user_id, "expiry_time": expiry_time}
                await db.update_user(user_data)
                await delete_all_referal_users(user_id)

                await client.send_message(
                    chat_id=user_id,
                    text=f"<b>You have successfully completed the total referral count.\n\nYou are now in Premium for {REFERAL_PREMEIUM_TIME}</b>"
                )
                return

        else:
            reply_markup = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        '⤬ Add Me To Your Group ⤬',
                        url=f'http://t.me/{temp.U_NAME}?startgroup=true'
                    )
                ],
                [
                    InlineKeyboardButton('Movie Group', url=GRP_LNK)
                ],
                [
                    InlineKeyboardButton('Help', callback_data='help'),
                    InlineKeyboardButton('About', callback_data='about')
                ],
                [
                    InlineKeyboardButton('Join Update Channel', url=CHNL_LNK)
                ]
            ])

            if CLONE_MODE:
                reply_markup.inline_keyboard.append([InlineKeyboardButton('Create Own Clone Bot', callback_data='clone')])

            sticker_msg = await message.reply_sticker("CAACAgUAAxkBAAEKVaxlCWGs1Ri6ti45xliLiUeweCnu4AACBAADwSQxMYnlHW4Ls8gQMAQ")
            await asyncio.sleep(1)
            await sticker_msg.delete()

            await message.reply_photo(
                photo=random.choice(PICS),
                caption=script.START_TXT.format(
                    message.from_user.mention, temp.U_NAME, temp.B_NAME
                ),
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
            return
    try:
        pre, file_id = data.split('_', 1)
    except ValueError:
        file_id = data
        pre = ""

    if data.startswith("BATCH-"):
        sts = await message.reply("<b>📂 Processing your request, please wait...</b>")
        file_id = data.split("-", 1)[1]
        msgs = BATCH_FILES.get(file_id)

        if not msgs:
            file = await client.download_media(file_id)
            try:
                with open(file) as file_data:
                    msgs = json.loads(file_data.read())
            except:
                await sts.edit("⚠️ Failed to process batch file.")
                return await client.send_message(LOG_CHANNEL, "⚠️ Unable to open batch file.")
            os.remove(file)
            BATCH_FILES[file_id] = msgs

        filesarr = []
        for msg in msgs:
            title = msg.get("title")
            size = get_size(int(msg.get("size", 0)))
            f_caption = msg.get("caption", "")

            if BATCH_FILE_CAPTION:
                try:
                    f_caption = BATCH_FILE_CAPTION.format(
                        file_name=title if title else '',
                        file_size=size if size else '',
                        file_caption=f_caption if f_caption else ''
                    )
                except:
                    f_caption = f_caption

            if f_caption is None:
                f_caption = f"{title}"

            try:
                if STREAM_MODE:
                    log_msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=msg.get("file_id"))
                    fileName = quote_plus(get_name(log_msg))
                    stream = f"{URL}watch/{str(log_msg.id)}/{fileName}?hash={get_hash(log_msg)}"
                    download = f"{URL}{str(log_msg.id)}/{fileName}?hash={get_hash(log_msg)}"

                    button = [[
                        InlineKeyboardButton("📥 Download", url=download),
                        InlineKeyboardButton("▶ Watch", url=stream)
                    ], [
                        InlineKeyboardButton("🌐 Watch in Web", web_app=WebAppInfo(url=stream))
                    ]]
                    reply_markup = InlineKeyboardMarkup(button)

                else:
                    button = [[
                        InlineKeyboardButton('⤬ Add Me To Your Group ⤬', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
                    ], [
                        InlineKeyboardButton('Movie Group', url=GRP_LNK)
                    ], [
                        InlineKeyboardButton('Help', callback_data='help'),
                        InlineKeyboardButton('About', callback_data='about')
                    ], [
                        InlineKeyboardButton('Join Update Channel', url=CHNL_LNK)
                    ]]
                    reply_markup = InlineKeyboardMarkup(button)

                msg = await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=msg.get("file_id"),
                    caption=f_caption,
                    protect_content=msg.get('protect', False),
                    reply_markup=reply_markup
                )
                filesarr.append(msg)

            except FloodWait as e:
                await asyncio.sleep(e.value)
                msg = await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=msg.get("file_id"),
                    caption=f_caption,
                    protect_content=msg.get('protect', False),
                    reply_markup=reply_markup
                )
                filesarr.append(msg)

            except:
                continue
            await asyncio.sleep(1)

        await sts.delete()
        k = await client.send_message(
            chat_id=message.from_user.id,
            text="<b>⚠️ Important Notice!</b>\n\n"
                 "🛑 This message will be deleted in <b>10 minutes</b> due to copyright issues. "
                 "Please forward it to your <b>Saved Messages</b> or another private chat."
        )
        await asyncio.sleep(600)
        for x in filesarr:
            await x.delete()
        await k.edit_text("<b>✅ Your message has been successfully deleted.</b>")
        return
    elif data.startswith("DSTORE-"):
        sts = await message.reply("<b>📂 Processing your request, please wait...</b>")
        b_string = data.split("-", 1)[1]
        decoded = (base64.urlsafe_b64decode(b_string + "=" * (-len(b_string) % 4))).decode("ascii")
        
        try:
            f_msg_id, l_msg_id, f_chat_id, protect = decoded.split("_", 3)
        except ValueError:
            f_msg_id, l_msg_id, f_chat_id = decoded.split("_", 2)
            protect = "/pbatch" if PROTECT_CONTENT else "batch"

        filesarr = []
        async for msg in client.iter_messages(int(f_chat_id), int(l_msg_id), int(f_msg_id)):
            if msg.media:
                media = getattr(msg, msg.media.value)
                file = getattr(msg, msg.media.value)
                size = get_size(int(file.file_size))
                file_name = getattr(media, 'file_name', '')
                f_caption = getattr(msg, 'caption', file_name)

                if BATCH_FILE_CAPTION:
                    try:
                        f_caption = BATCH_FILE_CAPTION.format(
                            file_name=file_name,
                            file_size=size if size else '',
                            file_caption=f_caption
                        )
                    except:
                        f_caption = getattr(msg, 'caption', '')

                file_id = file.file_id

                if STREAM_MODE:
                    log_msg = await client.send_cached_media(chat_id=LOG_CHANNEL, file_id=file_id)
                    fileName = quote_plus(get_name(log_msg))
                    stream = f"{URL}watch/{str(log_msg.id)}/{fileName}?hash={get_hash(log_msg)}"
                    download = f"{URL}{str(log_msg.id)}/{fileName}?hash={get_hash(log_msg)}"

                    button = [[
                        InlineKeyboardButton("📥 Download", url=download),
                        InlineKeyboardButton("▶ Watch", url=stream)
                    ], [
                        InlineKeyboardButton("🌐 Watch in Web", web_app=WebAppInfo(url=stream))
                    ]]
                    reply_markup = InlineKeyboardMarkup(button)
                else:
                    button = [[
                        InlineKeyboardButton('⤬ Add Me To Your Group ⤬', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
                    ], [
                        InlineKeyboardButton('Movie Group', url=GRP_LNK)
                    ], [
                        InlineKeyboardButton('Help', callback_data='help'),
                        InlineKeyboardButton('About', callback_data='about')
                    ], [
                        InlineKeyboardButton('Join Update Channel', url=CHNL_LNK)
                    ]]
                    reply_markup = InlineKeyboardMarkup(button)

                try:
                    p = await msg.copy(
                        message.chat.id,
                        caption=f_caption,
                        protect_content=True if protect == "/pbatch" else False,
                        reply_markup=reply_markup
                    )
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    p = await msg.copy(
                        message.chat.id,
                        caption=f_caption,
                        protect_content=True if protect == "/pbatch" else False,
                        reply_markup=reply_markup
                    )
                except:
                    continue

            elif msg.empty:
                continue
            else:
                try:
                    p = await msg.copy(
                        message.chat.id,
                        protect_content=True if protect == "/pbatch" else False
                    )
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                    p = await msg.copy(
                        message.chat.id,
                        protect_content=True if protect == "/pbatch" else False
                    )
                except:
                    continue

            filesarr.append(p)
            await asyncio.sleep(1)

        await sts.delete()
        k = await client.send_message(
            chat_id=message.from_user.id,
            text="<b>⚠️ Important Notice!</b>\n\n"
                 "🛑 This message will be deleted in <b>10 minutes</b> due to copyright issues. "
                 "Please forward it to your <b>Saved Messages</b> or another private chat."
        )
        await asyncio.sleep(600)
        for x in filesarr:
            await x.delete()
        await k.edit_text("<b>✅ Your message has been successfully deleted.</b>")
        return
    elif data.startswith("verify-"):
        user_id, token = data.split("-", 2)[1:]

        if str(message.from_user.id) != str(user_id):
            return await message.reply_text("<b>❌ Invalid or expired verification link.</b>", protect_content=True)

        is_valid = await check_token(client, user_id, token)

        if is_valid:
            text = (
                f"<b>👋 Hey {message.from_user.mention},</b>\n\n"
                "✅ You have successfully completed the verification.\n\n"
                "🔓 Now you have unlimited access for today! Enjoy!\n\n"
            )

            if PREMIUM_AND_REFERAL_MODE:
                text += (
                    "💎 If you want direct file access without any verification, "
                    "consider purchasing the bot subscription.\n\n"
                    "💶 Send /plan to buy a subscription."
                )

            await message.reply_text(text=text, protect_content=True)
            await verify_user(client, user_id, token)

        else:
            await message.reply_text("<b>❌ Invalid or expired verification link.</b>", protect_content=True)

        return

    elif data.startswith("sendfiles"):
        chat_id = int("-" + file_id.split("-")[1])
        settings = await get_settings(chat_id)
        pre = 'allfilesp' if settings['file_secure'] else 'allfiles'
        short_link = await get_shortlink(chat_id, f"https://telegram.me/{temp.U_NAME}?start={pre}_{file_id}")

        btn = [[InlineKeyboardButton('📥 Download Now', url=short_link)]]

        if settings['tutorial']:
            btn.append([InlineKeyboardButton('📖 How to Download', url=await get_tutorial(chat_id))])

        text = "<b>✅ Your file is ready! Click the button below to download:</b>\n\n"

        if PREMIUM_AND_REFERAL_MODE:
            text += (
                "💎 Want instant access without ads? Buy a subscription!\n\n"
                "💶 Send /plan to subscribe."
            )

        msg = await client.send_message(
            chat_id=message.from_user.id,
            text=text,
            reply_markup=InlineKeyboardMarkup(btn)
        )

        await asyncio.sleep(300)  # Auto-delete after 5 minutes
        await msg.edit("<b>✅ Your message has been deleted for privacy reasons.</b>")
        return
    elif data.startswith("short"):
        user = message.from_user.id
        chat_id = temp.SHORT.get(user)

        if chat_id is None:
            await message.reply_text("<b>🔍 Please search again in the group.</b>")
            return

        settings = await get_settings(chat_id)
        pre = 'filep' if settings['file_secure'] else 'file'

        if settings['is_shortlink'] and not await db.has_premium_access(user):
            short_link = await get_shortlink(chat_id, f"https://telegram.me/{temp.U_NAME}?start={pre}_{file_id}")
            btn = [[InlineKeyboardButton('📥 Download Now', url=short_link)]]

            if settings['tutorial']:
                btn.append([InlineKeyboardButton('📖 How to Download', url=await get_tutorial(chat_id))])

            text = "<b>✅ Your file is ready! Click the button below to download:</b>\n\n"

            if PREMIUM_AND_REFERAL_MODE:
                text += (
                    "💎 Want direct access without waiting? Buy a subscription!\n\n"
                    "💶 Send /plan to subscribe."
                )

            msg = await client.send_message(chat_id=message.from_user.id, text=text, reply_markup=InlineKeyboardMarkup(btn))
            await asyncio.sleep(1200)  # Auto-delete after 20 minutes
            await msg.edit("<b>✅ Your message has been deleted for privacy reasons.</b>")
            return
    elif data.startswith("all"):
        files = temp.GETALL.get(file_id)

        if not files:
            return await message.reply("<b>⚠️ No such file exists.</b>")

        filesarr = []
        for file in files:
            file_id = file["file_id"]
            file_details = await get_file_details(file_id)

            if not file_details:
                continue

            title = file_details["file_name"]
            size = get_size(file_details["file_size"])
            f_caption = file_details["caption"]

            if CUSTOM_FILE_CAPTION:
                try:
                    f_caption = CUSTOM_FILE_CAPTION.format(
                        file_name=title or '',
                        file_size=size or '',
                        file_caption=f_caption or ''
                    )
                except:
                    f_caption = f_caption

            if not f_caption:
                f_caption = f"{' '.join(filter(lambda x: not x.startswith('[') and not x.startswith('@'), title.split()))}"

            if not await db.has_premium_access(message.from_user.id):
                if not await check_verification(client, message.from_user.id) and VERIFY:
                    btn = [[
                        InlineKeyboardButton("✅ Verify", url=await get_token(client, message.from_user.id, f"https://telegram.me/{temp.U_NAME}?start="))
                    ], [
                        InlineKeyboardButton("📖 How to Verify", url=VERIFY_TUTORIAL)
                    ]]

                    text = "<b>👋 Hey {message.from_user.mention},\n\nYou are not verified today. Please click on Verify to get unlimited access for today.</b>"

                    if PREMIUM_AND_REFERAL_MODE:
                        text += "\n\n💎 Want direct file access without verification? Buy a subscription! 💶 Send /plan to subscribe."

                    await message.reply_text(text=text, protect_content=True, reply_markup=InlineKeyboardMarkup(btn))
                    return

            if STREAM_MODE:
                button = [[InlineKeyboardButton('▶ Stream & Download', callback_data=f'generate_stream_link:{file_id}')]]
                reply_markup = InlineKeyboardMarkup(button)
            else:
                button = [
                    [
                        InlineKeyboardButton('⤬ Add Me To Your Group ⤬', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
                    ],
                    [
                        InlineKeyboardButton('Movie Group', url=GRP_LNK)
                    ],
                    [
                        InlineKeyboardButton('Help', callback_data='help'),
                        InlineKeyboardButton('About', callback_data='about')
                    ],
                    [
                        InlineKeyboardButton('Join Update Channel', url=CHNL_LNK)
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(button)

            msg = await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=file_id,
                caption=f_caption,
                protect_content=True if pre == 'allfilesp' else False,
                reply_markup=reply_markup
            )
            filesarr.append(msg)

        k = await client.send_message(
            chat_id=message.from_user.id,
            text="<b>⚠️ Important Notice!</b>\n\n"
                 "🛑 This message will be deleted in <b>10 minutes</b> due to copyright issues. "
                 "Please forward it to your <b>Saved Messages</b> or another private chat."
        )
        await asyncio.sleep(600)
        for x in filesarr:
            await x.delete()
        await k.edit_text("<b>✅ Your message has been successfully deleted.</b>")
        return
    elif data.startswith("files"):
        user = message.from_user.id
        chat_id = temp.SHORT.get(user)

        if chat_id is None:
            await message.reply_text("<b>🔍 Please search again in the group.</b>")
            return

        settings = await get_settings(chat_id)
        pre = 'filep' if settings['file_secure'] else 'file'

        if settings['is_shortlink'] and not await db.has_premium_access(user):
            short_link = await get_shortlink(chat_id, f"https://telegram.me/{temp.U_NAME}?start={pre}_{file_id}")
            btn = [[InlineKeyboardButton('📥 Download Now', url=short_link)]]

            if settings['tutorial']:
                btn.append([InlineKeyboardButton('📖 How to Download', url=await get_tutorial(chat_id))])

            text = "<b>✅ Your file is ready! Click the button below to download:</b>\n\n"

            if PREMIUM_AND_REFERAL_MODE:
                text += (
                    "💎 Want direct access without waiting? Buy a subscription!\n\n"
                    "💶 Send /plan to subscribe."
                )

            msg = await client.send_message(chat_id=message.from_user.id, text=text, reply_markup=InlineKeyboardMarkup(btn))
            await asyncio.sleep(1200)  # Auto-delete after 20 minutes
            await msg.edit("<b>✅ Your message has been deleted for privacy reasons.</b>")
            return

    user = message.from_user.id
    file_details = await get_file_details(file_id)

    if not file_details:
        pre, file_id = ((base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))).decode("ascii")).split("_", 1)

        try:
            if not await db.has_premium_access(message.from_user.id):
                if not await check_verification(client, message.from_user.id) and VERIFY:
                    btn = [[
                        InlineKeyboardButton("✅ Verify", url=await get_token(client, message.from_user.id, f"https://telegram.me/{temp.U_NAME}?start="))
                    ], [
                        InlineKeyboardButton("📖 How to Verify", url=VERIFY_TUTORIAL)
                    ]]

                    text = "<b>👋 Hey {message.from_user.mention},\n\nYou are not verified today. Please click on Verify to get unlimited access for today.</b>"

                    if PREMIUM_AND_REFERAL_MODE:
                        text += "\n\n💎 Want direct file access without verification? Buy a subscription! 💶 Send /plan to subscribe."

                    await message.reply_text(text=text, protect_content=True, reply_markup=InlineKeyboardMarkup(btn))
                    return

            if STREAM_MODE:
                button = [[InlineKeyboardButton('▶ Stream & Download', callback_data=f'generate_stream_link:{file_id}')]]
                reply_markup = InlineKeyboardMarkup(button)
            else:
                button = [
                    [
                        InlineKeyboardButton('⤬ Add Me To Your Group ⤬', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
                    ],
                    [
                        InlineKeyboardButton('Movie Group', url=GRP_LNK)
                    ],
                    [
                        InlineKeyboardButton('Help', callback_data='help'),
                        InlineKeyboardButton('About', callback_data='about')
                    ],
                    [
                        InlineKeyboardButton('Join Update Channel', url=CHNL_LNK)
                    ]
                ]
                reply_markup = InlineKeyboardMarkup(button)

            msg = await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=file_id,
                protect_content=True if pre == 'filep' else False,
                reply_markup=reply_markup
            )

            file_type = msg.media
            file = getattr(msg, file_type.value)
            title = file.file_name
            size = get_size(file.file_size)
            f_caption = f"<code>{title}</code>"

            if CUSTOM_FILE_CAPTION:
                try:
                    f_caption = CUSTOM_FILE_CAPTION.format(
                        file_name=title or '',
                        file_size=size or '',
                        file_caption=''
                    )
                except:
                    pass

            await msg.edit_caption(caption=f_caption)

            btn = [[InlineKeyboardButton("✅ Get File Again ✅", callback_data=f'del#{file_id}')]]
            k = await msg.reply(
                text="<b>⚠️ Important Notice!</b>\n\n"
                     "🛑 This message will be deleted in <b>10 minutes</b> due to copyright issues. "
                     "Please forward it to your <b>Saved Messages</b> or another private chat.",
                reply_markup=InlineKeyboardMarkup(btn)
            )

            await asyncio.sleep(600)
            await msg.delete()
            await k.edit_text("<b>✅ Your message has been successfully deleted. Click below to get the file again.</b>", reply_markup=InlineKeyboardMarkup(btn))

            return
        except:
            pass

        return await message.reply('<b>⚠️ No such file exists.</b>')
@Client.on_message(filters.command('channel') & filters.user(ADMINS))
async def channel_info(bot, message):
    text = '📑 **Indexed channels/groups**\n'
    for channel in CHANNELS:
        chat = await bot.get_chat(channel)
        if chat.username:
            text += f'\n@{chat.username}'
        else:
            text += f'\n{chat.title or chat.first_name}'

    text += f'\n\n**Total:** {len(CHANNELS)}'

    if len(text) < 4096:
        await message.reply(text)
    else:
        file = 'Indexed_channels.txt'
        with open(file, 'w') as f:
            f.write(text)
        await message.reply_document(file)
        os.remove(file)


@Client.on_message(filters.command('logs') & filters.user(ADMINS))
async def log_file(bot, message):
    try:
        await message.reply_document('TELEGRAM_BOT.LOG')
    except Exception as e:
        await message.reply(str(e))


@Client.on_message(filters.command('delete') & filters.user(ADMINS))
async def delete(bot, message):
    reply = await bot.ask(message.from_user.id, "📂 Now send me the media file you want to delete.")
    
    if not reply.media:
        await message.reply('⚠️ Please send a valid media file (video, file, or document).', quote=True)
        return
    
    msg = await message.reply("⏳ Processing...", quote=True)

    for file_type in ("document", "video", "audio"):
        media = getattr(reply, file_type, None)
        if media is not None:
            break
    else:
        await msg.edit('❌ Unsupported file format.')
        return
    
    file_id, file_ref = unpack_new_file_id(media.file_id)
    result = col.delete_one({'file_id': file_id})
    
    if not result.deleted_count:
        result = sec_col.delete_one({'file_id': file_id})

    if result.deleted_count:
        await msg.edit('✅ File successfully deleted from the database.')
    else:
        file_name = re.sub(r"(_|-|\.|\+)", " ", str(media.file_name))
        unwanted_chars = ['[', ']', '(', ')']
        for char in unwanted_chars:
            file_name = file_name.replace(char, '')
        file_name = ' '.join(filter(lambda x: not x.startswith('@'), file_name.split()))

        result = col.delete_many({'file_name': file_name, 'file_size': media.file_size})

        if not result.deleted_count:
            result = sec_col.delete_many({'file_name': file_name, 'file_size': media.file_size})

        if result.deleted_count:
            await msg.edit('✅ File successfully deleted from the database.')
        else:
            await msg.edit('⚠️ File not found in the database.')


@Client.on_message(filters.command('deleteall') & filters.user(ADMINS))
async def delete_all_index(bot, message):
    await message.reply_text(
        '⚠️ This will delete all indexed files.\nDo you want to continue?',
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="✅ YES", callback_data="autofilter_delete")],
             [InlineKeyboardButton(text="❌ CANCEL", callback_data="close_data")]]
        ),
        quote=True,
    )


@Client.on_callback_query(filters.regex(r'^autofilter_delete'))
async def delete_all_index_confirm(bot, query):
    col.drop()
    sec_col.drop()
    await query.answer('🛑 Piracy is a crime!')
    await query.message.edit('✅ Successfully deleted all indexed files.')
@Client.on_message(filters.command('settings'))
async def settings(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"⚠️ You are an anonymous admin. Use /connect {message.chat.id} in PM.")

    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        grpid = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("⚠️ Make sure I'm present in your group!", quote=True)
                return
        else:
            await message.reply_text("⚠️ I'm not connected to any groups!", quote=True)
            return

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grp_id = message.chat.id
        title = message.chat.title
    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if (
        st.status not in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]
        and str(userid) not in ADMINS
    ):
        return

    settings = await get_settings(grp_id)

    # Ensure default settings exist
    if 'max_btn' not in settings:
        await save_group_settings(grp_id, 'max_btn', False)
        settings = await get_settings(grp_id)

    if 'is_shortlink' not in settings:
        await save_group_settings(grp_id, 'is_shortlink', False)

    buttons = [
        [
            InlineKeyboardButton('🔘 Result Page', callback_data=f'setgs#button#{settings["button"]}#{grp_id}'),
            InlineKeyboardButton('🔘 Button' if settings["button"] else '🔘 Text', callback_data=f'setgs#button#{settings["button"]}#{grp_id}')
        ],
        [
            InlineKeyboardButton('🔒 Protect Content', callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}'),
            InlineKeyboardButton('✔ ON' if settings["file_secure"] else '✘ OFF', callback_data=f'setgs#file_secure#{settings["file_secure"]}#{grp_id}')
        ],
        [
            InlineKeyboardButton('🎬 IMDb', callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}'),
            InlineKeyboardButton('✔ ON' if settings["imdb"] else '✘ OFF', callback_data=f'setgs#imdb#{settings["imdb"]}#{grp_id}')
        ],
        [
            InlineKeyboardButton('🔍 Spell Check', callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}'),
            InlineKeyboardButton('✔ ON' if settings["spell_check"] else '✘ OFF', callback_data=f'setgs#spell_check#{settings["spell_check"]}#{grp_id}')
        ],
        [
            InlineKeyboardButton('👋 Welcome Message', callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}'),
            InlineKeyboardButton('✔ ON' if settings["welcome"] else '✘ OFF', callback_data=f'setgs#welcome#{settings["welcome"]}#{grp_id}')
        ],
        [
            InlineKeyboardButton('🗑 Auto-Delete', callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{grp_id}'),
            InlineKeyboardButton('10 Mins' if settings["auto_delete"] else '✘ OFF', callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{grp_id}')
        ],
        [
            InlineKeyboardButton('📌 Auto-Filter', callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{grp_id}'),
            InlineKeyboardButton('✔ ON' if settings["auto_ffilter"] else '✘ OFF', callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{grp_id}')
        ],
        [
            InlineKeyboardButton('🔢 Max Buttons', callback_data=f'setgs#max_btn#{settings["max_btn"]}#{grp_id}'),
            InlineKeyboardButton('10' if settings["max_btn"] else f'{MAX_B_TN}', callback_data=f'setgs#max_btn#{settings["max_btn"]}#{grp_id}')
        ],
        [
            InlineKeyboardButton('🔗 ShortLink', callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{grp_id}'),
            InlineKeyboardButton('✔ ON' if settings["is_shortlink"] else '✘ OFF', callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{grp_id}')
        ]
    ]

    btn = [
        [
            InlineKeyboardButton("📂 Open Here", callback_data=f"opnsetgrp#{grp_id}"),
            InlineKeyboardButton("📬 Open in PM", callback_data=f"opnsetpm#{grp_id}")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(buttons)

    if chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        await message.reply_text(
            "<b>⚙ Do you want to open settings here?</b>",
            reply_markup=InlineKeyboardMarkup(btn),
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML,
            reply_to_message_id=message.id
        )
    else:
        await message.reply_text(
            f"<b>🔧 Change your settings for {title} as you wish.</b>",
            reply_markup=reply_markup,
            disable_web_page_preview=True,
            parse_mode=enums.ParseMode.HTML
        )
@Client.on_callback_query(filters.regex(r"^setgs#"))
async def callback_settings(client, query):
    _, setting, current_value, chat_id = query.data.split("#")

    chat_id = int(chat_id)
    new_value = False if current_value == "True" else True

    await save_group_settings(chat_id, setting, new_value)
    settings = await get_settings(chat_id)

    buttons = [
        [
            InlineKeyboardButton('🔘 Result Page', callback_data=f'setgs#button#{settings["button"]}#{chat_id}'),
            InlineKeyboardButton('🔘 Button' if settings["button"] else '🔘 Text', callback_data=f'setgs#button#{settings["button"]}#{chat_id}')
        ],
        [
            InlineKeyboardButton('🔒 Protect Content', callback_data=f'setgs#file_secure#{settings["file_secure"]}#{chat_id}'),
            InlineKeyboardButton('✔ ON' if settings["file_secure"] else '✘ OFF', callback_data=f'setgs#file_secure#{settings["file_secure"]}#{chat_id}')
        ],
        [
            InlineKeyboardButton('🎬 IMDb', callback_data=f'setgs#imdb#{settings["imdb"]}#{chat_id}'),
            InlineKeyboardButton('✔ ON' if settings["imdb"] else '✘ OFF', callback_data=f'setgs#imdb#{settings["imdb"]}#{chat_id}')
        ],
        [
            InlineKeyboardButton('🔍 Spell Check', callback_data=f'setgs#spell_check#{settings["spell_check"]}#{chat_id}'),
            InlineKeyboardButton('✔ ON' if settings["spell_check"] else '✘ OFF', callback_data=f'setgs#spell_check#{settings["spell_check"]}#{chat_id}')
        ],
        [
            InlineKeyboardButton('👋 Welcome Message', callback_data=f'setgs#welcome#{settings["welcome"]}#{chat_id}'),
            InlineKeyboardButton('✔ ON' if settings["welcome"] else '✘ OFF', callback_data=f'setgs#welcome#{settings["welcome"]}#{chat_id}')
        ],
        [
            InlineKeyboardButton('🗑 Auto-Delete', callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{chat_id}'),
            InlineKeyboardButton('10 Mins' if settings["auto_delete"] else '✘ OFF', callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{chat_id}')
        ],
        [
            InlineKeyboardButton('📌 Auto-Filter', callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{chat_id}'),
            InlineKeyboardButton('✔ ON' if settings["auto_ffilter"] else '✘ OFF', callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{chat_id}')
        ],
        [
            InlineKeyboardButton('🔢 Max Buttons', callback_data=f'setgs#max_btn#{settings["max_btn"]}#{chat_id}'),
            InlineKeyboardButton('10' if settings["max_btn"] else f'{MAX_B_TN}', callback_data=f'setgs#max_btn#{settings["max_btn"]}#{chat_id}')
        ],
        [
            InlineKeyboardButton('🔗 ShortLink', callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{chat_id}'),
            InlineKeyboardButton('✔ ON' if settings["is_shortlink"] else '✘ OFF', callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{chat_id}')
        ]
    ]

    reply_markup = InlineKeyboardMarkup(buttons)

    await query.message.edit_text(
        "<b>🔧 Settings Updated!</b>\n\nClick the buttons below to toggle features.",
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )
    await query.answer("✅ Setting updated successfully!")


@Client.on_callback_query(filters.regex(r"^opnsetgrp#"))
async def open_settings_group(client, query):
    _, chat_id = query.data.split("#")
    chat_id = int(chat_id)

    settings = await get_settings(chat_id)

    reply_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔙 Back", callback_data=f"close_data"),
            InlineKeyboardButton("🔧 Open in PM", callback_data=f"opnsetpm#{chat_id}")
        ]
    ])

    await query.message.edit_text(
        "<b>⚙️ Bot Settings</b>\n\nSelect a setting to modify:",
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )
    await query.answer("✅ Opened settings in group!")


@Client.on_callback_query(filters.regex(r"^opnsetpm#"))
async def open_settings_pm(client, query):
    _, chat_id = query.data.split("#")
    chat_id = int(chat_id)

    settings = await get_settings(chat_id)

    buttons = [
        [
            InlineKeyboardButton('🔘 Result Page', callback_data=f'setgs#button#{settings["button"]}#{chat_id}'),
            InlineKeyboardButton('🔘 Button' if settings["button"] else '🔘 Text', callback_data=f'setgs#button#{settings["button"]}#{chat_id}')
        ],
        [
            InlineKeyboardButton('🔒 Protect Content', callback_data=f'setgs#file_secure#{settings["file_secure"]}#{chat_id}'),
            InlineKeyboardButton('✔ ON' if settings["file_secure"] else '✘ OFF', callback_data=f'setgs#file_secure#{settings["file_secure"]}#{chat_id}')
        ],
        [
            InlineKeyboardButton("🔙 Back", callback_data=f"close_data")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(buttons)

    await query.message.edit_text(
        "<b>⚙️ Bot Settings</b>\n\nModify settings as per your preference:",
        reply_markup=reply_markup,
        parse_mode=enums.ParseMode.HTML
    )
    await query.answer("✅ Opened settings in private chat!")
@Client.on_callback_query(filters.regex(r"^close_data$"))
async def close_data(client, query):
    await query.message.delete()
    await query.answer("❌ Closed!")


@Client.on_message(filters.command("help"))
async def help_command(client, message):
    buttons = [
        [
            InlineKeyboardButton("📢 Updates", url=CHNL_LNK),
            InlineKeyboardButton("💬 Support", url=SUPPORT_CHAT)
        ],
        [
            InlineKeyboardButton("ℹ About", callback_data="about"),
            InlineKeyboardButton("👨‍💻 Developer", url=OWNER_LNK)
        ]
    ]

    reply_markup = InlineKeyboardMarkup(buttons)
    
    help_text = (
        "**🤖 Bot Commands Guide**\n\n"
        "Here are some useful commands:\n"
        "🔹 `/start` - Start the bot\n"
        "🔹 `/help` - Get this help message\n"
        "🔹 `/settings` - Configure bot settings\n"
        "🔹 `/channel` - View indexed channels\n"
        "🔹 `/logs` - Get bot logs (Admin only)\n"
        "🔹 `/delete` - Delete a file from the database (Admin only)\n"
        "🔹 `/deleteall` - Delete all indexed files (Admin only)\n"
        "\n"
        "💡 For more information, join our support group."
    )

    await message.reply_text(help_text, reply_markup=reply_markup, disable_web_page_preview=True)


@Client.on_callback_query(filters.regex("about"))
async def about_callback(client, query):
    buttons = [
        [InlineKeyboardButton("🔙 Back", callback_data="close_data")]
    ]
    
    about_text = (
        "**🤖 Bot Information**\n\n"
        "🔹 **Bot Name:** {bot_name}\n"
        "🔹 **Developer:** [Tech VJ](https://t.me/KingVJ01)\n"
        "🔹 **Library:** Pyrogram\n"
        "🔹 **Language:** Python 3\n"
        "🔹 **Hosted On:** VPS\n"
        "\n"
        "📢 Join our update channel for news and updates."
    ).format(bot_name=temp.B_NAME)

    await query.message.edit_text(about_text, reply_markup=InlineKeyboardMarkup(buttons), disable_web_page_preview=True)


@Client.on_message(filters.command("plan"))
async def subscription_plan(client, message):
    buttons = [
        [
            InlineKeyboardButton("💎 1 Month - ₹100", callback_data="subscribe_1m"),
            InlineKeyboardButton("💎 3 Months - ₹250", callback_data="subscribe_3m")
        ],
        [
            InlineKeyboardButton("💎 6 Months - ₹450", callback_data="subscribe_6m"),
            InlineKeyboardButton("💎 1 Year - ₹800", callback_data="subscribe_1y")
        ],
        [
            InlineKeyboardButton("📢 Contact Admin", url=OWNER_LNK)
        ]
    ]

    text = (
        "**💎 Subscription Plans**\n\n"
        "🚀 Get premium access and enjoy benefits like:\n"
        "✔ No verification required\n"
        "✔ Direct file access\n"
        "✔ No shortlinks or ads\n\n"
        "💰 Choose a plan below to subscribe."
    )

    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex(r"subscribe_\d+[m|y]"))
async def subscribe_user(client, query):
    plan = query.data.split("_")[1]

    if plan == "1m":
        duration = "1 Month"
        price = "₹100"
    elif plan == "3m":
        duration = "3 Months"
        price = "₹250"
    elif plan == "6m":
        duration = "6 Months"
        price = "₹450"
    elif plan == "1y":
        duration = "1 Year"
        price = "₹800"

    text = (
        f"**💎 Subscription Plan: {duration}**\n"
        f"💰 Price: {price}\n\n"
        "📌 To subscribe, please contact the admin."
    )

    await query.message.edit_text(text, reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("📢 Contact Admin", url=OWNER_LNK)]
    ]))


@Client.on_message(filters.command("verify"))
async def manual_verification(client, message):
    if await check_verification(client, message.from_user.id):
        await message.reply("✅ You are already verified for today!")
    else:
        verify_link = await get_token(client, message.from_user.id, f"https://telegram.me/{temp.U_NAME}?start=")
        btn = [[InlineKeyboardButton("✅ Verify Now", url=verify_link)]]
        text = (
            "**🔑 Verification Required**\n\n"
            "📌 Click the button below to verify and get unlimited access for today.\n"
            "💡 If you face issues, refer to the tutorial."
        )
        await message.reply_text(text, reply_markup=InlineKeyboardMarkup(btn))


@Client.on_message(filters.command("donate"))
async def donate_info(client, message):
    buttons = [[InlineKeyboardButton("💰 Donate Now", url=OWNER_LNK)]]
    
    text = (
        "**🙏 Support Our Project**\n\n"
        "💡 If you like this bot and want to support its development, "
        "consider making a donation. Your support helps keep this service running.\n\n"
        "📢 Click the button below to donate."
    )

    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_message(filters.command("feedback"))
async def feedback_request(client, message):
    buttons = [
        [InlineKeyboardButton("👍 Good", callback_data="feedback_good"), InlineKeyboardButton("👎 Bad", callback_data="feedback_bad")],
        [InlineKeyboardButton("✍ Write a Review", url=f"https://t.me/{temp.U_NAME}")]
    ]

    text = "**📝 We value your feedback!**\n\nPlease rate your experience using this bot."

    await message.reply_text(text, reply_markup=InlineKeyboardMarkup(buttons))


@Client.on_callback_query(filters.regex("feedback_good"))
async def feedback_good(client, query):
    await query.answer("😊 Thank you for your positive feedback!")
    await query.message.edit_text("✅ Thank you for your positive feedback! 🎉")


@Client.on_callback_query(filters.regex("feedback_bad"))
async def feedback_bad(client, query):
    await query.answer("😢 We're sorry to hear that. Let us know how we can improve!")
    await query.message.edit_text("❌ Sorry to hear that. Let us know how we can improve!")

@Client.on_message(filters.command("broadcast") & filters.user(ADMINS))
async def broadcast_message(client, message):
    if not message.reply_to_message:
        return await message.reply_text("⚠️ Please reply to a message to broadcast.")

    msg = message.reply_to_message
    users = await db.get_all_users()
    count = 0

    for user in users:
        try:
            await msg.copy(user["id"])
            count += 1
            await asyncio.sleep(0.5)
        except Exception:
            pass

    await message.reply_text(f"✅ Broadcast completed. Message sent to {count} users.")


@Client.on_message(filters.command("stats") & filters.user(ADMINS))
async def bot_statistics(client, message):
    user_count = await db.total_users_count()
    group_count = await db.total_chats_count()

    text = (
        f"📊 **Bot Statistics**\n\n"
        f"👤 **Total Users:** {user_count}\n"
        f"👥 **Total Groups:** {group_count}\n"
    )

    await message.reply_text(text)


@Client.on_message(filters.command("ban") & filters.user(ADMINS))
async def ban_user(client, message):
    if not message.reply_to_message:
        return await message.reply_text("⚠️ Reply to a user’s message to ban them.")

    user_id = message.reply_to_message.from_user.id
    await db.ban_user(user_id)
    await message.reply_text(f"🚫 User {user_id} has been banned.")


@Client.on_message(filters.command("unban") & filters.user(ADMINS))
async def unban_user(client, message):
    if len(message.command) < 2:
        return await message.reply_text("⚠️ Provide a user ID to unban.")

    user_id = int(message.command[1])
    await db.unban_user(user_id)
    await message.reply_text(f"✅ User {user_id} has been unbanned.")


@Client.on_message(filters.command("banned") & filters.user(ADMINS))
async def banned_users_list(client, message):
    banned_users = await db.get_banned_users()
    if not banned_users:
        return await message.reply_text("✅ No banned users.")

    text = "**🚫 Banned Users:**\n"
    for user in banned_users:
        text += f"• `{user['id']}`\n"

    await message.reply_text(text)


@Client.on_message(filters.command("ping"))
async def ping_command(client, message):
    start_time = time.time()
    msg = await message.reply_text("🏓 Pong...")
    end_time = time.time()
    latency = round((end_time - start_time) * 1000, 2)
    await msg.edit(f"🏓 Pong! `{latency}ms`")


async def main():
    await db.init_db()
    print("✅ Bot is running!")


if __name__ == "__main__":
    asyncio.run(main())
