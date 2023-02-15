from dotenv import dotenv_values
from logic import clean_data, format_message, query_data
from logging import INFO, ERROR
from requests import get, post
from telebot import TeleBot
from time import sleep

BOT_TOKEN = dotenv_values(".env")['TELEGRAM_TOKEN']
bot = TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    print("New user: %s" % message.from_user.username)
    bot.reply_to(message, "Welcome to Italogram! Send a message with a train number to get some information about it.")


@bot.message_handler(func=lambda msg: True)
def get_train_status(message):

    train_id = message.text

    try:
        if len(train_id) != 4 or not train_id.isdigit():
            bot.send_message(message.chat.id, "That's not a valid train number...")
            return
    except Exception as e:
        bot.send_message(message.chat.id, "That's not a valid train number... %s" % e)
        return

    # querying data
    data = query_data(train_id)
    if "error" in data:
        bot.send_message(message.chat.id, "Requesto to Italo failed with error code %s..." % data["error"])
        return
    elif data["IsEmpty"] == True:
        bot.send_message(message.chat.id, "That train doesn't exist or it's already arrived to destination...")
        return
    data = clean_data(query_data(train_id))

    # query_data returns the integer
    # error code if the request failed
    if type(data) == int:
        bot.send_message(message.chat.id, "Requesto to Italo failed with error code %s..." % data)
        return
    
    bot.send_message(message.chat.id, format_message(data), parse_mode = "HTML")
    return

bot.infinity_polling(
    logger_level=INFO
)
