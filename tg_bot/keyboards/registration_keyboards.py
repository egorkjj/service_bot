from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from tg_bot.DBSM import all_cities

def startaregister_kb():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text = "Сервис", callback_data= "step1_0"))
    kb.add(InlineKeyboardButton(text = "Пользователь", callback_data= "step1_1"))
    return kb

async def cities_kb():
    kb = InlineKeyboardMarkup()
    for i in await all_cities():
        kb.add(InlineKeyboardButton(text = i, callback_data= "city_" + i))
    kb.add(InlineKeyboardButton(text = "Отменить ❌", callback_data= "decline"))
    return kb

def chem_zanimaetsya_kb():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text= "Скупка", callback_data="chem_скупка,"))
    kb.add(InlineKeyboardButton(text= "Ремонт", callback_data="chem_ремонт,"))
    kb.add(InlineKeyboardButton(text= "И то, и то", callback_data="chem_скупка,ремонт"))
    kb.add(InlineKeyboardButton(text = "Отменить ❌", callback_data= "decline"))
    return kb

def final_kb():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text = "Все верно. Отправить ✅", callback_data="send"))
    kb.add(InlineKeyboardButton(text = "Пройти регистрацию заново ❌", callback_data= "decline"))
    return kb

def decline_appl_kb():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text = "Отменить ❌", callback_data= "decline"))
    return kb

