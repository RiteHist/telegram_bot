import os
from dotenv import load_dotenv
import requests
from telegram.ext import Updater, Filters, MessageHandler, CommandHandler
from telegram import ReplyKeyboardMarkup

load_dotenv()
secret_token = os.getenv('TOKEN')
kots_url = 'https://api.thecatapi.com/v1/images/search'


def get_new_kot():
    try:
        response = requests.get(kots_url)
    except Exception as err:
        print(err)
        new_url = 'https://api.thedogapi.com/v1/images/search'
        response = requests.get(new_url)

    response = response.json()
    kato = response[0].get('url')
    return kato


def on_new_cat(update, context):
    chat = update.effective_chat
    context.bot.send_photo(chat.id, get_new_kot())


def say_anything(update, context):
    chat = update.effective_chat
    context.bot.send_message(chat_id=chat.id, text='What is up, my dude')


def on_start(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    msg = f'I am now turned on... by you, {name} :^)'
    button = ReplyKeyboardMarkup([['/newcat',
                                   'Are you single?'],
                                  ['How long will I live?',
                                   'Where are you now?']
                                  ], resize_keyboard=True)
    context.bot.send_message(chat_id=chat.id, text=msg, reply_markup=button)


def main():
    updater = Updater(token=secret_token)
    updater.dispatcher.add_handler(CommandHandler('start', on_start))
    updater.dispatcher.add_handler(CommandHandler('newcat', on_new_cat))
    updater.dispatcher.add_handler(MessageHandler(Filters.text, say_anything))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
