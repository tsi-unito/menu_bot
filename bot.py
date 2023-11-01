import logging
import datetime
import pytz
import sqlalchemy
from sqlalchemy import create_engine, MetaData, Table, Column, inspect
from sqlalchemy.orm import Session
from telegram.constants import ParseMode

import scraper
import json
from telegram import Update, BotCommand, Bot, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import os
from sql_alchemy.database_connect import BotUser, Base

global engine

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
for log_name, log_obj in logging.Logger.manager.loggerDict.items():
    if log_name == "httpx":
        log_obj.disabled = True


def add_user(uid: int):
    global engine
    with Session(engine) as session:
        if not session.query(BotUser).filter(BotUser.uid == uid).first():
            session.add(BotUser(uid=uid))
            session.commit()

def grid

    keyboard = [
        [KeyboardButton('Start Dubai'), KeyboardButton('Stop Dubai')],
        [KeyboardButton('Start Doc'), KeyboardButton('Stop Doc')],
        [KeyboardButton('Stop'), KeyboardButton('HELP')],
        [KeyboardButton('Autori'), KeyboardButton('FAQ')]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    return reply_markup
async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if datetime.datetime.today().weekday() == 5 or datetime.datetime.today().weekday() == 6:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text="Oggi il ristorante è chiuso")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=scraper.get_menu(f"{update.message.text[1:]}")["text"],
                                       parse_mode=ParseMode.HTML, disable_web_page_preview=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # db_connector.add_user(update.effective_user.id)
    add_user(update.effective_user.id)

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   parse_mode=ParseMode.HTML,
                                   text="<i>Benvenuto nel bot del ristorante Doc&Dubai</i>\n\nPuoi richiedere i menu "
                                        "dei due ristoranti usando rispettivamente /doc e /dubai\n\n"
                                        "Per iscriverti al menù giornaliero usa /start_doc o /start_dubai "
                                        ", riceverai il menù alle 11:30 ogni giorno\n\n"
                                        "/help per mostrare questo messaggio")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   parse_mode=ParseMode.HTML,
                                   text="<i>Benvenuto nel bot del ristorante Doc&Dubai</i>\n\nPuoi richiedere i menu "
                                        "dei due ristoranti usando rispettivamente /doc e /dubai\n\n"
                                        "Per iscriverti al menù giornaliero usa /start_doc o /start_dubai "
                                        ", riceverai il menù alle 11:30 ogni giorno\n\n"
                                        "/help per mostrare questo messaggio")


async def menu_command_callback(context: ContextTypes.DEFAULT_TYPE):
    print(f"job: {context.job.name}")
    job = context.job
    await context.bot.send_message(chat_id=job.chat_id,
                                   text=scraper.get_menu(f"{job.data}")["text"], parse_mode=ParseMode.HTML, disable_web_page_preview=True)


async def subscription_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_message.chat_id
    resturant = ""
    if update.message.text[0] == "/":
        resturant = update.message.text.split('_')[1]
    elif update.message.text.lower().split()[1] == "dubai" or update.message.text.lower().split()[1] == "doc":
        resturant = update.message.text.lower().split()[1]

    text = (f"Iscrizione effettuata, riceverai il menù del {resturant} ogni giorno alle 11:30\n"
            f"Per cancellare l'iscrizione scrivi /stop_{resturant}")
    add_user(chat_id)
    global engine
    with Session(engine) as session:
        user = session.query(BotUser).filter(BotUser.uid == chat_id).first()
        if resturant == "doc":
            if user.doc:
                text = f"Sei già iscritto al menù del doc, per cancellare l' iscrizione scrivi /stop_doc"
            user.doc = True
        elif resturant == "dubai":

            if user.dubai:
                text = f"Sei già iscritto al menù del dubai, per cancellare l' iscrizione scrivi /stop_dubai"
            user.dubai = True
        session.commit()

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=text)


async def unsubscription_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_message.chat_id
    resturant = ""

    if update.message.text[0] == "/":
        resturant = update.message.text.split('_')[1]
    elif update.message.text.lower().split()[1] == "dubai" or update.message.text.lower().split()[1] == "doc":
        resturant = update.message.text.lower().split()[1]

    text = f"Iscrizione cancellata, non riceverai più il menù del {resturant}\n"

    add_user(chat_id)
    global engine
    with Session(engine) as session:
        user = session.query(BotUser).filter(BotUser.uid == chat_id).first()
        if resturant == "doc":
            if not user.doc:
                text = f"Non sei iscritto al menù del doc"
            user.doc = False
        elif resturant == "dubai":
            if not user.dubai:
                text = f"Non sei iscritto al menù del dubai"
            user.dubai = False
        session.commit()
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=text)


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Questo comando non esiste. Usa la tastiera personalizzata per aiutarti!")

async def unknown_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if text == 'start dubai' or text == 'start doc':
        await subscription_command(update, context)
    elif text == 'stop dubai' or text == 'stop doc':
        await unsubscription_command(update, context)
    elif text == 'help':
        await help_command(update, context)
    #elif text == 'autori':
        #comando autori
    #elif text == 'stop':
        #comando stop
    #elif text == 'faq':
        #comando FAQ
    else:
        keyboard = grid()
        await context.bot.send_message(chat_id=update.effective_chat.id, reply_markup=keyboard, text="Questo comando non esiste. Usa la tastiera personalizzata per aiutarti!")

