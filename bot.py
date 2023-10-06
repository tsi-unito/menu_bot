import logging

import telegram

import scraper
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.ERROR
)


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text=scraper.get_menu(f"{update.message.text[1:]}")["text"])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Bot in fase di costruzione e testing, please be patient\n"
                                                                          "al momento ci sono solo 2 comandi: /dubai e /doc\n")


if __name__ == '__main__':
    with open("config.json", "r") as file:
        token = json.load(file)["token"]
    application = ApplicationBuilder().token(token).build()

    #telegram.Bot.set_my_commands([("/dubai" , "menu del dubai"),("/doc" , "menu del doc")])

    # Add handlers
    start_handler = CommandHandler('start', start)
    dubai_handler = CommandHandler('dubai', menu_command)
    doc_handler = CommandHandler('doc', menu_command)

    application.add_handler(start_handler)
    application.add_handler(dubai_handler)
    application.add_handler(doc_handler)


    application.run_polling()
