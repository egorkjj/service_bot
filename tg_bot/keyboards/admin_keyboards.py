from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def accept_kb(appl_id):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text = "Принять ✅", callback_data= f"appl_1_{appl_id}"))
    kb.add(InlineKeyboardButton(text = "Отклонить ❌", callback_data= f"appl_0_{appl_id}"))
    return kb

def admin_menu():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text = "Статистика", callback_data="startadmin_stat"))
    kb.add(InlineKeyboardButton(text = "Заявки", callback_data="startadmin_appl"))
    kb.add(InlineKeyboardButton(text = "Рассылка", callback_data="startadmin_rass"))
    kb.add(InlineKeyboardButton(text = "Блокировка/разблокировка", callback_data="startadmin_blok"))
    kb.add(InlineKeyboardButton(text = "Добавление нового города", callback_data="startadmin_city"))
    kb.add(InlineKeyboardButton(text = "Управление ценой подписки", callback_data="startadmin_sub"))
    return kb

def admin_citychoice():
    kb = InlineKeyboardMarkup() 
    kb.add(InlineKeyboardButton(text= "Добавить ✅", callback_data= "cchoice_1"))
    kb.add(InlineKeyboardButton(text= "Отменить ❌", callback_data= "cchoice_0"))
    return kb

def tomenu_admin():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text = "В меню 🔙", callback_data="startadmin_tomenu"))
    return kb

def choice_blok_admin():
    kb = InlineKeyboardMarkup()
    kb.row(InlineKeyboardButton(text = "Сервис", callback_data= "block_1"), InlineKeyboardButton(text = "Пользователя", callback_data= "block_2"))
    kb.add(InlineKeyboardButton(text = "Назад 🔙", callback_data= "block_0"))
    return kb

def final_blok_admin():
    kb = InlineKeyboardMarkup()
    kb.row(InlineKeyboardButton(text = "Заблокировать", callback_data= "toblock_1"), InlineKeyboardButton(text = "Разблокировать", callback_data= "toblock_2"))
    kb.add(InlineKeyboardButton(text = "В меню 🔙", callback_data= "toblock_0"))
    return kb

def admin_excel_choice():
    kb  =InlineKeyboardMarkup()
    kb.row(InlineKeyboardButton(text = "Заявки на регистрацию", callback_data= "excel_0"), InlineKeyboardButton(text = "Заявки на публикацию", callback_data= "excel_1"))
    kb.add(InlineKeyboardButton(text = "В меню 🔙", callback_data="startadmin_tomenu"))
    return kb


def admin_stat_choice():
    kb  =InlineKeyboardMarkup()
    kb.row(InlineKeyboardButton(text = "За месяц", callback_data= "stat_month"), InlineKeyboardButton(text = "За неделю", callback_data= "stat_week"))
    kb.row(InlineKeyboardButton(text = "За день", callback_data= "stat_day"), InlineKeyboardButton(text = "За все время", callback_data= "stat_all"))
    kb.add(InlineKeyboardButton(text = "В меню 🔙", callback_data="startadmin_tomenu"))
    return kb

def backtostat():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text = "Назад 🔙", callback_data= "stat_back"))
    return kb

def adminsub_kb():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text = "Изменить цену для пользователей", callback_data= "startadmin_change0"))
    kb.add(InlineKeyboardButton(text = "Изменить цену для сервисов", callback_data= "startadmin_change1"))
    kb.add(InlineKeyboardButton(text = "В меню 🔙", callback_data="startadmin_tomenu"))
    return kb
