#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# %%

# pip uninstall python-telegram-bot telegram
# pip install python-telegram-bot

import telegram

# 918743728
def get_chat_id(bot):
  updates = bot.getUpdates()
  chat_id = updates[-1].message.chat_id
  print(chat_id)
  return chat_id

def send(bot, txt):
  bot.sendMessage(chat_id=918743728 , text=txt)

telegram_token = '5758487515:AAFfZ9fZsv7padX_6StJbn3T9zFOvW46jcc'
bot = telegram.Bot(token = telegram_token)
chat_id = get_chat_id(bot)

txt = '안녕하세요'
send(bot, txt)