# -*- coding: utf-8 -*-

import config
import json
import logging
import requests
import telebot
import threading
import traceback

monitoring_enabled = False

bot = telebot.TeleBot(config.token)

cancelEvent = threading.Event()

last_stopped_workers = set()


def poll_server(stop_event):
    while not stop_event.wait(timeout=config.interval_polling):
        check_workers()
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


def check_workers():
    global last_stopped_workers

    try:
        active_workers = get_active_workers()
    except Exception:
        logging.error("Error occurred while getting workers: %s", traceback.format_exc())
        return None

    stopped_workers = config.all_workers.difference(active_workers)
    if stopped_workers == set():
        last_stopped_workers.clear()
    else:
        if last_stopped_workers == set():
            last_stopped_workers = last_stopped_workers.union(stopped_workers)
            logging.warning("The following workers possibly don't work: %s", ', '.join(last_stopped_workers))
        else:
            workers_down = stopped_workers.intersection(last_stopped_workers)
            if workers_down != set():
                logging.error("The following workers don't work: %s", ', '.join(workers_down))
                bot.send_message(config.channel_id, "\U000026A0 Absent workers: \U000026A0 \n" + '\n'.join(workers_down))


def get_active_workers():
    response = requests.get(config.link)
    json_response = json.loads(response.text)
    workers_array = json_response['result']['workers']

    unique_workers = set()
    for worker in workers_array:
        unique_workers.add(worker[0])

    return unique_workers
