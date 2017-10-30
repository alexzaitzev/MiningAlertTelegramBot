# -*- coding: utf-8 -*-

import config
import json
import logging
import requests
import telebot
import threading

monitoring_enabled = False

bot = telebot.TeleBot(config.token)

cancelEvent = threading.Event()


def poll_server(stop_event):
    while not stop_event.wait(config.interval_polling):
        get_workers()
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
        t1 = threading.Thread(target=poll_server, args=(cancelEvent,))
        t1.start()
        t1.join()


def end(message):
    global monitoring_enabled

    if not monitoring_enabled:
        bot_answer = "Monitoring has already been stopped"
        bot.send_message(message.chat.id, bot_answer)
    else:
        cancelEvent.set()
        bot_answer = "Monitoring has been stopped"
        bot.send_message(message.chat.id, bot_answer)
        logging.info("%s by %s" % (bot_answer, message.chat.username))
        monitoring_enabled = False


def get_workers():
    prev_workers = set()
    response = requests.get(config.link)
    json_response = json.loads(response.text)
    workers_array = json_response['result']['workers']

    unique_workers = set()
    for worker in workers_array:
        unique_workers.add(worker[0])

    workers_off = config.all_workers.difference(unique_workers)
    if workers_off == set():
        prev_workers.clear()
    else:
        if prev_workers == set():
            prev_workers = prev_workers.union(workers_off)
            logging.warning("The following workers are absent: %s", ', '.join(prev_workers))
        else:
            workers_down = workers_off.intersection(prev_workers)
            if workers_down != set():
                bot.send_message(config.channel_id, "\U000026A0 Absent workers: \U000026A0 \n" + '\n'.join(workers_off))
