from sqlalchemy import Column, Integer, Text, Boolean, BigInteger, select, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from environs import Env
import asyncio, pytz, datetime
from collections import Counter

# env = Env()
# env.read_env(".env")
# user_db = env.str("DB_USER")
# passw = env.str("DB_PASSWORD")
# host = env.str("DB_HOST")
# name = env.str("DB_NAME")


# DATABASE_URL = "" f"postgresql+asyncpg:////{user_db}:{passw}{host}/{name}"
DATABASE_URL = "sqlite+aiosqlite:///./db.sqlite3"

# Создание объекта Engine
engine = create_async_engine(DATABASE_URL)

# Создание базового класса для моделей
Base = declarative_base()


class Users(Base):
    __tablename__ = "user"
    id = Column(Integer, autoincrement=True, primary_key=True)
    username = Column(Text, nullable=True)
    user_id = Column(BigInteger, nullable=True)
    nickname = Column(Text, nullable=True)
    city = Column(Text, nullable=True)
    adress = Column(Text, nullable=True)
    phone = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=True)
    is_subscriber = Column(Boolean, nullable=True)


class Services(Base):
    __tablename__ = "services"
    id = Column(Integer, autoincrement=True, primary_key=True)
    username = Column(Text, nullable=True)
    user_id = Column(BigInteger, nullable=True)
    name = Column(Text, nullable=True)
    city = Column(Text, nullable=True)
    adress = Column(Text, nullable=True)
    contacts = Column(Text, nullable=True)
    activity = Column(JSON, nullable=True)
    worktime = Column(Text, nullable=True)
    is_active = Column(Boolean, nullable=True)
    is_subscriber = Column(Boolean, nullable=True)
    link = Column(Text, nullable=True)


class Application_service(Base):
    __tablename__ = "appl_service"
    id = Column(Integer, autoincrement=True, primary_key=True)
    username = Column(Text, nullable=True)
    user_id = Column(BigInteger, nullable=True)
    name = Column(Text, nullable=True)
    city = Column(Text, nullable=True)
    adress = Column(Text, nullable=True)
    contacts = Column(Text, nullable=True)
    activity = Column(JSON, nullable=True)
    worktime = Column(Text, nullable=True)
    accepted = Column(Boolean, nullable=True)


class Variables(Base):
    __tablename__ = "variables"
    id = Column(Integer, autoincrement=True, primary_key=True)
    name = Column(Text, nullable=True)
    value = Column(JSON, nullable=True)


class Remont(Base):
    __tablename__ = "remont"
    id = Column(Integer, autoincrement = True, primary_key = True)
    user_id = Column(BigInteger, nullable=True)
    username = Column(Text, nullable=True)
    date_add = Column(DateTime, nullable=True)
    description = Column(Text, nullable=True)
    model = Column(Text, nullable=True)
    closed = Column(Boolean, nullable=True)
    closed_with_service = Column(Text, nullable=True)
    date_close = Column(Text, nullable=True)


class Sell(Base):
    __tablename__ = "sell"
    id = Column(Integer, autoincrement = True, primary_key = True)
    user_id = Column(BigInteger, nullable=True)
    username = Column(Text, nullable=True)
    date_add = Column(DateTime, nullable=True)
    model = Column(Text, nullable=True)
    equipment = Column(Text, nullable=True)
    condition = Column(Text, nullable=True)
    battery = Column(Text, nullable=True)
    price = Column(Text, nullable=True)
    memory = Column(Text, nullable=True)
    display_size = Column(Text, nullable=True)
    closed = Column(Boolean, nullable=True)
    closed_with_service = Column(Text, nullable=True)
    date_close = Column(Text, nullable=True)




#PART 1 - REGISTRATION
async def add_user(user, nickname, city):
    Session = async_sessionmaker()
    session = Session(bind = engine)
    new = Users(username = user.username, user_id = user.id, nickname = nickname, city = city, is_subscriber = False, is_active = True)
    session.add(new)
    await session.commit()
    await session.refresh(new)
    await session.close()


