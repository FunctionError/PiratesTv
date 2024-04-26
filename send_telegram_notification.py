from telegram import Bot

bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')

bot = Bot(token=bot_token)
message = "M3U files updated by bot 🤖"
bot.send_message(chat_id=chat_id, text=message)