async def print_subscribers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != 532629429:
        return

    with Session(engine) as session:
        users = session.query(BotUser).all()
        doc = [user.uid for user in users if user.doc]
        dubai = [user.uid for user in users if user.dubai]

    message = (f"subscribers:\n\n"
               f"doc: {len(doc)}\n"
               f"dubai: {len(dubai)}\n"
               f"total: {len(users)}\n\n")

    for user in users:
        message += f"{user.uid}: {'Doc' if user.doc else ''} {'Dubai' if user.dubai else ''}\n"

    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text=message)


async def download_menus(context: ContextTypes.DEFAULT_TYPE):
    scraper.download_menu("doc")
    scraper.download_menu("dubai")


async def send_menus(context: ContextTypes.DEFAULT_TYPE):
    menu_doc = scraper.get_menu("doc")
    menu_dubai = scraper.get_menu("dubai")

    global engine
    retry = 0
    database_get_succeded = False
    while not database_get_succeded and retry < 3:
        try:
            with Session(engine) as session:
                users = session.query(BotUser).all()
                doc = [user.uid for user in users if user.doc]
                dubai = [user.uid for user in users if user.dubai]
                database_get_succeded = True
        except Exception as e:
            print(f"error while getting users: {e}")
            retry = retry + 1

    for uid in doc:
        await context.bot.send_message(chat_id=uid, text=menu_doc["text"], parse_mode=ParseMode.HTML)
    for uid in dubai:
        await context.bot.send_message(chat_id=uid, text=menu_dubai["text"], parse_mode=ParseMode.HTML)



def init_db():
    global engine
    if not inspect(engine).has_table("subscriptions"):  # If table don't exist, Create.
        metadata = MetaData()
        # Create a table with the appropriate Columns
        Table("subscriptions", metadata,
              Column("uid", sqlalchemy.Integer, primary_key=True),
              Column("dubai", sqlalchemy.Boolean, default=False),
              Column("doc", sqlalchemy.Boolean, default=False))
        # Implement the creation
        metadata.create_all(engine)


async def load_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.set_my_commands([
        BotCommand("doc", "Stampa menù del giorno del doc"),
        BotCommand("dubai", "Stampa menù del giorno del dubai"),
        BotCommand("start_doc", "ricevi il menù del doc ogni giorno"),
        BotCommand("start_dubai", "ricevi il menù del dubai ogni giorno"),
        BotCommand("stop_doc", "non ricevere il menù del doc ogni giorno"),
        BotCommand("stop_dubai", "non ricevere il menù del dubai ogni giorno"),
        BotCommand("help", "mostra messaggio di aiuto")
    ])
    await context.bot.send_message(chat_id=update.effective_chat.id, text="comandi aggiornati")

async def send_menus_wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == 532629429:
        await send_menus(context)

async def announce(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user.id == 532629429:
        return

    global engine
    retry = 0
    database_get_succeded = False
    while not database_get_succeded and retry < 3:
        try:
            with Session(engine) as session:
                users = session.query(BotUser).all()
                database_get_succeded = True
        except Exception as e:
            print(f"error while getting users: {e}")
            retry = retry + 1

    for user in users:
        await context.bot.send_message(chat_id=user.uid, text="ANNUNCIO: " + update.message.text[10:])

if __name__ == '__main__':
    if os.getenv("SECRETS") is None:
        os.environ["SECRETS"] = "secrets.json"

    with open(os.getenv("SECRETS"), "r") as file:
        config = json.load(file)

    if os.getenv("DOCKER") is None:
        config["db_host"]="localhost"

    application = ApplicationBuilder().token(config['token']).build()

    application.job_queue.run_daily(download_menus, days=(1, 2, 3, 4, 5),
                                    time=datetime.time(hour=10, minute=00, second=00,
                                                       tzinfo=pytz.timezone('Europe/Rome')))
    # Due to a bug Job_queue is skipping job if timezone is not provided for job.run_daily.

    application.job_queue.run_daily(send_menus, days=(1, 2, 3, 4, 5),
                                    time=datetime.time(hour=11, minute=30, second=00,
                                                       tzinfo=pytz.timezone('Europe/Rome')))

    # https://docs.sqlalchemy.org/en/20/core/engines.html#creating-urls-programmatically
    engine = create_engine(sqlalchemy.URL.create(
        "mysql+pymysql",
        username= config["db_username"],
        password= config["db_password"],
        host= config["db_host"],
        database= config["database"],
    ))

    Base.metadata.create_all(engine)

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('dubai', menu_command))
    application.add_handler(CommandHandler('doc', menu_command))
    application.add_handler(CommandHandler('send', send_menus_wrapper))
    application.add_handler(CommandHandler('announce', announce))
    application.add_handler(CommandHandler('start_doc', subscription_command))
    application.add_handler(CommandHandler('start_dubai', subscription_command))
    application.add_handler(CommandHandler('stop_doc', unsubscription_command))
    application.add_handler(CommandHandler('stop_dubai', unsubscription_command))
    application.add_handler(CommandHandler('subscribers', print_subscribers))
    application.add_handler(CommandHandler('set_commands', load_commands))
    application.add_handler(MessageHandler(filters.COMMAND, unknown_command))
    application.add_handler(MessageHandler(None, unknown_text))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

   