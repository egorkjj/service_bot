from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from tg_bot.DBSM import my_applications, all_cities

import json

def user_menu():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text = "Профиль 👤", callback_data= "usermenu_profile"))
    kb.add(InlineKeyboardButton(text = "Создать объявление ➕", callback_data= "usermenu_new"))
    kb.add(InlineKeyboardButton(text = "Мои объявления 📋", callback_data= "usermenu_my"))
    return kb

def after_registration_user():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text = "Главное меню 🏠", callback_data= "callmenu_user"))
    return kb

def choice_new_kb():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text = "Продажа/обмен", callback_data= "newtype_1"))
    kb.add(InlineKeyboardButton(text = "Ремонт", callback_data= "newtype_2"))
    kb.add(InlineKeyboardButton(text = "Главное меню 🔙", callback_data= "newtype_0"))
    return kb

def models_kb():
    kb = InlineKeyboardMarkup()
    lis = ["iPhone", "AirPods", "Apple Watch", "MacBook", "iPad"]
    for i in range(0, len(lis), 2):
        if i == 4:
            kb.add(InlineKeyboardButton(text = lis[i], callback_data= "mdl_" + lis[i]))
        else:
            kb.row(InlineKeyboardButton(text = lis[i], callback_data= "mdl_" + lis[i]), InlineKeyboardButton(text = lis[i+1], callback_data= "mdl_" + lis[i+1]))
    kb.add(InlineKeyboardButton(text = "Назад 🔙", callback_data= "mdl_back"))
    return kb

def types_kb(gadget):
    kb = InlineKeyboardMarkup()
    with open("tg_bot/models.json", 'r') as file:
        data = json.load(file)
    
    if gadget == "iPhone":
        keys_list = [i for i in data['iPhone']]
    if gadget != "iPhone":
        for i in range(len(data[gadget])): 
            kb.add(InlineKeyboardButton(callback_data= "ф_" + gadget + "_" + str(i), text = data[gadget][i]))
    else:
        for key in data[gadget]:
            kb.add(InlineKeyboardButton(callback_data= "ф_" + gadget + "_" + str(keys_list.index(key)), text = key))
    kb.add(InlineKeyboardButton(callback_data = "backfrommodels", text = "Назад 🔙"))
    return kb

def create_iphones_kb(idx):
    kb = InlineKeyboardMarkup()
    with open("tg_bot/models.json", 'r') as file:
        data = json.load(file)
    
    keys_list = [i for i in data['iPhone']]
    curr_key = keys_list[idx]
    lis = data['iPhone'][curr_key]
    for i in range(len(lis)):
        kb.add(InlineKeyboardButton(callback_data= "г_" + curr_key + "_" + str(i), text = lis[i]))
    kb.add(InlineKeyboardButton(callback_data = "backfromiphones", text = "Назад 🔙"))
    return kb

def backtochoice_kb():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(callback_data = "backtchs", text = "Вернуться 🔙"))
    return kb


def photos_user_kb(): 
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text = "Пропустить", callback_data= "skip"))
    kb.add(InlineKeyboardButton(callback_data = "backtchs", text = "Вернуться 🔙"))
    return kb


def final_appl_kb():
    kb  =InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text = "Отправить ✅", callback_data= "fremont_1"))
    kb.add(InlineKeyboardButton(text = "Отменить ❌", callback_data= "fremont_0"))
    kb.add(InlineKeyboardButton(text = "Отредактировать ✏️", callback_data= "fremont_redakt"))
    return kb


def remont_decision(service_id):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text = "Согласиться ✅", callback_data= f"racc_{service_id}"))
    kb.add(InlineKeyboardButton(text = "Отказаться ❌", callback_data= "racc_decl"))
    return kb

def sell_decision(service_id):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text = "Согласиться ✅", callback_data= f"rsell_{service_id}"))
    kb.add(InlineKeyboardButton(text = "Отказаться ❌", callback_data= "rsell_decl"))
    return kb

def toredakt_user_kb():
    kb  =InlineKeyboardMarkup()
    kb.row(InlineKeyboardButton(text = "Модель", callback_data="backtchs"), InlineKeyboardButton(text = "Описание и фото", callback_data= "tochange_desc"))
    kb.add(InlineKeyboardButton(text = "Отменить заявку ❌", callback_data="fremont_0"))
    kb.add(InlineKeyboardButton(text = "Назад 🔙", callback_data= "tochange_back"))
    return kb


def categories_appl_kb():
    kb  =InlineKeyboardMarkup()
    kb.row(InlineKeyboardButton(text = "Завершенные", callback_data= "my_1"), InlineKeyboardButton(text = "Активные", callback_data= "my_0"))
    kb.add(InlineKeyboardButton(text = "Главное меню 🔙", callback_data= "newtype_0"))
    return kb


async def all_applications(user_id, is_closed):
    kb = InlineKeyboardMarkup()
    res = await my_applications(user_id, is_closed)
    for i in res:
        kb.add(InlineKeyboardButton(text = i['name'], callback_data= i['id']))
    kb.add(InlineKeyboardButton(text = "Назад 🔙", callback_data= "arem_back"))
    return kb
 

def back_from_appl_info_kb(is_closed, appl_id):
    kb = InlineKeyboardMarkup()
    if not is_closed:
        kb.add(InlineKeyboardButton(text = "Снять с публикации ❌", callback_data= f"сн_{appl_id}"))
    kb.add(InlineKeyboardButton(text = "Назад 🔙", callback_data= f"my_{is_closed}"))
    return kb