async def add_service_application(user, nickname, city, adress, contacts, activity, worktime):
    Session = async_sessionmaker()
    session = Session(bind = engine)
    new = Application_service(username = user.username, user_id = user.id, name = nickname, city = city, adress = adress, contacts = contacts, activity = activity, worktime = worktime)
    session.add(new)
    await session.commit()
    await session.refresh(new)
    return_id = new.id
    await session.close()
    return return_id


async def process_application(application_id, is_accept):
    Session = async_sessionmaker()
    session = Session(bind = engine)
    curr = await session.execute(select(Application_service).filter(Application_service.id == application_id))
    curr = curr.scalars().first()
    curr.accepted = is_accept
    return_id = curr.user_id
    await session.commit()
    await session.close()
    return return_id


async def add_service(appl_id, link):
    Session = async_sessionmaker()
    session = Session(bind = engine)
    curr = await session.execute(select(Application_service).filter(Application_service.id == appl_id))
    curr = curr.scalars().first()
    new = Services(username = curr.username, user_id =curr.user_id, name = curr.name, city = curr.city, adress = curr.adress, contacts = curr.contacts, activity = curr.activity, worktime = curr.worktime, is_subscriber = False, is_active = True, link = link)
    session.add(new)
    await session.commit()
    await session.refresh(new)
    await session.close()


async def all_applications_for_review():
    Session = async_sessionmaker()
    session = Session(bind = engine)
    all = await session.execute(select(Application_service))
    all = all.scalars().all()
    await session.close()
    return all


#PART 2 - menu
async def who_is_user(user_id):
    Session = async_sessionmaker()
    session = Session(bind = engine)
    
    curr_service = await session.execute(select(Services).filter(Services.user_id == user_id))
    curr_service = curr_service.scalars().first()
    is_service = curr_service is not None
    if is_service:
        is_sub_service = curr_service.is_subscriber
        is_active_service = curr_service.is_active
    else:
        is_sub_service, is_active_service = None, None
    
    curr_user = await session.execute(select(Users).filter(Users.user_id == user_id))
    curr_user = curr_user.scalars().first()
    is_user = curr_user is not None
    if is_user:
        is_active_user = curr_user.is_active
    else:
        is_active_user = None

    curr_appl = await session.execute(select(Application_service).filter(Application_service.user_id == user_id))
    is_appl = curr_appl.scalars().first() is not None
    
    await session.close()
    
    if is_user:
        return "user", None, is_active_user
    if is_service:
        return "service", is_sub_service, is_active_service
    if is_appl:
        return "application", None, None
    return None, None, None


async def user_info(user_id):
    Session = async_sessionmaker()
    session = Session(bind = engine)
    curr = await session.execute(select(Users).filter(Users.user_id == user_id))
    curr = curr.scalars().first()
    await session.close()
    return curr.nickname, curr.city, curr.is_subscriber, curr.phone, curr.adress


async def user_subscription(user_id, param):
    Session = async_sessionmaker()
    session = Session(bind = engine)
    curr = await session.execute(select(Users).filter(Users.user_id == user_id))
    curr = curr.scalars().first()
    curr.is_subscriber = param
    await session.commit()
    await session.close()


async def service_subscription(user_id, param):
    Session = async_sessionmaker()
    session = Session(bind = engine)
    curr = await session.execute(select(Services).filter(Services.user_id == user_id))
    curr = curr.scalars().first()
    curr.is_subscriber = param
    await session.commit()
    await session.close()

async def is_phone(user_id):
    Session = async_sessionmaker()
    session = Session(bind = engine)
    curr = await session.execute(select(Users).filter(Users.user_id == user_id))
    curr = curr.scalars().first()
    await session.close()
    return curr.phone

async def fetch(user_id, phone, adress):
    Session = async_sessionmaker()
    session = Session(bind = engine)
    curr = await session.execute(select(Users).filter(Users.user_id == user_id))
    curr = curr.scalars().first()
    curr.phone = phone
    curr.adress = adress
    await session.commit()
    await session.close()




async def change_city_request(user_id, new_city):
    Session = async_sessionmaker()
    session = Session(bind = engine)
    curr = await session.execute(select(Users).filter(Users.user_id == user_id))
    curr = curr.scalars().first()
    curr.city = new_city
    await session.commit()
    await session.close()

