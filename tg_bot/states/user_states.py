from aiogram.dispatcher.filters.state import State, StatesGroup

class registration(StatesGroup):
    name = State()
    city = State()
    adress = State()
    photo = State()
    contacts = State()
    chem = State()
    time = State()
    send = State()

class admin(StatesGroup):
    appl_reason = State()
    service_link = State()
    city = State()
    choice_city = State()
    rass_text = State()
    blok_choice = State()
    block_name = State()
    block_finish = State()
    block_reason = State()
    sub_price = State()
    

class user(StatesGroup):
    desc = State()
    photos = State()
    final = State()
    city_edit = State()
    phone = State()
    adress = State()
    adress_edit = State()
    phone_edit = State()


class service(StatesGroup):
    remont_price = State()
    remont_choice = State()
    remont_comm = State()
    price = State()
    comm = State()


class sell(StatesGroup):
    photos = State()
    sost = State()
    acum = State()
    size = State()
    equip  =State()
    sum = State()
    memory = State()
    final = State()


    

