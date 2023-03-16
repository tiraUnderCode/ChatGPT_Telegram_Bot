# ChatGPT_Telegram_Bot

A simple A.I chat bot on Telegram using OpenAI API (model gpt-3.5-turbo)

Introduction to use this bot:

1. Create .env file and put your tokens for OPENAI_API_KEY and TELEGRAM_BOT_KEY

2. Install all packages that need (python-telegram-bot (version 13.7), openai (version latest), dotenv)

3. To run the bot in the background: **python3 bot.py &**

NOTE: The bot remembers maximum last 5 questions and 5 answers then reset data about history conversation, it will just remember the last question and the last answer
