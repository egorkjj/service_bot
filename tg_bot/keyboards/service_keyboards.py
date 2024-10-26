from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def subscription_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text = "Активировать подписку ⭐", callback_data= "serivicesub"))
    return kb

def remont_appl_acception(appl_id):
    kb =  InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text = "Принять ✅", callback_data= f"sgl1_{appl_id}"))
    kb.add(InlineKeyboardButton(text = "Отклонить ❌", callback_data= f"sgl0_{appl_id}"))
    return kb

def sell_appl_acception(appl_id):
    kb = InlineKeyboardMarkup()
    kb.row(InlineKeyboardButton(text = "Принять ✅", callback_data= f"ssgl2_{appl_id}"), InlineKeyboardButton(text = "Отклонить ❌", callback_data= f"ssgl0_{appl_id}"))
    kb.add(InlineKeyboardButton(text = "Предложить свою стоимость 💵", callback_data= f"ssgl1_{appl_id}"))
    return kb

def decline_remont_kb():
    kb  =InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text = "Отменить ❌", callback_data= "declineremont"))
    return kb

def choice_comm_kb():
    kb = InlineKeyboardMarkup()
    kb.row(InlineKeyboardButton(text = "Да ✅", callback_data= "comm1"), InlineKeyboardButton(text = "Нет ❌", callback_data= "comm0"))
    kb.add(InlineKeyboardButton(text = "Отменить ❌", callback_data= "declineremont"))
    return kb


def touser_link_kb(url):
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text = "Связаться 💬", url= url))
    return  kb

def toskip():
    kb  =InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text = "Пропустить", callback_data= "skip"))
    return kb

def pay_kb():
    kb  =InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(text = "Оплатить подписку ⭐", pay=True))
    return kb
