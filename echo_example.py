import json
import logging
import os
import sys
from threading import Thread
from time import sleep

from telegram.ext import Updater, ConversationHandler, PicklePersistence, \
    CommandHandler, Filters

from config import config
from src import REGISTERED_BRIDGES
from src.handler import auth_conversation, new_ticket_conversation, \
    main_loop_conversation
from src.handler.auth_conversation import AUTH_CONVERSATION_HANDLER
from src.handler.const import *
from src.handler.main_loop_conversation import MAIN_MENU_HANDLER
from src.handler.new_ticket_conversation import NEW_TICKET_CONVERSATION
# pycharm is a pumpkin requirement is correct
# noinspection PyPackageRequirements
from tg_utils import ticket_link

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

persistence_obj = PicklePersistence(filename='tg_bot_persistence')

main_conversation = ConversationHandler(
    entry_points=[AUTH_CONVERSATION_HANDLER],
    states={
        Flows.AUTHORIZATION: [AUTH_CONVERSATION_HANDLER],
        Flows.MAIN_LOOP: [MAIN_MENU_HANDLER],
        Flows.NEW_TICKET: [NEW_TICKET_CONVERSATION]
        # Flows.UPDATE_TICKETS: []
    },  # TODO: fix fallbacks
    fallbacks=[MAIN_MENU_HANDLER, AUTH_CONVERSATION_HANDLER]
)


def main():
    updater = Updater(token=token,
                      persistence=persistence_obj,
                      use_context=True)
    dispatcher = updater.dispatcher

    auth_conversation.db = db
    new_ticket_conversation.db = db
    main_loop_conversation.db = db
    auth_conversation.dispatcher = dispatcher
    main_loop_conversation.dispatcher = dispatcher

    def stop_and_restart():
        """Gracefully stop the Updater and replace the current process with a new one"""
        updater.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def report_progress(ticket_id, chat_id):
        updater.bot.send_message(
            chat_id=chat_id,
            text=f'{STARTED_PROGRESS}: {ticket_link(ticket_id)}')

    def report_done(ticket_id, chat_id):
        updater.bot.send_message(
            chat_id=chat_id,
            text=f'{TICKET_DONE}: {ticket_link(ticket_id)}')

    def report_lost(ticket_id, chat_id):
        updater.bot.send_message(
            chat_id=chat_id,
            text = f'{TICKET_LOST}: {ticket_link(ticket_id)}')

    def poll_db_for_changes():
        report_funcs = {
            #TicketStatesStr.OPENED.value: None  ## ignore
            TicketStatesStr.IN_PROGRESS.value: report_progress,
            TicketStatesStr.DONE.value: report_done,
            #TicketStatesStr.NEED_CLARIFICATION.value: None,
        }
        old_statuses = db.snapshot_ticket_statuses()
        while True:
            sleep(DB_POLLING_INTERVAL)
            new_statuses = db.snapshot_ticket_statuses()
            for _id in set(old_statuses.keys()) | set(new_statuses.keys()):
                report_func = None
                address = None

                if _id in old_statuses.keys()\
                        and _id not in new_statuses.keys():
                    if REPORT_LOST_TICKETS:
                        report_func = report_lost
                        address = old_statuses[_id][0]
                elif old_statuses.get(_id) != new_statuses.get(_id):
                    status = new_statuses[_id][1]
                    report_func = report_funcs.get(status)
                    address = new_statuses[_id][0]

                if report_func:
                    for p in db.peers("", address):
                        report_func(_id, p)

            old_statuses = new_statuses

    def restart(update, context):
        update.message.reply_text('Bot is restarting...')
        Thread(target=stop_and_restart).start()

    dispatcher.add_handler(main_conversation)
    if config.LIST_OF_ADMINS:
        dispatcher.add_handler(
            CommandHandler(
                'r',
                restart,
                filters=Filters.user(user_id=config.LIST_OF_ADMINS)))

    Thread(target=poll_db_for_changes).start()
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
