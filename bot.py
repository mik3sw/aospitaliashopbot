#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import time
from sympy import E

from telegram import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
    CallbackQueryHandler
)
import database as db

TOKEN = ""
MARKET = -1001804385883
ADMIN = [38201859, ]

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

GENDER, PHOTO, LOCATION, BIO = range(4)

POST, NAME, DESCRIPTION, PHOTO, PRICE, PAYMENTS, SHIPMENTS, CONTACTS = range(8) 
#telegram_id,type,name,description,price,payments,shipment,contacts

'''
def newpostold(update: Update, context: CallbackContext) -> int:
    """Starts the conversation."""
    reply_keyboard = [['#vendo', '#cerco']]
    try:
        db.add_post(update.message.from_user.id)
    except:
        pass

    update.message.reply_text(
        'Stai pubblicando un annuncio di vendita o cerchi qualcosa?',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='#vendo o #cerco?'
        ),
    )

    return POST
'''

def newpost(update: Update, context: CallbackContext) -> int:
    try: 
        # controllo se id è in blacklist
        db.get_id(update.message.from_user.id)
        update.message.reply_text("⚠️ Attenzione!\n\n Sembra che tu sia in una blacklist e non ti sarà permesso di postare annunci. Se pensi ci sia un errore contattare gli admin di @googlepixelit.", reply_markup=ReplyKeyboardRemove(), parse_mode='HTML')
        return ConversationHandler.END

    except:
        pass

    try:
        db.add_post(update.message.from_user.id)
    except:
        pass
    #res = update.message.text
    #db.add_post_partial(update.message.from_user.id, "type", update.message.text)
    update.message.reply_text("Benvenuto!\nCominciamo: dai un <b>titolo</b> al tuo annuncio 📦\n\n<i>Cerca di essere più esaustivo possibile, esempio: Google Pixel 6 nero tempesta 128GB</i>\n\n Puoi uscire dal processo in qualunque momento usando /cancel", reply_markup=ReplyKeyboardRemove(), parse_mode='HTML')
    return NAME

def name(update: Update, context: CallbackContext) -> int:
    db.add_post_partial(update.message.from_user.id, "name", update.message.text)
    update.message.reply_text("Perfetto! Ora aggiungi una <b>descrizione</b> 🗒\n(il più dettagliata possibile, in un unico messaggio)", reply_markup=ReplyKeyboardRemove(),parse_mode='HTML')
    return DESCRIPTION

def description(update: Update, context: CallbackContext) -> int:
    db.add_post_partial(update.message.from_user.id, "description", update.message.text)
    update.message.reply_text("Ora manda <b>una foto</b> del prodotto 📷\n\n<i>Per rendere l'annuncio più appetibile deve essere una foto vera non scaricata da internet e se possibile aggiungete anche un foglio di carta con scritto il vostro username telegram (se non lo avete impostatelo)</i>", reply_markup=ReplyKeyboardRemove(), parse_mode='HTML')
    return PHOTO


def photo(update: Update, context: CallbackContext) -> int:
    """Stores the photo and asks for a location."""
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('images/{}.jpg'.format(update.message.from_user.id))
    logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
    update.message.reply_text(
        'Quale prezzo proponi per questo prodotto? 💰 \n\n<i>Invia solo un numero (100, non 100€)</i>', parse_mode='HTML'
    )

    return PRICE

def price(update: Update, context: CallbackContext) -> int:
    db.add_post_partial(update.message.from_user.id, "price", update.message.text)
    update.message.reply_text("Che tipo di pagamenti accetti? 💳\n\n<i>Inserisci per esempio 'Bonifico', 'PayPal', ecc...</i>", reply_markup=ReplyKeyboardRemove(),parse_mode='HTML')
    return PAYMENTS

def payments(update: Update, context: CallbackContext) -> int:
    db.add_post_partial(update.message.from_user.id, "payments", update.message.text)
    update.message.reply_text("Spedizione? 🚚\nInserisci anche il luogo dal quale spedisci o dove vuoi far ritirare il prodotto\n\n<i>Si, No, a carico di chi?\nEs: Si, a carico dell'acquirente\nEs: No, ritiro a mano [LUOGO] </i>", reply_markup=ReplyKeyboardRemove(), parse_mode='HTML')
    return SHIPMENTS

