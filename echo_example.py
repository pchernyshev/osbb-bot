import json
import logging
import os

# pycharm is a pumpkin requirement is correct
# noinspection PyPackageRequirements
from telegram.ext import Updater, ConversationHandler

from config import config
from src import REGISTERED_BRIDGES
from src.handler.auth_conversation import AUTH_CONVERSATION_HANDLER
from src.handler.const import Flows
from src.handler.main_loop_conversation import MAIN_MENU_HANDLER
from src.handler.new_ticket_conversation import NEW_TICKET_CONVERSATION

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)


CONFIG_FILE = 'config/config.py'


if not os.path.exists(CONFIG_FILE):
    err = f"Please create {CONFIG_FILE} file with your telegram token"
    logging.error(err)
    raise FileNotFoundError(err)

token = config.BOT_TOKEN


db = None
dbconfig = json.loads(open('config/db.json').read())
bridge_type = dbconfig.pop('type')
for bridge in REGISTERED_BRIDGES:
    if bridge.responds_to(bridge_type):
        db = bridge(dbconfig)
        break
else:
    raise LookupError(f"No bridge found for {bridge_type}")


# init
updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher

# handle

main_conversation = ConversationHandler(
    entry_points=[AUTH_CONVERSATION_HANDLER],
    states={
        Flows.AUTHORIZATION: [AUTH_CONVERSATION_HANDLER],
        Flows.MAIN_LOOP: [MAIN_MENU_HANDLER],
        Flows.NEW_TICKET: [NEW_TICKET_CONVERSATION],
       # Flows.LIST_TICKETS: [],
        #Flows.FAQ: [],
        #Flows.UPDATE_TICKETS: []
    },
    fallbacks=[MAIN_MENU_HANDLER]
)

# attach
dispatcher.add_handler(main_conversation)

# go
updater.start_polling()
