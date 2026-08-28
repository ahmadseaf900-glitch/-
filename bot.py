import os
import time
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import requests
import telebot
from telebot import types

from aternos import (
    start_server,
    stop_server,
    restart_server,
    get_server_status,
    get_server_info,
)


# ============================================================
# ENVIRONMENT
# ============================================================

BOT_TOKEN = os.getenv(
    "BOT_TOKEN",
    ""
).strip()

DISCORD_TOKEN = os.getenv(
    "DISCORD_TOKEN",
    ""
).strip()

DISCORD_CHANNEL_ID = os.getenv(
    "DISCORD_CHANNEL_ID",
    ""
).strip()

PORT = int(
    os.getenv(
        "PORT",
        "10000"
    )
)

CONSOLE_WHITELIST = os.getenv(
    "CONSOLE_WHITELIST",
    "say,whitelist,list,online,save-all"
).strip()

# اختياري:
# اسم أمر بوت Discord الذي يستقبل أوامر Minecraft
DISCORD_CONSOLE_COMMAND = os.getenv(
    "DISCORD_CONSOLE_COMMAND",
    "!console"
).strip()


# ============================================================
# VALIDATION
# ============================================================

if not BOT_TOKEN:
    raise RuntimeError(
        "BOT_TOKEN غير موجود"
    )

if not DISCORD_TOKEN:
    raise RuntimeError(
        "DISCORD_TOKEN غير موجود"
    )

if not DISCORD_CHANNEL_ID:
    raise RuntimeError(
        "DISCORD_CHANNEL_ID غير موجود"
    )


# ============================================================
# TELEGRAM
# ============================================================

bot = telebot.TeleBot(
    BOT_TOKEN,
    parse_mode="HTML",
    threaded=True
)


# ============================================================
# DISCORD
# ============================================================

DISCORD_API = (
    "https://discord.com/api/v10"
)


def discord_headers():

    return {
        "Authorization":
            f"Bot {DISCORD_TOKEN}",

        "Content-Type":
            "application/json",

        "User-Agent":
            "Minecraft-Telegram-Bridge/1.0"
    }


def send_discord_message(text):

    response = requests.post(

        f"{DISCORD_API}/channels/"
        f"{DISCORD_CHANNEL_ID}/messages",

        headers=discord_headers(),

        json={
            "content": text
        },

        timeout=15
    )

    if response.status_code not in (
        200,
        201
    ):

        raise RuntimeError(
            f"Discord HTTP "
            f"{response.status_code}: "
            f"{response.text[:1000]}"
        )

    return response.json()


def test_discord():

    response = requests.get(

        f"{DISCORD_API}/users/@me",

        headers=discord_headers(),

        timeout=15
    )

    if response.status_code != 200:

        raise RuntimeError(
            f"Discord authentication HTTP "
            f"{response.status_code}: "
            f"{response.text[:1000]}"
        )

    return response.json()


# ============================================================
# DISCORD CONSOLE BRIDGE
# ============================================================

def send_console_to_discord(command):

    command = command.strip()

    if not command:
        raise ValueError(
            "الأمر فارغ"
        )

    return send_discord_message(
        f"{DISCORD_CONSOLE_COMMAND} {command}"
    )


# ============================================================
# KEYBOARD
# ============================================================

def main_keyboard():

    markup = types.InlineKeyboardMarkup(
        row_width=2
    )

    markup.add(

        types.InlineKeyboardButton(
            "▶️ تشغيل",
            callback_data="aternos_start"
        ),

        types.InlineKeyboardButton(
            "⏹️ إيقاف",
            callback_data="aternos_stop"
        )
    )

    markup.add(

        types.InlineKeyboardButton(
            "🔄 Restart",
            callback_data="aternos_restart"
        ),

        types.InlineKeyboardButton(
            "📊 Status",
            callback_data="aternos_status"
        )
    )

    markup.add(

        types.InlineKeyboardButton(
            "🖥️ Console",
            callback_data="console"
        ),

        types.InlineKeyboardButton(
            "🔐 Whitelist",
            callback_data="whitelist"
        )
    )

    markup.add(

        types.InlineKeyboardButton(
            "👥 Players",
            callback_data="players"
        )
    )

    return markup


