from datetime import datetime
import time
import os
import json
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# === Setup Secret Configuration ===
def secret():
    script_directory = os.path.dirname(os.path.abspath(__file__))
    secrets_path = os.path.join(script_directory, 'SECRETS.json')
    with open(secrets_path, 'r') as secrets_file:
        secrets = json.load(secrets_file)
    return secrets['id'], secrets['id_owner'], secrets['password'], secrets['token']

# === Globals ===
chat_id_waiting = []
chat_id_verified = {}
chat_id_banned = []
inverse_chat_id_verified = {}
qta = {}
seekers = {}
helpers = {}
matches = {}

chat_id_key, chat_id_owner, password, token = secret()

# === Core Functionalities ===
def qta_set(chat_id, answer):
    qta[chat_id] = {'answer': answer}

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
        "🛠 Available Commands:\n\n"
        "🔀 /seek [topic] – Find someone to talk to (e.g. /seek anxiety)\n"
        "🙏 /help [topic] – Offer your experience to help someone (e.g. /help burnout)\n"
        "🚪 /leave – Leave the current conversation\n"
        "🚨 /report – Report your chat partner\n"
        "📖 /help – View this message again\n\n"
        "You're not alone ❤️ We're here to help each other."
    )
    await context.bot.send_message(chat_id=update.effective_chat.id, text=help_text)

async def handle_matching(chat_id, topic, role, context):
    if role == 'seeker':
        seekers.setdefault(topic, []).append(chat_id)
        await context.bot.send_message(chat_id, f"Looking for a helper in '{topic}'...")
        if helpers.get(topic):
            helper_id = helpers[topic].pop(0)
            seekers[topic].remove(chat_id)
            matches[chat_id] = helper_id
            matches[helper_id] = chat_id
            await context.bot.send_message(chat_id, "You have been matched with someone willing to help!")
            await context.bot.send_message(helper_id, "You have been matched with someone who needs support!")
    elif role == 'helper':
        helpers.setdefault(topic, []).append(chat_id)
        await context.bot.send_message(chat_id, f"Waiting to support someone in '{topic}'...")
        if seekers.get(topic):
            seeker_id = seekers[topic].pop(0)
            helpers[topic].remove(chat_id)
            matches[chat_id] = seeker_id
            matches[seeker_id] = chat_id
            await context.bot.send_message(chat_id, "You have been matched with someone who needs support!")
            await context.bot.send_message(seeker_id, "You have been matched with someone who is here to help!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    chat_id = message.chat.id
    text = message.text.strip().lower() if message.text else ''

    if chat_id in chat_id_banned:
        await context.bot.send_message(chat_id, "Access removed. You are banned.")
        return

    if chat_id not in chat_id_verified.values():
        if chat_id not in chat_id_waiting:
            chat_id_waiting.append(chat_id)
            await context.bot.send_message(chat_id, 'Welcome to Hear2Help. Please enter the password.')
        elif text == password:
            user_tag = "/USER" + str(len(chat_id_verified) + 1)
            chat_id_verified[user_tag] = chat_id
            inverse_chat_id_verified[chat_id] = user_tag
            chat_id_waiting.remove(chat_id)

            keyboard = ReplyKeyboardMarkup(
                [["/seek anxiety", "/seek stress"], ["/help anxiety", "/help stress"]],
                resize_keyboard=True,
                one_time_keyboard=True
            )

            await context.bot.send_message(chat_id, (
                f"✅ You are verified as {user_tag}.\n\n"
                "What would you like to do today? Choose an option below or type your own command:"
            ), reply_markup=keyboard)
        else:
            await context.bot.send_message(chat_id, "❌ Incorrect password. Please try again.")
        return

    if text == "/start":
        await context.bot.send_message(chat_id, (
            "👋 Welcome to Hear2Help – Because being heard is the first step to healing.\n\n"
            "This is a safe, anonymous space where you can talk to someone or help others through shared experiences.\n\n"
            "🔐 To get started, please enter the access password."
        ))
    elif text == "/help":
        await help_command(update, context)
    elif text.startswith("/seek "):
        topic = text.split("/seek ", 1)[1].strip()
        await handle_matching(chat_id, topic, 'seeker', context)
    elif text.startswith("/help "):
        topic = text.split("/help ", 1)[1].strip()
        await handle_matching(chat_id, topic, 'helper', context)
    elif text == "/leave":
        if chat_id in matches:
            partner = matches.pop(chat_id)
            matches.pop(partner, None)
            await context.bot.send_message(chat_id, "You left the conversation.")
            await context.bot.send_message(partner, "The other user has left the conversation.")
    elif text == "/report":
        if chat_id in matches:
            partner = matches[chat_id]
            await context.bot.send_message(chat_id_owner, f"User {chat_id} reported {partner}")
            await context.bot.send_message(chat_id, "Your report has been submitted.")
    elif chat_id in matches:
        partner_id = matches[chat_id]
        if message.text:
            await context.bot.send_message(partner_id, message.text)
        elif message.photo:
            await context.bot.send_photo(partner_id, message.photo[-1].file_id, caption=message.caption)
        elif message.video:
            await context.bot.send_video(partner_id, message.video.file_id, caption=message.caption)

if __name__ == '__main__':
    app = ApplicationBuilder().token(token).build()
    app.add_handler(MessageHandler(filters.ALL, handle_message))

    print('Bot is listening...')
    app.run_polling()
