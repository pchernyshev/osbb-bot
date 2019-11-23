
import logging
import os

# pycharm is a pumpkin requirement is correct
# noinspection PyPackageRequirements
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler

from Authenticator import Authenticator
from config import config
from src.handler.example_handler import start, echo, unknown, got_contact, \
    test_gdrive, got_callback

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)


CONFIG_FILE = 'config/config.py'


if not os.path.exists(CONFIG_FILE):
    err = f"Please create {CONFIG_FILE} file with your telegram token"
    logging.error(err)
    raise FileNotFoundError(err)

token = config.BOT_TOKEN

# init
updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher

# handle
start_handler = CommandHandler('start', start)
requests_handler = CommandHandler('requests', test_gdrive)
echo_handler = MessageHandler(Filters.text, echo)
unknown_handler = MessageHandler(Filters.command, unknown)
contactHandler = MessageHandler(Filters.contact, got_contact)

main_menu_handler = CallbackQueryHandler(got_callback)

# attach
dispatcher.add_handler(start_handler)
dispatcher.add_handler(echo_handler)
dispatcher.add_handler(requests_handler)
dispatcher.add_handler(unknown_handler)
dispatcher.add_handler(contactHandler)
dispatcher.add_handler(main_menu_handler)

# go
updater.start_polling()
