# -*- coding: utf-8 -*-

import config
import json
import logging
import requests
import telebot
import time
import threading

monitoring_enabled = False

bot = telebot.TeleBot(config.token)


def task1():
    while monitoring_enabled:
        get_workers()
        time.sleep(config.interval_polling)
    pass


def begin(message):
    global monitoring_enabled

    if monitoring_enabled:
        bot_answer = "Monitoring has already been started"
        bot.send_message(message.chat.id, bot_answer)
    else:
        monitoring_enabled = True
        bot_answer = "Monitoring has been started"
        logging.info("%s by %s" % (bot_answer, message.chat.username))
        bot.send_message(message.chat.id, bot_answer)
        t1 = threading.Thread(target=task1)
        t1.start()
        t1.join()


def end(message):
    global monitoring_enabled

    if not monitoring_enabled:
        bot_answer = "Monitoring has already been stopped"
        bot.send_message(message.chat.id, bot_answer)
    else:
        bot_answer = "Monitoring has been stopped"
        bot.send_message(message.chat.id, bot_answer)
        logging.info("%s by %s" % (bot_answer, message.chat.username))
        monitoring_enabled = False


def get_workers():
    while monitoring_enabled:
        response = requests.get(config.link)
        json_response = json.loads(response.text)
        workers_array = json_response['result']['workers']

        unique_workers = set()
        for worker in workers_array:
            unique_workers.add(worker[0])

        print("запрос")
        xor = config.all_workers ^ unique_workers
        if xor != set():
            bot.send_message(config.channel_id, "\U000026A0 Есть неработающие воркеры \U000026A0 \n" + '\n'.join(xor))