#PART 3 - admin

async def add_new_city(city):
    Session = async_sessionmaker()
    session = Session(bind = engine)
    curr = await session.execute(select(Variables).filter(Variables.name == "cities"))
    curr = curr.scalars().first()
    if curr is None:
        new = Variables(name = "cities", value = [city])
        session.add(new)
        await session.commit()
        await session.refresh(new)
        await session.close()
        return
    lis = curr.value
    lis.append(city)
    curr.value = lis
    await session.commit()
    await session.close()


async def change_sub_price(is_service, new_val):
    Session = async_sessionmaker()
    session = Session(bind = engine)
    if is_service:
        curr = await session.execute(select(Variables).filter(Variables.name == "service_sub"))
        curr = curr.scalars().first()
        new = Variables(name = "service_sub", value = new_val)
    else:
        curr = await session.execute(select(Variables).filter(Variables.name == "user_sub"))
        curr = curr.scalars().first()
        new = Variables(name = "user_sub", value = new_val)
    if not curr:
        session.add(new)
        await session.commit()
        await session.refresh(new)
    else:
        curr.value = new_val
        await session.commit()
    return await session.close()


async def get_sub_price():
    Session = async_sessionmaker()
    session = Session(bind = engine)
    curr = await session.execute(select(Variables).filter(Variables.name == "service_sub"))
    curr = curr.scalars().first()
    curr1 = await session.execute(select(Variables).filter(Variables.name == "user_sub"))
    curr1 = curr1.scalars().first()
    await session.close()
    return curr, curr1
    


async def all_cities():
    Session = async_sessionmaker()
    session = Session(bind = engine)
    curr = await session.execute(select(Variables).filter(Variables.name == "cities"))
    curr = curr.scalars().first()
    await session.close()
    return curr.value


async def all_user_for_rass():
    Session = async_sessionmaker()
    session = Session(bind = engine)
    all_user = await session.execute(select(Users))
    all_user = all_user.scalars().all()
    all_services = await session.execute(select(Services))
    all_services = all_services.scalars().all()
    return_list = [i.user_id for i in all_user]
    return_list.extend([i.user_id for i in all_services])
    await session.close()
    return return_list


async def namecheck(name, is_service):
    Session = async_sessionmaker()
    session = Session(bind = engine)
    if not is_service:
        curr = await session.execute(select(Users).filter(Users.username == name))
        curr = curr.scalars().first()
    else:
        curr = await session.execute(select(Services).filter(Services.username == name))
        curr = curr.scalars().first()
    await session.close()
    return curr is not None


async def block(name, is_service, is_block):
    Session = async_sessionmaker()
    session = Session(bind = engine)
    if not is_service:
        curr = await session.execute(select(Users).filter(Users.username == name))
        curr = curr.scalars().first()
    else:
        curr = await session.execute(select(Services).filter(Services.username == name))
        curr = curr.scalars().first()
    return_id = curr.user_id
    curr.is_active = not is_block
    await session.commit()
    await session.close()
    return return_id



#PART 4 - applications remont

async def add_application(user, desc, model):
    Session = async_sessionmaker()
    session = Session(bind = engine)
    now_date = datetime.datetime.now(pytz.timezone('Europe/Moscow'))
    new = Remont(user_id = user.id, username = user.username, description = desc, model=model, closed = False, date_add = now_date)
    session.add(new)
    await session.commit()
    await session.refresh(new)
    return_id = new.id
    await session.close()
    return return_id


async def get_services_list_for_remont(user_id):
    Session = async_sessionmaker()
    session = Session(bind = engine)
    curr = await session.execute(select(Users).filter(Users.user_id == user_id))
    curr = curr.scalars().first()
    city = curr.city
    all = await session.execute(select(Services).filter(Services.city == city, Services.is_subscriber, Services.is_active))
    all = all.scalars().all()
    await session.close()
    return [i.user_id for i in all if "ремонт" in i.activity]


async def remont_application_info(id):
    Session = async_sessionmaker()
    session = Session(bind = engine)
    curr = await session.execute(select(Remont).filter(Remont.id == id))
    curr = curr.scalars().first()
    await session.close()
    return curr.user_id, curr.description, curr.model


