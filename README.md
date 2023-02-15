# italogram
Tiny script which fetches data about running trains in Italo's train network

## Usage
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
