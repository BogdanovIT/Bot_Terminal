from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, inline_keyboard_markup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData



main_kb = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Поиск по NS'), KeyboardButton(text='Поиск по ШК')],
    [KeyboardButton(text='Нет ШК на товаре'), KeyboardButton(text="Сделай штрих-код")],
    [KeyboardButton(text="Как это выглядит?"), KeyboardButton(text="Где моя половинка?")],
    [KeyboardButton(text='Одиночки'), KeyboardButton(text='Битые SSCC'), KeyboardButton(text="Есть идея!")],
    [KeyboardButton(text='Дефрагментация')],
    ], resize_keyboard=True, one_time_keyboard=True)
