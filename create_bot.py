from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
import config

TOKEN = config.BotToken
dp = Dispatcher()
bot = Bot(TOKEN, parse_mode="HTML")
