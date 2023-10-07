import logging
import datetime
import pytz
import scraper
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

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
                                       text=scraper.get_menu(f"{update.message.text[1:]}")["text"])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text="Bot in fase di costruzione e testing, please be patient\n")


async def menu_command_callback(context: ContextTypes.DEFAULT_TYPE):
    print(f"job: {context.job.name}")
    job = context.job
    await context.bot.send_message(chat_id=job.chat_id,
                                   text=scraper.get_menu(f"{job.data}")["text"])


async def subscription_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_message.chat_id
    text = (f"Sottoscrizione effettuata, riceverai il menù del {update.message.text[10:]} ogni giorno alle 11:30\n Per "
            f"cancellare la sottoscrizione scrivi /unsubscribe_{update.message.text[10:]}")
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
    job_removed = remove_job_if_exists(f"{chat_id}_{update.message.text[13:]}", context)
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=f"Sottoscrizione cancellata, non riceverai più il menù del {update.message.text[13:]}\n")


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="comando sconosciuto")


if __name__ == '__main__':
    with open("config.json", "r") as file:
        token = json.load(file)["token"]
    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('dubai', menu_command))
    application.add_handler(CommandHandler('doc', menu_command))
    application.add_handler(CommandHandler('subscribe_doc', subscription_command))
    application.add_handler(CommandHandler('subscribe_dubai', subscription_command))
    application.add_handler(CommandHandler('unsubscribe_doc', unsubscription_command))
    application.add_handler(CommandHandler('unsubscribe_dubai', unsubscription_command))
    application.add_handler(MessageHandler(filters.COMMAND, unknown))

    application.run_polling(allowed_updates=Update.ALL_TYPES)
    # https://github.com/python-telegram-bot/ptbcontrib/tree/main/ptbcontrib/ptb_jobstores persistent queue