async def is_active_remont_appl(id):
    Session = async_sessionmaker()
    session = Session(bind = engine)
    curr = await session.execute(select(Remont).filter(Remont.id == id))
    curr = curr.scalars().first()
    await session.close()
    
    if curr is None:
        return False, "К сожалению, данное объявление снято с публикации ("
    
    if curr.closed:
        return False, "К сожалению, данное объявление завершено"
    
    return True, None


async def get_service_info(user_id):
    Session = async_sessionmaker()
    session = Session(bind = engine)
    curr = await session.execute(select(Services).filter(Services.user_id == user_id))
    curr = curr.scalars().first()
    await session.close()
    return curr.link, curr.name


async def close_appl_remont(appl_id, service_link):
    Session = async_sessionmaker()
    session = Session(bind = engine)
    curr = await session.execute(select(Remont).filter(Remont.id == appl_id))
    curr = curr.scalars().first()
    curr.closed = True
    curr.closed_with_service = service_link
    now_date = datetime.datetime.now(pytz.timezone('Europe/Moscow')).strftime('%d.%m.%Y %H:%M')
    curr.date_close = now_date
    await session.commit()
    await session.close()




async def decline_remont_application(appl_id):
    Session = async_sessionmaker()
    session = Session(bind = engine)
    curr = await session.execute(select(Remont).filter(Remont.id == appl_id))
    curr = curr.scalars().first()
    await session.delete(curr)
    await session.commit()
    await session.close()


# PART 5 - application sell

async def get_services_list_for_sell(user_id):
    Session = async_sessionmaker()
    session = Session(bind = engine)
    curr = await session.execute(select(Users).filter(Users.user_id == user_id))
    curr = curr.scalars().first()
    city = curr.city
    all = await session.execute(select(Services).filter(Services.city == city, Services.is_subscriber, Services.is_active))
    all = all.scalars().all()
    await session.close()
    return [i.user_id for i in all if "скупка" in i.activity]


async def add_application_sell(user, model, size, memory, equip, price, acum, sostoyanie):
    Session = async_sessionmaker()
    session = Session(bind = engine)
    now_date = datetime.datetime.now(pytz.timezone('Europe/Moscow'))
    new = Sell(username = user.username, user_id = user.id, display_size = size, model = model, date_add = now_date, closed = False, memory = memory, equipment = equip, price = price, condition = sostoyanie, battery = acum)
    session.add(new)
    await session.commit()
    await session.refresh(new)
    return_id = new.id
    await session.close()
    return return_id


async def is_active_sell_appl(id):
    Session = async_sessionmaker()
    session = Session(bind = engine)
    curr = await session.execute(select(Sell).filter(Sell.id == id))
    curr = curr.scalars().first()
    await session.close()
    
    if curr is None:
        return False, "К сожалению, данное объявление снято с публикации ("
    
    if curr.closed:
        return False, "К сожалению, данное объявление завершено"
    
    return True, None


async def sell_application_info(id):
    Session = async_sessionmaker()
    session = Session(bind = engine)
    curr = await session.execute(select(Sell).filter(Sell.id == id))
    curr = curr.scalars().first()
    await session.close()
    return curr.user_id, curr.model, curr.price


async def close_appl_sell(appl_id, service_link):
    Session = async_sessionmaker()
    session = Session(bind = engine)
    curr = await session.execute(select(Sell).filter(Sell.id == appl_id))
    curr = curr.scalars().first()
    curr.closed = True
    curr.closed_with_service = service_link
    now_date = datetime.datetime.now(pytz.timezone('Europe/Moscow')).strftime('%d.%m.%Y %H:%M')
    curr.date_close = now_date
    await session.commit()
    await session.close()



async def decline_sell_application(appl_id):
    Session = async_sessionmaker()
    session = Session(bind = engine)
    curr = await session.execute(select(Sell).filter(Sell.id == appl_id))
    curr = curr.scalars().first()
    await session.delete(curr)
    await session.commit()
    await session.close()


#PART 6 - statistics

