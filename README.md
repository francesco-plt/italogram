# italogram
Tiny script which fetches data about running trains in Italo's train network

<img src="https://user-images.githubusercontent.com/26849744/219042887-08b7c8d2-bc9b-4ef0-a087-21368b657663.png" alt="" width="50%" height="50%">



## Disclaimer
This bot uses unofficial APIs to fetch data. The information provided by this bot may not be accurate, complete, or up-to-date. The use of unofficial APIs may violate the terms of service of the services that this bot relies on, and therefore, the creators of this bot cannot guarantee the stability or reliability of the service. The creators of this bot do not assume any responsibility for the accuracy or reliability of the information provided, and the user of this bot assumes all risks associated with using the information provided. By using this bot, you acknowledge and agree to these terms and conditions.

## Installation
First of all, create a Telegram bot with [Bot Father](https://telegram.me/BotFather). Then write the token in the `.env` file:
```
TELEGRAM_TOKEN = <YOUR_TOKEN>
```
Then you need to initialize the webhook by pasting the following url in the address bar of your browser:
```
https://api.telegram.org/bot<YOUR_TOKEN>/setWebhook?url=
```
The bot can be deployed with either [AWS Lambda](https://aws.amazon.com/it/lambda/) using the source in the `lambda` folder, or with docker.

### Deploying with container
Now you can run the following commands to get it up and running:
``` shell
$ docker-compose build && docker-compose up -d
```

### Running locally
You can run the bot locally by executing:
``` shell
$ python3 -m venv .venv
$ source .venv/bin/activate
$ python3 -m pip install -r requirements.txt
$ python3 src/app.py
```

## Usage
Just open the chat with it and send a message containing the number of the train you want to check.