def shipments(update: Update, context: CallbackContext) -> int:
    db.add_post_partial(update.message.from_user.id, "shipment", update.message.text)
    update.message.reply_text("Aggiungi un contatto 👤\n\n<i>Può essere il tuo username telegram o il tuo numero di telefono/mail ecc...\nÈ possibile inserire più contatti, ricorda di scriverli in un unico messaggio</i>", reply_markup=ReplyKeyboardRemove(), parse_mode='HTML')
    return CONTACTS


def contacts(update: Update, context: CallbackContext) -> int:
    db.add_post_partial(update.message.from_user.id, "contacts", update.message.text)
    #db.testout()
    info = db.getpost(update.message.from_user.id)
    #telegram_id,type,name,description,price,payments,shipment,contacts
    #{info['post']}
    text1 = f"""
<code>{info['tg_id']}</code>
#vendo
📦 <b>{info['name']}</b>

<i>{info['description']}</i>

💰 <b>Prezzo:</b> {info['price']}€
💳 <b>Pagamenti</b>: {info['payments']}
🚚 <b>Spedizione</b>: {info['shipment']}

👤 <b>Contatti</b>: {info['contacts']}"""

    update.message.reply_text(f"<b>Congratulazioni!</b> 🎉 \nIl tuo annuncio è stato postato correttamente nel canale @aospitaliashop.\n\nRicorda che una volta venduto l'articolo o se vuoi semplicemente cancellare o rifare l'annuncio è presente un bottone 'Elimina' che puoi usare solo tu.\nPer cercare i tuoi annunci all'interno del canale usa la funzione di ricerca di Telegram e inserisci come campo il tuo user_id: <code>{update.message.from_user.id}</code>\n\nGrazie.", reply_markup=ReplyKeyboardRemove(), parse_mode='HTML')

    keyboard = [[InlineKeyboardButton("Elimina", callback_data='delete')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_photo(MARKET, open(f"images/{update.message.from_user.id}.jpg", "rb"), caption=text1, reply_markup=reply_markup, parse_mode='HTML')
    #38201859
    return ConversationHandler.END

def delete(update,context):
    bot = context.bot
    query = update.callback_query
    caption = query.message.caption
    #print(caption)
    query.answer()
    if query.data == 'delete':
        target_id = int(caption.partition('\n')[0])
        print(target_id)
        if (target_id == query.from_user.id) or (query.from_user.id in ADMIN):
            message = "Articolo venduto"
            query = update.callback_query
            #print(query)
            #query.edit_message_caption(caption=message, parse_mode='HTML')
            #print(query.message.message_id)
            #time.sleep(2)
            #query.delete_message(MARKET, query.message.message_id)
            context.bot.delete_message(MARKET, query.message.message_id)


def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END

def blacklist(update, context):
    try:
        tg_id = context.args[0]
        db.add_blacklist(tg_id)
        update.message.reply_text(f"Utente {tg_id} inserito correttamente nella blacklist")
    except:
        update.message.reply_text("Errore, fornire un parametro valido.")


def whitelist(update, context):
    try:
        tg_id = context.args[0]
        db.delete_from_blacklist(tg_id)
        update.message.reply_text(f"Utente {tg_id} tolto correttamente dalla blacklist")
    except:
        update.message.reply_text("Errore, fornire un parametro valido.")

def start(update, context):
    update.message.reply_text(f"Benvenuto! Usa il comando /newpost per postare un nuovo annuncio.")


def main() -> None:
    """Run the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    # POST, NAME, DESCRIPTION, PHOTO, PRICE, PAYMENTS, SHIPMENTS, CONTACTS = range(8)
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('newpost', newpost)],
        states={
            #POST: [MessageHandler(Filters.regex('^(#vendo|#cerco)$'), post)],
            NAME: [MessageHandler(Filters.text & ~Filters.command, name)],
            DESCRIPTION: [MessageHandler(Filters.text & ~Filters.command, description)],
            PHOTO: [MessageHandler(Filters.photo, photo)], #CommandHandler('skip', skip_photo)],
            PRICE: [MessageHandler(Filters.text & ~Filters.command, price)],
            PAYMENTS: [MessageHandler(Filters.text & ~Filters.command, payments)],
            SHIPMENTS: [MessageHandler(Filters.text & ~Filters.command, shipments)],
            CONTACTS: [MessageHandler(Filters.text & ~Filters.command, contacts)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    dispatcher.add_handler(CallbackQueryHandler(delete, pattern='delete'))

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('blacklist', blacklist ,pass_args=True))
    dispatcher.add_handler(CommandHandler('whitelist', whitelist ,pass_args=True))

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()

