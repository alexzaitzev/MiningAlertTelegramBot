# -*- coding: utf-8 -*-

import commands
import config
import logging


@commands.bot.message_handler(content_types=["text"])
def message_handler(message):
    if message.from_user.username not in config.admin_usernames:
        commands.bot.send_message(message.chat.id, "You are not my master! \U0001F6AB")
        return

    if message.text == "/begin":
        commands.begin(message)
    elif message.text == "/end":
        commands.end(message)


if __name__ == '__main__':
    logging.basicConfig(filename='/tmp/bot.log',
                        level=logging.INFO,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    commands.bot.polling(none_stop=True)
