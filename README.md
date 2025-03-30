# 🤝 Anonymous Support Bot

A Telegram chatbot that enables anonymous one-on-one connections between individuals struggling with mental stress and those who've overcome similar experiences. The bot matches users based on shared topics (e.g. anxiety, burnout, grief) and facilitates private, anonymous support conversations.

---

## 🚀 Features

- `/seek [topic]` – Find someone to talk to about a specific mental health topic.
- `/help [topic]` – Offer support to others based on your experience.
- `/leave` – Exit a current anonymous chat.
- `/report` – Report your chat partner for inappropriate behavior.
- Anonymous message forwarding with full media support (text, photos, videos).

---

## 🛠 Setup Instructions

1. **Clone the repo**
   ```bash
   git clone https://github.com/YOUR_USERNAME/anonymous-support-bot.git
   cd anonymous-support-bot

2. **Create a virtual environment**
    python3 -m venv venv
    source venv/bin/activate

3. **Install dependencies**
    pip install -r requirements.txt

4. **Create your `SECRETS.json` file in the project root directory**
    ```ruby
    {
    "id": [123456789],  // list of allowed chat_ids (e.g., your own for testing)
    "id_owner": 123456789,
    "password": "your_password",
    "token": "your_telegram_bot_token"
    }
    ```

5. **Run the bot**
    python bot.py

## ⚠️ Disclaimer
This bot is designed to foster safe, supportive conversations but cannot replace professional therapy or emergency mental health services. Always seek professional help when needed.