#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# %%

# pip uninstall python-telegram-bot telegram
# pip install python-telegram-bot

import telegram

# 918743728
async def get_chat_id(bot):
  updates = await bot.getUpdates()
  chat_id = 918743728 if len(updates) == 0 else updates[-1].message.chat_id
  return chat_id

def send(bot, txt):
  bot.sendMessage(chat_id=918743728 , text=txt)

telegram_token = '5758487515:AAFfZ9fZsv7padX_6StJbn3T9zFOvW46jcc'
bot = telegram.Bot(token = telegram_token)
chat_id = get_chat_id(bot)

# %%
import os
import configparser
import errno

try:
    path = os.path.dirname(os.path.realpath(__file__))
    config = configparser.RawConfigParser()
    configFile = 'tcafe_config.ini'
    config.read(path+'/'+ configFile , encoding="utf-8")
    tcafe_host = config.get('CONFIG','HOST')
    tcafe_id = config.get('CONFIG','ID')
    tcafe_pw = config.get('CONFIG','PW')
    tcafe_key = config.get('CONFIG','KEY')
    telegram_token = config.get('CONFIG','TELEGRAM_TOKEN')
    telegram_chat_id = config.get('CONFIG','TELEGRAM_CHAT_ID')
except:
    raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), configFile)

# %%
telegram_chat_id

# %%

updates = bot.getUpdates()
chat_id = telegram_chat_id if len(updates) == 0 else updates[-1].message.chat_id
if len(chat_id) > 0 and chat_id != telegram_chat_id:
  config.add_section('CONFIG')
  config.set('CONFIG','HOST', tcafe_host)
  config.set('CONFIG', 'ID', tcafe_id)
  config.set('CONFIG', 'PW', tcafe_pw)
  config.set('CONFIG', 'KEY', tcafe_key)
  config.set('CONFIG', 'TELEGRAM_TOKEN', telegram_token)
  config.set('CONFIG', 'TELEGRAM_CHAT_ID', telegram_chat_id)
  with open(configFile,'w',encoding="utf-8") as f:
      config.write(f)


# %%
txt = '안녕하세요'
send(bot, txt)
