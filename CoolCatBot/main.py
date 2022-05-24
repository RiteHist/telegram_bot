import logging
from logging.handlers import RotatingFileHandler
import os
import time
from dotenv import load_dotenv
import requests
from telegram.ext import Updater, Filters, MessageHandler, CommandHandler
from telegram import InlineKeyboardButton, ReplyKeyboardMarkup

load_dotenv()
secret_token = os.getenv('TOKEN')
yan_token = os.getenv('YANTOKEN')
kots_url = 'https://api.thecatapi.com/v1/images/search'
yandex_homework_url = ('https://practicum.yandex.ru/api/'
                       'user_api/homework_statuses/')
google_url = 'https://www.google.com/'


def init_buttons():
    btn_newcat = InlineKeyboardButton('Give me a cool cat',
                                      callback_data='/newcat')
    btn_homework = InlineKeyboardButton('Check my homework',
                                        callback_data='/homework')
    buttons = ReplyKeyboardMarkup([[btn_newcat], [btn_homework]],
                                  resize_keyboard=True)
    return buttons


def init_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    handler = RotatingFileHandler('CoolCatBot/cat_log.log',
                                  maxBytes=5000000, backupCount=3)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def staying_alive():
    requests.get(google_url)


def get_new_kot():
    try:
        response = requests.get(kots_url)
    except Exception:
        logging.exception('Some shit happened trying to reach kots.')
        new_url = 'https://api.thedogapi.com/v1/images/search'
        response = requests.get(new_url)

    response = response.json()
    kato = response[0].get('url')
    return kato


def get_homework_status():
    headers = {'Authorization': f'OAuth {yan_token}'}
    from_date = int(time.time())
    payload = {'from_date': from_date}
    messages = []

    try:
        status = requests.get(yandex_homework_url,
                              headers=headers, params=payload)
    except Exception as e:
        raise requests.exceptions.ConnectionError() from e

    homeworks = status.json().get('homeworks')
    logging.info(f'answer from api is {str(homeworks)}')
    if homeworks:
        for work in homeworks:
            stat = work.get('status')
            comment = work.get('reviewer_comment')
            name = work.get('lesson_name')
            message = (f'Домашняя работа {name}:'
                       f'\nСтатус: {stat}'
                       f'\nКомментарий: {comment}'
                       )
            messages.append(message)

    return messages


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
    button = init_buttons()
    context.bot.send_message(chat_id=chat.id, text=msg, reply_markup=button)
    context.job.run_repeating(staying_alive, 600)


def on_homework(update, context):
    chat = update.effective_chat
    messages = get_homework_status()
    if messages:
        for msg in messages:
            context.bot.send_message(
                chat_id=chat.id, text=msg)
    else:
        empty = 'Нет обновлений по проектам'
        context.bot.send_message(chat_id=chat.id, text=empty)


def main():
    logger = init_logger()
    try:
        updater = Updater(token=secret_token)
        updater.dispatcher.add_handler(CommandHandler('homework', on_homework))
        updater.dispatcher.add_handler(CommandHandler('start', on_start))
        updater.dispatcher.add_handler(CommandHandler('newcat', on_new_cat))
        updater.dispatcher.add_handler(MessageHandler(Filters.text,
                                                      say_anything))
        updater.start_polling()
        updater.idle()
    except Exception as err:
        msg = f'Сбой. Ошибка: {err}'
        logger.error(msg)


if __name__ == '__main__':
    main()
