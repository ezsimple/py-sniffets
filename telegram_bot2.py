#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=unused-argument, wrong-import-position
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

import telegram
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
log = logging.getLogger(__name__)

TOKEN = '5758487515:AAFfZ9fZsv7padX_6StJbn3T9zFOvW46jcc'
CHAT_ID = '918743728'

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TOKEN).build()

    # send message to bot
    # application.send_message(chat_id=CHAT_ID, text=r'안녕하십니까?')
    # AttributeError: 'Application' object has no attribute 'send_message'


async def send(msg='hello'):
  bot = telegram.Bot(token=TOKEN)

  # send message to bot
  return await bot.send_message(chat_id=CHAT_ID, text=msg)

import asyncio

async def main():
  await send()

if __name__ == "__main__":
  main()

