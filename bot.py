import os
import json
from datetime import datetime
import time
import telepot
from telepot.loop import MessageLoop

# Setup Secret Config
def secret():
    script_directory = os.path.dirname(os.path.abspath(__file__))
    secrets_path = os.path.join(script_directory, "SECRETS.json")
    with open(secrets_path, 'r') as secrets_file:
        secrets = json.load(secrets_file)
    return secrets['id'], secrets['id_owner'], secrets['password'], secrets['token']

# Global Variables
chat_id_waiting = []
chat_id_verified = {}
chat_id_banned = []
inverse_chat_id_verified = {}
qta = {}
seekers = {} # List of seekers
helpers = {} # List of helpers
matches = {} # chat_id --> partner_chat_id

chat_id_key, chat_id_owner, password, token = secret()
bot = telepot.Bot(token)

# Core Functions
def qta_set(chat_id, answer):
    qta[chat_id] = {'answer': answer}

def help(chat_id):
    help_text = (
        "/seek [topic] - Seek help for a specific stress (e.g /seek anxiety)\n"
        "/help [topic] - Offer help for a specific stress (e.g /help anxiety\n"
        "/leave - Leave the current chat\n"
        "/report - Report your current partner\n"
        "/help - Show this help message"
    )
    bot.sendMessage(chat_id, help_text)

def handle_matching(chat_id, topic, role):
    if role == "seeker":
        seekers.setDefault(topic, []).append(chat_id)
        bot.sendMessage(chat_id, f"Looking for a helper in '{topic}'...")
        if helpers.get(topic):
            helper_id = helpers[topic].pop(0)
            seekers[topic].remove(chat_id)
            matches[chat_id] = helper_id
            matches[helper_id] = chat_id
            bot.sendMessage(chat_id, "you have been matches with someone willing to help!")
            bot.sendMessage(helper_id, "You have been matched with someone who needs support!")
    elif role == "helper":
        helpers.setDefault(topic, []).append(chat_id)
        bot.sendMessage(chat_id, f"Waiting to support someone in '{topic}'...")
        if seekers.get(topic):
            seeker_id = seekers[topic].pop(0)
            helpers[topic].remove(chat_id)
            matches[chat_id] = seeker_id
            matches[seeker_id] = chat_id
            bot.sendMessage(chat_id, "You have been matched with someone who needs support!")
            bot.sendMessage(seeker_id, "You have been matched with someone willing to help!")
    else:
        bot.sendMessage(chat_id, "Invalid role. Please use 'seeker' or 'helper'.")

def handle_message(msg):
    content_type, _, chat_id = telepot.glance(msg)
    command = msg.get('text', '').strip().lower() if content_type == 'text' else ''

    if chat_id in chat_id_banned:
        bot.sendMessage(chat_id, "Access removed. You are banned.")
        return
    
    if chat_id not in chat_id_verified.values():
        if chat_id not in chat_id_waiting:
            chat_id_waiting.append(chat_id)
            bot.sendMessage(chat_id, 'Welcome to Hear2Help! Please enter the password.')
        elif command == password:
            user_tag = "/USER" + str(len(chat_id_verified) + 1)
            chat_id_verified[user_tag] = chat_id
            inverse_chat_id_verified[chat_id] = user_tag
            chat_id_waiting.remove(chat_id)
            bot.sendMessage(chat_id, f"You are verified as {user_tag}. Use /help to get started.")
        else:
            bot.sendMessage(chat_id, "Incorrect password. Please try again.")
        return

    # Handle registered user commands
    if command == "/help":
        help(chat_id)
    elif command.startswith("/seek "):
        topic = command.split("/seek", 1)[1].strip()
        handle_matching(chat_id, topic, 'seeker')
    elif command.startswith("/help"):
        topic = command.split("/help", 1)[1].strip()
        handle_matching(chat_id, topic, 'helper')
    elif command == "leave":
        if chat_id in matches:
            partner = matches.pop(chat_id)
            matches.pop(partner, None)
            bot.sendMessage(chat_id, "You left the chat.")
            bot.sendMessage(partner, "Your partner left the chat.")
    elif command == "report":
        if chat_id in matches:
            partner = matches[chat_id]
            bot.sendMessage(chat_id_owner, f"User {chat_id} reported {partner}")
            bot.sendMessage(chat_id, "Your report has been submitted.")
    elif chat_id in matches:
        partner_id = matches[chat_id]
        if content_type == 'text':
            bot.sendMessage(partner_id, msg['text'])
        elif content_type == 'photo' and 'photo' in msg:
            photo_id = msg['photo'][-1]['file_id']
            bot.sendPhoto(partner_id, photo_id, caption=msg.get("caption", ""))
        elif content_type == 'video' and 'video' in msg:
            video_id = msg['video']['file_id']
            bot.sendVideo(partner_id, video_id, caption=msg.get("caption", ""))

MessageLoop(bot, handle_message).run_as_thread()
print("Bot is listening...")

# for id_user in chat_id_key:
#     try:
#         bot.sendMessage(id_user, 'Hear2Help bot is online.')
#     except Exception as e:
#         print(f"Failed to message {id_user}: {e}")

while True:
    time.sleep(1)            