# ============================================================
# FORMAT STATUS
# ============================================================

def format_status(data):

    return (
        "📊 <b>حالة السيرفر</b>\n\n"
        f"🌐 <code>{data.get('address')}</code>\n"
        f"📡 الحالة: <b>{data.get('status')}</b>\n"
        f"🎮 Software: <b>{data.get('software')}</b>\n"
        f"🔢 Version: <b>{data.get('version')}</b>"
    )


# ============================================================
# /START
# ============================================================

@bot.message_handler(
    commands=["start"]
)
def start_command(message):

    try:

        info = get_server_info()

        text = (
            "🤖 <b>Minecraft Server Manager</b>\n\n"
            f"🌐 <code>{info['address']}</code>\n"
            f"📡 الحالة: <b>{info['status']}</b>\n\n"
            "اختر العملية:"
        )

    except Exception as exc:

        text = (
            "🤖 <b>Minecraft Server Manager</b>\n\n"
            "⚠️ تعذر قراءة معلومات Aternos.\n\n"
            f"<code>{str(exc)[:500]}</code>"
        )

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=main_keyboard()
    )


# ============================================================
# START SERVER
# ============================================================

def do_start(chat_id):

    bot.send_message(
        chat_id,
        "▶️ <b>جاري تشغيل السيرفر...</b>"
    )

    try:

        data = start_server()

        bot.send_message(
            chat_id,
            "✅ <b>تم إرسال طلب تشغيل السيرفر.</b>\n\n"
            + format_status(data),
            reply_markup=main_keyboard()
        )

    except Exception as exc:

        bot.send_message(
            chat_id,

            "❌ <b>فشل تشغيل السيرفر</b>\n\n"
            f"<code>{str(exc)[:1000]}</code>",

            reply_markup=main_keyboard()
        )


# ============================================================
# STOP SERVER
# ============================================================

def do_stop(chat_id):

    bot.send_message(
        chat_id,
        "⏹️ <b>جاري إيقاف السيرفر...</b>"
    )

    try:

        data = stop_server()

        bot.send_message(
            chat_id,
            "✅ <b>تم إرسال طلب إيقاف السيرفر.</b>\n\n"
            + format_status(data),
            reply_markup=main_keyboard()
        )

    except Exception as exc:

        bot.send_message(
            chat_id,

            "❌ <b>فشل إيقاف السيرفر</b>\n\n"
            f"<code>{str(exc)[:1000]}</code>",

            reply_markup=main_keyboard()
        )


# ============================================================
# RESTART
# ============================================================

def do_restart(chat_id):

    bot.send_message(
        chat_id,
        "🔄 <b>جاري إعادة تشغيل السيرفر...</b>"
    )

    try:

        data = restart_server()

        bot.send_message(
            chat_id,

            "✅ <b>تم إرسال طلب Restart.</b>\n\n"
            + format_status(data),

            reply_markup=main_keyboard()
        )

    except Exception as exc:

        bot.send_message(
            chat_id,

            "❌ <b>فشل Restart</b>\n\n"
            f"<code>{str(exc)[:1000]}</code>",

            reply_markup=main_keyboard()
        )


# ============================================================
# STATUS
# ============================================================

def do_status(chat_id):

    try:

        data = get_server_info()

        bot.send_message(
            chat_id,

            format_status(data),

            reply_markup=main_keyboard()
        )

    except Exception as exc:

        bot.send_message(
            chat_id,

            "❌ <b>فشل الحصول على الحالة</b>\n\n"
            f"<code>{str(exc)[:1000]}</code>"
        )


# ============================================================
# CONSOLE
# ============================================================

