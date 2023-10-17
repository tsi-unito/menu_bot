import logging
import datetime
import pytz
import telegram
from telegram.constants import ParseMode

import scraper
import json
from telegram import Update, BotCommand, Bot
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from ptbcontrib.ptb_jobstores.mongodb import PTBMongoDBJobStore
import os

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
for log_name, log_obj in logging.Logger.manager.loggerDict.items():
    if log_name == "httpx":
        log_obj.disabled = True


def remove_job_if_exists(name: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Remove job with given name. Returns whether job was removed."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False
    for job in current_jobs:
        job.schedule_removal()
    logging.info(f"removed job with name: {name}")
    return True


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if datetime.datetime.today().weekday() == 5 or datetime.datetime.today().weekday() == 6:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Oggi il ristorante è chiuso")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=scraper.get_menu(f"{update.message.text[1:]}")["text"], parse_mode=ParseMode.HTML)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   parse_mode=ParseMode.HTML,
                                   text="<i>Benvenuto nel bot del ristorante Doc&Dubai</i>\n\nPuoi richiedere i menu "
                                        "dei due ristoranti usando rispettivamente /doc e /dubai\n\n"
                                   "Per sottoscriverti al menù giornaliero usa /subscribe_doc o /subscribe_dubai "
                                        ", riceverai il menù alle 11:30 ogni giorno\n\n"
                                        "/help per mostrare questo messaggio")


async def menu_command_callback(context: ContextTypes.DEFAULT_TYPE):
    print(f"job: {context.job.name}")
    job = context.job
    await context.bot.send_message(chat_id=job.chat_id,
                                   text=scraper.get_menu(f"{job.data}")["text"], parse_mode=ParseMode.HTML)


async def subscription_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_message.chat_id
    text = (f"Sottoscrizione effettuata, riceverai il menù del {update.message.text[11:]} ogni giorno alle 11:30\n Per "
            f"cancellare la sottoscrizione scrivi /unsubscribe_{update.message.text[11:]}")
    try:
        if context.job_queue.get_jobs_by_name(f"{chat_id}_{update.message.text[11:]}"):
            text = f"Sei già sottoscritto al menù del {update.message.text[11:]}"

        else:
            context.job_queue.run_daily(menu_command_callback, days=(1, 2, 3, 4, 5),
                                        time=datetime.time(hour=11, minute=30, second=00,
                                                           tzinfo=pytz.timezone('Europe/Rome')),
                                        # Due to a bug Job_queue is skipping job if timezone is not provided for job.run_daily.
                                        chat_id=chat_id, user_id=update.effective_user.id,
                                        name=f"{chat_id}_{update.message.text[11:]}", data=update.message.text[11:])

    except (IndexError, ValueError):
        text = f'error: {ValueError}'

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=text)


async def unsubscription_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_message.chat_id
    remove_job_if_exists(f"{chat_id}_{update.message.text[13:]}", context)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=f"Sottoscrizione cancellata, non riceverai più il menù del {update.message.text[13:]}\n")


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="comando sconosciuto")

async def load_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.set_my_commands([
        BotCommand("doc", "Stampa menù del giorno del doc"),
        BotCommand("dubai", "Stampa menù del giorno del dubai"),
        BotCommand("subscribe_doc","ricevi il menù del doc ogni giorno"),
        BotCommand("subscribe_dubai","ricevi il menù del dubai ogni giorno"),
        BotCommand("unsubscribe_doc","non ricevere il menù del doc ogni giorno"),
        BotCommand("unsubscribe_dubai","non ricevere il menù del dubai ogni giorno"),
        BotCommand("help","mostra messaggio di benvenuto")
    ])

if __name__ == '__main__':
    if os.getenv("SECRETS") is None:
        os.environ["SECRETS"] = "secrets.json"

    with open(os.getenv("SECRETS"), "r") as file:
        config = json.load(file)

    if os.getenv("MONGO_USERNAME") is None:
        DB_URI = f"mongodb://{config['MONGO_USERNAME']}:{config['MONGO_PASSWORD']}@{config['MONGO_HOST']}:{config['MONGO_PORT']}/admin?retryWrites=true&w=majority"
    else:
        DB_URI = f"mongodb://{os.getenv('MONGO_USERNAME')}:{os.getenv('MONGO_PASSWORD')}@{os.getenv('MONGO_HOST')}:{os.getenv('MONGO_PORT')}/admin?retryWrites=true&w=majority"
    application = ApplicationBuilder().token(config['token']).build()

    application.job_queue.scheduler.add_jobstore(
        PTBMongoDBJobStore(
            application=application,
            host=DB_URI,
        )
    )

    for jobs in application.job_queue.jobs():
        print(jobs.name)

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', start))
    application.add_handler(CommandHandler('dubai', menu_command))
    application.add_handler(CommandHandler('doc', menu_command))
    application.add_handler(CommandHandler('subscribe_doc', subscription_command))
    application.add_handler(CommandHandler('subscribe_dubai', subscription_command))
    application.add_handler(CommandHandler('unsubscribe_doc', unsubscription_command))
    application.add_handler(CommandHandler('unsubscribe_dubai', unsubscription_command))
    application.add_handler(CommandHandler('set_commands', load_commands))
    application.add_handler(MessageHandler(filters.COMMAND, unknown))

    application.run_polling(allowed_updates=Update.ALL_TYPES)
