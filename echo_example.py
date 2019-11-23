
import os
# pycharm is a pumpkin requirement is correct
# noinspection PyPackageRequirements
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

import logging

from src.handler.example_handler import start, echo, unknown

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)


TOKEN_FILE = 'config/api.token'


if not os.path.exists(TOKEN_FILE):
    raise FileNotFoundError(f"Please create {TOKEN_FILE} file "
                            f"with your telegram token")


with open(TOKEN_FILE) as f:
    token = f.read()


# init
updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher

# handle
start_handler = CommandHandler('start', start)
echo_handler = MessageHandler(Filters.text, echo)
unknown_handler = MessageHandler(Filters.command, unknown)

# attach
dispatcher.add_handler(start_handler)
dispatcher.add_handler(echo_handler)
dispatcher.add_handler(unknown_handler)

# go
updater.start_polling()