def console_menu(chat_id):

    msg = bot.send_message(

        chat_id,

        "🖥️ <b>Console</b>\n\n"
        "أرسل أمر Minecraft الآن.\n\n"
        "الأوامر المسموحة من متغير "
        "<code>CONSOLE_WHITELIST</code>:\n"
        f"<code>{CONSOLE_WHITELIST}</code>"
    )

    bot.register_next_step_handler(
        msg,
        console_execute
    )


def console_execute(message):

    command = (
        message.text or ""
    ).strip()

    if not command:
        return

    command_name = (
        command.split()[0]
        .lower()
    )

    allowed = [

        x.strip().lower()

        for x in
        CONSOLE_WHITELIST.split(",")

        if x.strip()
    ]

    if (
        allowed
        and command_name not in allowed
    ):

        bot.send_message(

            message.chat.id,

            "🚫 <b>الأمر غير مسموح.</b>\n\n"
            f"المسموح:\n"
            f"<code>{CONSOLE_WHITELIST}</code>"
        )

        return

    try:

        send_console_to_discord(
            command
        )

        bot.send_message(

            message.chat.id,

            "🖥️ <b>Console</b>\n\n"
            f"📤 <code>{command}</code>\n\n"
            "✅ تم إرسال الأمر إلى Discord."
        )

    except Exception as exc:

        bot.send_message(

            message.chat.id,

            "❌ <b>فشل</b>\n\n"
            f"<code>{str(exc)[:1000]}</code>"
        )


# ============================================================
# PLAYERS
# ============================================================

def players_menu(chat_id):

    try:

        send_console_to_discord(
            "list"
        )

        bot.send_message(

            chat_id,

            "👥 <b>Players</b>\n\n"
            "📤 تم إرسال أمر <code>list</code> إلى Discord.\n\n"
            "ستحتاج أن يكون Discord Bot/DiscordSRV "
            "مضبوطًا لإرجاع النتيجة."
        )

    except Exception as exc:

        bot.send_message(

            chat_id,

            "❌ <b>فشل</b>\n\n"
            f"<code>{str(exc)[:1000]}</code>"
        )


# ============================================================
# WHITELIST
# ============================================================

def whitelist_menu(chat_id):

    markup = types.InlineKeyboardMarkup(
        row_width=2
    )

    markup.add(

        types.InlineKeyboardButton(
            "➕ إضافة",
            callback_data="wl_add"
        ),

        types.InlineKeyboardButton(
            "➖ حذف",
            callback_data="wl_remove"
        )
    )

    markup.add(

        types.InlineKeyboardButton(
            "📋 عرض",
            callback_data="wl_list"
        )
    )

    bot.send_message(

        chat_id,

        "🔐 <b>Whitelist</b>\n\n"
        "اختر العملية:",

        reply_markup=markup
    )


def whitelist_add(chat_id):

    msg = bot.send_message(
        chat_id,
        "➕ أرسل اسم اللاعب:"
    )

    bot.register_next_step_handler(
        msg,
        whitelist_add_execute
    )


def whitelist_add_execute(message):

    player = (
        message.text or ""
    ).strip()

    if not player:
        return

    try:

        send_console_to_discord(
            f"whitelist add {player}"
        )

        bot.send_message(

            message.chat.id,

            "✅ تم إرسال:\n"
            f"<code>whitelist add {player}</code>"
        )

    except Exception as exc:

        bot.send_message(

            message.chat.id,

            "❌ <b>فشل</b>\n\n"
            f"<code>{str(exc)[:1000]}</code>"
        )


def whitelist_remove(chat_id):

    msg = bot.send_message(
        chat_id,
        "➖ أرسل اسم اللاعب:"
    )

    bot.register_next_step_handler(
        msg,
        whitelist_remove_execute
    )


def whitelist_remove_execute(message):

    player = (
        message.text or ""
    ).strip()

    if not player:
        return

    try:

        send_console_to_discord(
            f"whitelist remove {player}"
        )

        bot.send_message(

            message.chat.id,

            "✅ تم إرسال:\n"
            f"<code>whitelist remove {player}</code>"
        )

    except Exception as exc:

        bot.send_message(

            message.chat.id,

            "❌ <b>فشل</b>\n\n"
            f"<code>{str(exc)[:1000]}</code>"
        )