async def remont_appl_info_for_stat(appl_id):
    Session = async_sessionmaker()
    session = Session(bind = engine)
    curr = await session.execute(select(Remont).filter(Remont.id == appl_id))
    curr = curr.scalars().first()
    await session.close()
    if curr is None:
        return None, None, None, None
    return curr.description, curr.model, curr.closed_with_service, curr.date_close


async def sell_appl_info_for_stat(appl_id):
    Session = async_sessionmaker()
    session = Session(bind = engine)
    curr = await session.execute(select(Sell).filter(Sell.id == appl_id))
    curr = curr.scalars().first()
    await session.close()
    if curr is None:
        return None, None, None, None, None, None, None, None
    return curr.model, curr.battery, curr.memory, curr.equipment, curr.condition, curr.display_size, curr.date_close, curr.closed_with_service


async def all_applications_for_review():
    Session = async_sessionmaker()
    session = Session(bind = engine)
    all = await session.execute(select(Application_service))
    all = all.scalars().all()
    await session.close()
    return all


async def adminpanel_stat(filter):
    now = datetime.datetime.now(pytz.timezone('Europe/Moscow'))
    start_of_day = datetime.datetime(now.year, now.month, now.day)
    start_of_week = start_of_day - datetime.timedelta(days=start_of_day.weekday())
    start_of_month = datetime.datetime(now.year, now.month, 1)
    Session = async_sessionmaker()
    session = Session(bind = engine)
    filtered_list = []
    all_rem = await session.execute(select(Remont))
    all_rem = all_rem.scalars().all()
    all_sell = await session.execute(select(Sell))
    all_sell = all_sell.scalars().all()
    start_list = all_rem + all_sell
    for i in start_list:
        if filter == "all":
            filtered_list.append(i)
        elif filter == "day":
            if start_of_day <= i.date_add < start_of_day + datetime.timedelta(days=1):
                filtered_list.append(i)
        elif filter == "week":
            if start_of_week <= i.date_add < start_of_week + datetime.timedelta(weeks=1):
                filtered_list.append(i)
        elif filter == "month":
            if start_of_month <= i.date_add < start_of_month.replace(month=start_of_month.month % 12 + 1):
                filtered_list.append(i)
    
    await session.close()
    
    models_list = [i.model for i in filtered_list]
    if not models_list:
        most_common = "-"
    else:
        model_counts = Counter(models_list)
        max_count = max(model_counts.values())
        most_common = [model for model, count in model_counts.items() if count == max_count]
        most_common = ", ".join(most_common)
    
    return {
        "count": len(filtered_list),
        "count_sell": len(filtered_list) - len([i for i in filtered_list if isinstance(i, Remont)]),
        "count_remont": len([i for i in filtered_list if isinstance(i, Remont)]),
        "closed_count": len([i for i in filtered_list if i.closed]),
        "most_common": most_common
    }


async def remont_stat():
    Session = async_sessionmaker()
    session = Session(bind=engine)
    all = await session.execute(select(Remont))
    all = all.scalars().all()
    await session.close()
    return all


async def sell_stat():
    Session = async_sessionmaker()
    session = Session(bind=engine)
    all = await session.execute(select(Sell))
    all = all.scalars().all()
    await session.close()
    return all


async def my_applications(user_id, is_closed):
    return_list = []
    Session = async_sessionmaker()
    session = Session(bind = engine)
    all = await session.execute(select(Remont).filter(Remont.user_id == user_id, Remont.closed == is_closed))
    all = all.scalars().all()
    await session.close()
    for i in all:
        return_list.append({"id": f"arem_{i.id}", "name": i.model + " ремонт"})
    all = await session.execute(select(Sell).filter(Sell.user_id == user_id, Sell.closed == is_closed))
    all = all.scalars().all()
    for i in all:
        return_list.append({"id": f"asell_{i.id}", "name": i.model + " продажа/обмен"})

    brand_count = {}
    result = []
    
    for item in return_list:
        if item['name'] not in brand_count:
            brand_count[item['name']] = 1
            result.append({"id": item['id'], "name": item['name']})
        else:
            brand_count[item['name']] += 1
            result.append({"id": item['id'], "name": f"{item['name']} ({brand_count[item['name']]})"})

    await session.close()
    return result


async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        

# asyncio.run(init_models())


