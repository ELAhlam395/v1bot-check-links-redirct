import logging
import threading
import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Token for your bot
TOKEN = '6783916204:AAGrWsbz73SrQa0MWFIvk0BLTDmW6BI7Uqo'

# Create the Updater and pass it your bot's token
updater = Updater(token=TOKEN, use_context=True)

# Get the dispatcher to register handlers
dispatcher = updater.dispatcher

# Using a dictionary to store user positions
user_positions = {}

# Dictionary to store links for each user
user_links = {}

def validate_link(link, chat_id):
    try:
        response = requests.get(link)
        if response.status_code == 200:
            updater.bot.send_message(chat_id, f'The link is valid and works on the web: ' + link)
        else:
            updater.bot.send_message(chat_id, f'The link returned a {response.status_code} status code: ' + link)
    except Exception as e:
        updater.bot.send_message(chat_id, f'Error checking the link: {str(e)} ' + link)

def schedule_link_validation(link, chat_id):
    # Schedule the initial link validation after 2 minutes
    threading.Timer(120, validate_link, args=[link, chat_id]).start()
    
    # Schedule the next link validation every 2 minutes
    threading.Timer(1800, schedule_link_validation, args=[link, chat_id]).start() 

# Define a command handler. This one responds to the /start command
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hi , You can call Ahlam if you have any problems. :) ")

# Define an echo handler. This one echoes whatever message the user sends.
def echo(update, context):
    message_text = update.message.text
    chat_id = update.effective_chat.id

    # Check if the message is a link
    if 'https' in message_text or 'http' in message_text:
        user_links[chat_id] = message_text  # Store the link for the user
        # Remove the line below if you don't want to send the same link back to the user
        context.bot.send_message(chat_id, f'Thank you for sharing a link. We will validate it shortly.')
        # Schedule link validation
        schedule_link_validation(message_text, chat_id)
    else:
        context.bot.send_message(chat_id, f'You sent a non-link message: {message_text}')


# Define a command handler to clean all links
def clean_links(update, context):
    chat_id = update.effective_chat.id
    user_links.clear()
    context.bot.send_message(chat_id, 'All links cleared.')

# Register the handlers with the dispatcher
start_handler = CommandHandler('start', start)
echo_handler = MessageHandler(Filters.text & ~Filters.command, echo)
clean_links_handler = CommandHandler('clear', clean_links)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(echo_handler)
dispatcher.add_handler(clean_links_handler)

# Start the Bot
updater.start_polling()

# Run the bot until you send a signal to stop it
updater.idle()
