import os
from dotenv import load_dotenv
from ..src.logic import clean_data, format_message, query_data
from telebot import TeleBot

load_dotenv()
BOT_TOKEN = os.getenv('TELEGRAM_TOKEN')
bot = TeleBot(BOT_TOKEN)

def lambda_handler(event, context):
    message = event['message']
    train_id = message['text']

    try:
        if len(train_id) != 4 or not train_id.isdigit():
            bot.send_message(message['chat']['id'], "That's not a valid train number...")
            return
    except Exception as e:
        bot.send_message(message['chat']['id'], "That's not a valid train number... %s" % e)
        return

    # querying data
    data = query_data(train_id)
    if "error" in data:
        bot.send_message(message['chat']['id'], "Requesto to Italo failed with error code %s..." % data["error"])
        return
    elif data["IsEmpty"] == True:
        bot.send_message(message['chat']['id'], "That train doesn't exist or it's already arrived to destination...")
        return
    data = clean_data(query_data(train_id))
    print(data)

    # query_data returns the integer
    # error code if the request failed
    if type(data) == int:
        bot.send_message(message['chat']['id'], "Requesto to Italo failed with error code %s..." % data)
        return
    
    bot.send_message(message['chat']['id'], format_message(data), parse_mode="HTML")
    return
