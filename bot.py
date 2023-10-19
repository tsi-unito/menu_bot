import logging
import datetime
import pytz
import telegram
from telegram.constants import ParseMode

import db_connector
import scraper
import json
from telegram import Update, BotCommand, Bot
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from ptbcontrib.ptb_jobstores.mongodb import PTBMongoDBJobStore
import os

global jobstore

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
for log_name, log_obj in logging.Logger.manager.loggerDict.items():
    if log_name == "httpx":
        log_obj.disabled = True


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if datetime.datetime.today().weekday() == 5 or datetime.datetime.today().weekday() == 6:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Oggi il ristorante è chiuso")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=scraper.get_menu(f"{update.message.text[1:]}")["text"],
                                       parse_mode=ParseMode.HTML)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db_connector.add_user(update.effective_user.id)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   parse_mode=ParseMode.HTML,
                                   text="<i>Benvenuto nel bot del ristorante Doc&Dubai</i>\n\nPuoi richiedere i menu "
                                        "dei due ristoranti usando rispettivamente /doc e /dubai\n\n"
                                        "Per iscriverti al menù giornaliero usa /subscribe_doc o /subscribe_dubai "
                                        ", riceverai il menù alle 11:30 ogni giorno\n\n"
                                        "/help per mostrare questo messaggio")


async def menu_command_callback(context: ContextTypes.DEFAULT_TYPE):
    print(f"job: {context.job.name}")
    job = context.job
    await context.bot.send_message(chat_id=job.chat_id,
                                   text=scraper.get_menu(f"{job.data}")["text"], parse_mode=ParseMode.HTML)


async def subscription_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_message.chat_id
    text = (f"Iscrizione effettuata, riceverai il menù del {update.message.text[11:]} ogni giorno alle 11:30\n Per "
            f"cancellare l' iscrizione scrivi /unsubscribe_{update.message.text[11:]}")
    try:
        if context.job_queue.get_jobs_by_name(f"{chat_id}_{update.message.text[11:]}"):
            text = f"Sei già iscritto al menù del {update.message.text[11:]}"
        else:
            db_connector.add_subscription(chat_id, update.message.text[11:])

    except (IndexError, ValueError):
        text = f'error: {ValueError}'

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=text)


async def unsubscription_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_message.chat_id
    db_connector.remove_subscription(chat_id, update.message.text[13:])
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=f"Iscrizione cancellata, non riceverai più il menù del {update.message.text[13:]}\n")


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="comando sconosciuto")


async def print_subscribers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    doc = list(db_connector.get_subscribers("doc"))
    dubai = list(db_connector.get_subscribers("dubai"))
    all = list(db_connector.get_subscribers("all"))

    #todo ottimizzabile ottenendo i dati direttamente da all con una sola chiamata al db
    message = (f"subscribers:\n\n"
               f"doc: {len(doc)}\n"
               f"dubai: {len(dubai)}\n\n")

    for uid in all:
        message += f"{uid[0]} {'Dubai,' if uid[2] == 1 else '' } {'Doc' if uid[1] == 1 else ''}\n"

    await context.bot.send_message(chat_id='532629429',
                                   text=message)


async def download_menus():
    scraper.download_menu("doc")
    scraper.download_menu("dubai")


async def send_menus():
    with open("menu_doc.json", "r") as f:
        menu_doc = json.load(f)
    with open("menu_dubai.json", "r") as f:
        menu_dubai = json.load(f)

    for uid in db_connector.get_subscribers("doc"):
        await application.bot.send_message(chat_id=uid, text=menu_doc["text"], parse_mode=ParseMode.HTML)
    for uid in db_connector.get_subscribers("dubai"):
        await application.bot.send_message(chat_id=uid, text=menu_dubai["text"], parse_mode=ParseMode.HTML)


async def load_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.set_my_commands([
        BotCommand("doc", "Stampa menù del giorno del doc"),
        BotCommand("dubai", "Stampa menù del giorno del dubai"),
        BotCommand("subscribe_doc", "ricevi il menù del doc ogni giorno"),
        BotCommand("subscribe_dubai", "ricevi il menù del dubai ogni giorno"),
        BotCommand("unsubscribe_doc", "non ricevere il menù del doc ogni giorno"),
        BotCommand("unsubscribe_dubai", "non ricevere il menù del dubai ogni giorno"),
        BotCommand("help", "mostra messaggio di benvenuto")
    ])


if __name__ == '__main__':
    if os.getenv("SECRETS") is None:
        os.environ["SECRETS"] = "secrets.json"

    with open(os.getenv("SECRETS"), "r") as file:
        config = json.load(file)

    application = ApplicationBuilder().token(config['token']).build()

    application.job_queue.run_daily(download_menus, days=(1, 2, 3, 4, 5),
                                    time=datetime.time(hour=11, minute=00, second=00,
                                                       tzinfo=pytz.timezone('Europe/Rome')))
    # Due to a bug Job_queue is skipping job if timezone is not provided for job.run_daily.

    application.job_queue.run_daily(send_menus, days=(1, 2, 3, 4, 5),
                                    time=datetime.time(hour=11, minute=30, second=00,
                                                       tzinfo=pytz.timezone('Europe/Rome')))

    db_connector.init()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', start))
    application.add_handler(CommandHandler('dubai', menu_command))
    application.add_handler(CommandHandler('doc', menu_command))
    application.add_handler(CommandHandler('subscribe_doc', subscription_command))
    application.add_handler(CommandHandler('subscribe_dubai', subscription_command))
    application.add_handler(CommandHandler('unsubscribe_doc', unsubscription_command))
    application.add_handler(CommandHandler('unsubscribe_dubai', unsubscription_command))
    application.add_handler(CommandHandler('subscribers', print_subscribers))
    application.add_handler(CommandHandler('set_commands', load_commands))
    application.add_handler(MessageHandler(filters.COMMAND, unknown))

    application.run_polling(allowed_updates=Update.ALL_TYPES)