def whitelist_list(chat_id):

    try:

        send_console_to_discord(
            "whitelist list"
        )

        bot.send_message(

            chat_id,

            "📋 تم إرسال:\n"
            "<code>whitelist list</code>"
        )

    except Exception as exc:

        bot.send_message(

            chat_id,

            "❌ <b>فشل</b>\n\n"
            f"<code>{str(exc)[:1000]}</code>"
        )


# ============================================================
# CALLBACKS
# ============================================================

@bot.callback_query_handler(
    func=lambda call: True
)
def callback_handler(call):

    chat_id = call.message.chat.id

    try:
        bot.answer_callback_query(
            call.id
        )
    except Exception:
        pass

    if call.data == "aternos_start":
        do_start(chat_id)
        return

    if call.data == "aternos_stop":
        do_stop(chat_id)
        return

    if call.data == "aternos_restart":
        do_restart(chat_id)
        return

    if call.data == "aternos_status":
        do_status(chat_id)
        return

    if call.data == "console":
        console_menu(chat_id)
        return

    if call.data == "players":
        players_menu(chat_id)
        return

    if call.data == "whitelist":
        whitelist_menu(chat_id)
        return

    if call.data == "wl_add":
        whitelist_add(chat_id)
        return

    if call.data == "wl_remove":
        whitelist_remove(chat_id)
        return

    if call.data == "wl_list":
        whitelist_list(chat_id)
        return


# ============================================================
# COMMANDS
# ============================================================

@bot.message_handler(
    commands=["status"]
)
def status_command(message):

    do_status(
        message.chat.id
    )


@bot.message_handler(
    commands=["console"]
)
def console_command(message):

    console_menu(
        message.chat.id
    )


@bot.message_handler(
    commands=["players"]
)
def players_command(message):

    players_menu(
        message.chat.id
    )


@bot.message_handler(
    commands=["whitelist"]
)
def whitelist_command(message):

    whitelist_menu(
        message.chat.id
    )


# ============================================================
# HEALTH SERVER
# ============================================================

class HealthHandler(
    BaseHTTPRequestHandler
):

    def do_GET(self):

        self.send_response(200)

        self.send_header(
            "Content-Type",
            "text/plain; charset=utf-8"
        )

        self.end_headers()

        self.wfile.write(
            b"Minecraft Telegram Manager is running."
        )

    def log_message(
        self,
        format,
        *args
    ):
        return


def run_health_server():

    server = ThreadingHTTPServer(
        ("0.0.0.0", PORT),
        HealthHandler
    )

    print(
        f"Health server running on port {PORT}"
    )

    server.serve_forever()


# ============================================================
# MAIN
# ============================================================

def run_bot():

    while True:

        try:

            print(
                "Telegram bot started."
            )

            bot.infinity_polling(

                timeout=30,

                long_polling_timeout=30,

                skip_pending=True
            )

        except Exception as exc:

            print(
                "Telegram polling error:",
                exc
            )

            time.sleep(5)


if __name__ == "__main__":

    print(
        "=========================================="
    )

    print(
        "Minecraft Telegram Manager"
    )

    print(
        "Aternos: ENABLED"
    )

    print(
        "Discord Bridge: ENABLED"
    )

    print(
        "Console: ENABLED"
    )

    print(
        "Whitelist: ENABLED"
    )

    print(
        "Players: ENABLED"
    )

    print(
        "=========================================="
    )

    # اختبار Discord عند التشغيل
    try:

        discord = test_discord()

        print(
            "Discord authenticated as:",
            discord.get("username")
        )

    except Exception as exc:

        print(
            "Discord authentication failed:",
            exc
        )

    threading.Thread(
        target=run_health_server,
        daemon=True
    ).start()

    run_bot()
