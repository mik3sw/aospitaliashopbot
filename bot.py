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
from rich.logging import RichHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ConversationHandler
from telegram.ext import CallbackContext, CallbackQueryHandler
from telegram.constants import ParseMode
import database as db
import os
import config

# Enable logging
FORMAT = "%(message)s"
logging.basicConfig(
    level=logging.INFO, format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

logger = logging.getLogger("rich")

# set variables for dict
NAME, DESCRIPTION, PHOTO, PRICE, PAYMENTS, SHIPMENTS = range(6)


async def newpost(update: Update, context: CallbackContext) -> int:
    try: 
        # controllo se id è in blacklist
        db.get_id(update.message.from_user.id)
        await update.message.reply_text("⚠️ Attenzione!\n\n"
                                        "Sembra che tu sia in una blacklist e non ti sarà permesso "
                                        "di postare annunci. "
                                        "Se pensi ci sia un errore contattare gli admin "
                                        "di @googlepixelit.", reply_markup=ReplyKeyboardRemove(),
                                        parse_mode=ParseMode.HTML)
        return ConversationHandler.END

    except:
        pass

    try:
        db.add_post(update.message.from_user.id)
    except:
        pass

    await update.message.reply_text("Benvenuto!\nCominciamo: dai un <b>titolo</b> al tuo annuncio 📦\n\n"
                                    "<i>Cerca di essere più esaustivo possibile, esempio: "
                                    "Google Pixel 6 nero tempesta 128GB</i>\n\n"
                                    "Puoi uscire dal processo in qualunque momento usando /cancel\n\n<b>"
                                    "⚠️ Attenzione!</b>\nDurante tutto il processo <b>NON fare copia e incolla</b> "
                                    "da altre fonti. "
                                    "La presenza di caratteri speciali (a volte invisibili) fa annullare il processo.",
                                    reply_markup=ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
    return NAME


async def name(update: Update, context: CallbackContext) -> int:
    db.add_post_partial(update.message.from_user.id, "name", update.message.text)
    await update.message.reply_text("Perfetto! "
                                    "Ora aggiungi una <b>descrizione</b> 🗒\n"
                                    "(il più dettagliata possibile, in un unico messaggio)",
                                    reply_markup=ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
    return DESCRIPTION


async def description(update: Update, context: CallbackContext) -> int:
    db.add_post_partial(update.message.from_user.id, "description", update.message.text)
    await update.message.reply_text("Ora manda <b>una foto</b> del prodotto 📷\n\n"
                                    "<i>Per rendere l'annuncio più appetibile deve essere una foto vera "
                                    "non scaricata da internet e se possibile aggiungete anche "
                                    "un foglio di carta con scritto il vostro "
                                    "username telegram (se non lo avete impostatelo)</i>",
                                    reply_markup=ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
    return PHOTO


async def photo(update: Update, context: CallbackContext) -> int:
    """Stores the photo and asks for a location."""
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    await photo_file.download_to_drive('images/{}.jpg'.format(update.message.from_user.id))
    logger.info("Photo of %s: %s", user.first_name, 'user_photo.jpg')
    await update.message.reply_text(
        'Quale prezzo proponi per questo prodotto? 💰 \n\n'
        '<i>Invia solo un numero (100, non 100€)</i>', parse_mode=ParseMode.HTML)

    return PRICE


async def price(update: Update, context: CallbackContext) -> int:
    db.add_post_partial(update.message.from_user.id, "price", update.message.text)
    await update.message.reply_text("Che tipo di pagamenti accetti? 💳\n\n"
                                    "<i>Inserisci per esempio 'Bonifico', 'PayPal', ecc...</i>",
                                    reply_markup=ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)
    return PAYMENTS


async def payments(update: Update, context: CallbackContext) -> int:
    db.add_post_partial(update.message.from_user.id, "payments", update.message.text)
    await update.message.reply_text("Spedizione? 🚚\n"
                                    "Inserisci anche il luogo dal quale spedisci o "
                                    "dove vuoi far ritirare il prodotto\n\n"
                                    "<i>Si, No, a carico di chi?\n"
                                    "Es: Si, a carico dell'acquirente\n"
                                    "Es: No, ritiro a mano [LUOGO] </i>", reply_markup=ReplyKeyboardRemove(),
                                    parse_mode=ParseMode.HTML)
    return SHIPMENTS


async def shipments(update: Update, context: CallbackContext) -> int:
    db.add_post_partial(update.message.from_user.id, "shipment", update.message.text)
    new = update.message.from_user
    try:
        if new.username is None:
            name = "<a href=\"tg://user?id={}\">{}</a>".format(new.id, new.first_name)
        else:
            name = "@"+new.username
    except:
        name = "[ERROR]"
    db.add_post_partial(update.message.from_user.id, "contacts", name)
    info = db.getpost(update.message.from_user.id)
    text1 = f"""
<code>{info['tg_id']}</code>
#vendo
📦 <b>{info['name']}</b>

<i>{info['description']}</i>

💰 <b>Prezzo:</b> {info['price']}€
💳 <b>Pagamenti</b>: {info['payments']}
🚚 <b>Spedizione</b>: {info['shipment']}

👤 <b>Contatti</b>: {info['contacts']}"""

    await update.message.reply_text(f"<b>Congratulazioni!</b> 🎉 \n"
                                    f"Il tuo annuncio è stato postato "
                                    f"correttamente nel topic 'Mercatino' del gruppo @googlepixelit.\n\n"
                                    f"Ricorda che una volta venduto l'articolo "
                                    f"o se vuoi semplicemente cancellare o rifare "
                                    f"l'annuncio è presente un bottone 'Elimina' "
                                    f"che puoi usare solo tu.\n"
                                    f"Per cercare i tuoi annunci all'interno del topic 'Mercatino' "
                                    f"usa la funzione di ricerca di Telegram e inserisci come campo "
                                    f"il tuo user_id: <code>{update.message.from_user.id}</code>\n\nGrazie.",
                                    reply_markup=ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)

    keyboard = [[InlineKeyboardButton("Elimina", callback_data='delete')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await context.bot.send_photo(config.MARKET, open(f"images/{update.message.from_user.id}.jpg", "rb"),
                                 caption=text1, reply_markup=reply_markup, parse_mode=ParseMode.HTML,
                                 message_thread_id=config.TOPIC)

    return ConversationHandler.END


async def delete(update,context):

    query = update.callback_query
    caption = query.message.caption
    await query.answer()

    if query.data == 'delete':
        target_id = int(caption.partition('\n')[0])
        print(target_id)
        if (target_id == query.from_user.id) or (query.from_user.id in config.ADMIN):

            query = update.callback_query
            await context.bot.delete_message(config.MARKET, query.message.message_id)


async def cancel(update: Update, context: CallbackContext) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text('Bye! I hope we can talk again some day.',
                                    reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


async def blacklist(update, context):
    try:
        tg_id = context.args[0]
        db.add_blacklist(tg_id)
        await update.message.reply_text(f"Utente {tg_id} inserito correttamente nella blacklist")
    except:
        await update.message.reply_text("Errore, fornire un parametro valido.")


async def whitelist(update, context):
    try:
        tg_id = context.args[0]
        db.delete_from_blacklist(tg_id)
        await update.message.reply_text(f"Utente {tg_id} tolto correttamente dalla blacklist")
    except:
        await update.message.reply_text("Errore, fornire un parametro valido.")


async def start(update, context):
    await update.message.reply_text(f"Benvenuto! Usa il comando /newpost per postare un nuovo annuncio.")


async def demo(update, context):
    if update.message.from_user.id in config.ADMIN:
        keyboard = [[InlineKeyboardButton("Posta un annuncio", url = 'https://t.me/aospitaliashopbot')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await context.bot.send_message(config.MARKET, f"Benvenuti nel topic mercatino! 📦\n\n"
                                               f"Per postare un annuncio usate il nuovo bot @aospitaliashopbot",
                                       reply_markup=reply_markup, message_thread_id=config.TOPIC)
    else:
        pass


async def clean(update, context):
    user_id = update.effective_user.id
    if user_id not in config.ADMIN:
        logger.warning("Unauthorized access denied for {}.".format(user_id))
        await context.bot.send_message(update.message.chat_id, f"Non sei autorizzato ed eseguire il comando")
    else:
        dir_name = "./images/"
        img_list = os.listdir(dir_name)

        cnt = 0
        for item in img_list:
            if item.endswith(".jpg"):
                os.remove(os.path.join(dir_name, item))
                cnt += 1

        await context.bot.send_message(update.message.chat_id, f"{cnt} immagini correttamente eliminate")



def main() -> None:
    # initialize bot
    application = ApplicationBuilder().token(config.TOKEN).build()

    # Add conversation handler with the states NAME, DESCRIPTION, PHOTO, PRICE, PAYMENTS, SHIPMENTS
    conv_handler = ConversationHandler(entry_points=[CommandHandler('newpost', newpost)],
                                       states={
                                           NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, name)],
                                           DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, description)],
                                           PHOTO: [MessageHandler(filters.PHOTO, photo)],
                                           PRICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, price)],
                                           PAYMENTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, payments)],
                                           SHIPMENTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, shipments)]},
                                       fallbacks=[CommandHandler('cancel', cancel)])

    application.add_handler(CallbackQueryHandler(delete, pattern='delete'))
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('demo', demo))
    application.add_handler(CommandHandler('blacklist', blacklist))
    application.add_handler(CommandHandler('whitelist', whitelist))
    application.add_handler(CommandHandler('clean', clean))

    application.add_handler(conv_handler)

    # start the BOT
    application.run_polling()


if __name__ == '__main__':
    main()