def back_from_sell_info_kb(is_closed, appl_id):
    kb = InlineKeyboardMarkup()
    if not is_closed:
        kb.add(InlineKeyboardButton(text = "Снять с публикации ❌", callback_data= f"т_{appl_id}"))
    kb.add(InlineKeyboardButton(text = "Назад 🔙", callback_data= f"my_{is_closed}"))
    return kb

def fromprofile_kb(is_sub):
    kb  =InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text = "Отдредактировать ✏️", callback_data= "usermenu_redact"))
    if not is_sub:
        kb.add(InlineKeyboardButton(text = "Подписка ⭐", callback_data= "usermenu_sub"))
    kb.add(InlineKeyboardButton(text = "Главное меню 🔙", callback_data= "newtype_0"))
    return kb

def toredact_kb(is_sub):
    kb  =InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text = "Изменить город", callback_data= "toredakt_city"))
    if is_sub:
        kb.add(InlineKeyboardButton(text = "Изменить адрес", callback_data= "toredakt_adress"))
        kb.add(InlineKeyboardButton(text = "Изменить телефон", callback_data= "toredakt_phone"))
    kb.add(InlineKeyboardButton(text = "Назад 🔙", callback_data= "toredakt_back"))
    return kb


async def back_fromcity_redakt():
    kb  =InlineKeyboardMarkup()
    for i in await all_cities():
        kb.add(InlineKeyboardButton(text = i, callback_data= "er_" + i))
    kb.add(InlineKeyboardButton(text = "Назад 🔙", callback_data= "er_back"))
    return kb

def back_fromredakt_kb():
    kb  =InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text = "Назад 🔙", callback_data= "er_back"))
    return kb

def sub_kb():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text = "Активировать ⭐", callback_data= "usermenu_activate"))
    kb.add(InlineKeyboardButton(text = "Назад 🔙", callback_data= "usermenu_profile"))
    return kb


def sellmodels_kb():
    kb = InlineKeyboardMarkup()
    lis = ["iPhone", "AirPods", "Apple Watch", "MacBook", "iPad"]
    for i in range(0, len(lis), 2):
        if i == 4:
            kb.add(InlineKeyboardButton(text = lis[i], callback_data= "smdl_" + lis[i]))
        else:
            kb.row(InlineKeyboardButton(text = lis[i], callback_data= "smdl_" + lis[i]), InlineKeyboardButton(text = lis[i+1], callback_data= "smdl_" + lis[i+1]))
    kb.add(InlineKeyboardButton(text = "Назад 🔙", callback_data= "mdl_back"))
    return kb


def selltypes_kb(gadget):
    kb = InlineKeyboardMarkup()
    with open("tg_bot/models.json", 'r') as file:
        data = json.load(file)
    
    if gadget == "iPhone":
        keys_list = [i for i in data['iPhone']]
    if gadget != "iPhone":
        for i in range(len(data[gadget])): 
            kb.add(InlineKeyboardButton(callback_data= "и_" + gadget + "_" + str(i), text = data[gadget][i]))
    else:
        for key in data[gadget]:
            kb.add(InlineKeyboardButton(callback_data= "и_" + gadget + "_" + str(keys_list.index(key)), text = key))
    kb.add(InlineKeyboardButton(callback_data = "sellbackfrommodels", text = "Назад 🔙"))
    return kb

def sellcreate_iphones_kb(idx):
    kb = InlineKeyboardMarkup()
    with open("tg_bot/models.json", 'r') as file:
        data = json.load(file)
    
    keys_list = [i for i in data['iPhone']]
    curr_key = keys_list[idx]
    lis = data['iPhone'][curr_key]
    for i in range(len(lis)):
        kb.add(InlineKeyboardButton(callback_data= "м_" + curr_key + "_" + str(i), text = lis[i]))
    kb.add(InlineKeyboardButton(callback_data = "sellbackfromiphones", text = "Назад 🔙"))
    return kb


def sellbacktochoice_kb():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(callback_data = "sellbacktchs", text = "К моделям 🔙"))
    return kb


def memory_kb():
    kb  =InlineKeyboardMarkup()
    for i in ["32 Гб", "64 Гб", "128 Гб", "256 Гб", "512 Гб", "1 Тб"]:
        kb.add(InlineKeyboardButton(text = i, callback_data=  "m_" + i))
    kb.add(InlineKeyboardButton(callback_data = "sellbacktchs", text = "К моделям 🔙"))
    return kb

def sizes_kb():
    kb  = InlineKeyboardMarkup()
    for i in ["38 mm", "40mm", "41 mm", "42 mm", "44 mm", "45 mm", "49 mm"]:
        kb.add(InlineKeyboardButton(text = i, callback_data=  "s_" + i))
    kb.add(InlineKeyboardButton(callback_data = "sellbacktchs", text = "К моделям 🔙"))
    return kb

def finalsell_kb():
    kb  =InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text = "Отправить ✅", callback_data= "fsell_1"))
    kb.add(InlineKeyboardButton(text = "Отменить ❌", callback_data= "fsell_0"))
    kb.add(InlineKeyboardButton(callback_data = "sellbacktchs", text = "К моделям 🔙"))
    return kb
