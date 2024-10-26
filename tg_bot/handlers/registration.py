from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType, InputFile, InputMediaPhoto

from tg_bot.keyboards import startaregister_kb, cities_kb, chem_zanimaetsya_kb, final_kb, accept_kb, user_menu, after_registration_user, subscription_keyboard, decline_appl_kb, admin_menu, final_appl_kb, sellbacktochoice_kb
from tg_bot.DBSM import add_user, add_service_application, who_is_user
from tg_bot import generate_random_string
from tg_bot.states import registration, user, sell

import os
from typing import List


admin_ids = [1261888898]


def register_registration_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands=["start"], state = [None, sell.size, sell.photos, sell.memory, user.desc])
    dp.register_callback_query_handler(decline, state = registration.all_states, text = "decline")
    dp.register_callback_query_handler(step1, text_startswith = "step1")
    dp.register_message_handler(name, state = registration.name)
    dp.register_callback_query_handler(city, state = registration.city, text_startswith = "city")
    dp.register_message_handler(adress, state = registration. adress)
    dp.register_message_handler(handle_albums, state = registration.photo, content_types= ContentType.ANY)
    dp.register_errors_handler(photo, exception= TypeError)
    dp.register_message_handler(contacts, state = registration.contacts)
    dp.register_callback_query_handler(chem, state = registration.chem, text_startswith = "chem")
    dp.register_message_handler(time, state = registration.time)
    dp.register_callback_query_handler(final, state = registration.send, text = "send")


async def cmd_start(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        if "photos_sell" in data:
            for path in data['photos_sell']:
                os.remove(path)

    await state.finish()
    if message.from_user.id in admin_ids: #если админ
        await message.answer("Здравствуйте! Выберите, что вы хотите сделать 👇", reply_markup= admin_menu())
        return
    
    user_data = await who_is_user(message.from_user.id)
    who = user_data[0]
    is_sub =  user_data[1]
    is_active = user_data[2]
    
    if not who: # если неизвестно
        await message.answer("Здравствуйте!\nКто вы? 👇", reply_markup= startaregister_kb())
        
    elif who == "user": # если юзер 
        if is_active:
            await message.answer("Здравствуйте! Выберите интересующий вас раздел 👇", reply_markup= user_menu())
        else:
            await message.answer("Извините, но вы были заблокированы нашими администраторами ❌")
    
    elif who == "service": #если сервис
        if is_active:
            if is_sub:
                await message.answer("Здравствуйте!\n\nВ данный момент подписка активна и вы можете получать заявки по продаже/обмену или ремонту техники от пользователей бота ✅")
            else:
                await message.answer("Здравствуйте!\n\nВ данный момент подписка неактивна, и вы не можете получать заявки по продаже/обмену или ремонту техники от пользователей бота ❌\n\nДля того, чтобы активировать подписку, нажмите на кнопку ниже 👇", reply_markup= subscription_keyboard())
        else:
            await message.answer("К сожалению, вы были заблокированы нашими администраторами ❌")
    
    
    else: #если подана заявка
        await message.answer("Ваша заявка в данный момент находится на рассмотрении у администраторов\n\nЯ оповещу вас сразу же, как только она будет рассмотрена 🔔")


async def step1(call: types.CallbackQuery, state: FSMContext):
    is_service = not bool(int(call.data.split("_")[1]))
    async with state.proxy() as data:
        data["is_service"] = is_service
    if is_service:
        await call.message.answer("Введите название вашего сервиса 👇", reply_markup= decline_appl_kb())
    else:
        await call.message.answer("Придумайте себе никнейм 👇", reply_markup= decline_appl_kb())
    await registration.name.set()


async def name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["name"] = message.text
    await message.answer("Выберите ваш город из списка 👇", reply_markup= await cities_kb())
    await registration.city.set()


async def city(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["city"] = call.data.split("_")[1]
        if not data["is_service"]:
            await add_user(call.from_user, data['name'], data['city'])
            await call.message.answer(f'Поздравляем, {data["name"]}! Вы прошли регистрацию.', reply_markup= after_registration_user())
            await state.finish()
            return
    await registration.adress.set()
    await call.message.answer("Отправьте точный адрес вашего сервиса 👇", reply_markup= decline_appl_kb())


async def adress(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['adress'] = message.text
    
    await registration.photo.set()
    await message.answer("Отправьте фотографии вашего сервиса 👇\n\n<i>*Здесь может быть ваш логотип, фотография с улицы или фотография помещения</i>", reply_markup= decline_appl_kb())


async def photo(update: types.Update, error: TypeError): 
    if str(error) == "handle_albums() missing 1 required positional argument: 'album'":
        dp = update.message.bot['dp']
        state = dp.current_state(chat=update.message.chat.id, user=update.message.from_user.id)
        current_state = await state.get_state()
        if current_state != registration.photo.state:
            return
        message = update.message
        photo = message.photo[-1]
        
        file_info = await message.bot.get_file(photo.file_id)
        file = await message.bot.download_file(file_info.file_path)

        file_path = "tg_bot/photos/" + generate_random_string(20) + ".jpg"
        with open(file_path, 'wb') as f:
            f.write(file.getvalue())

        async with state.proxy() as data:
            data['photos'] = [file_path]

        await message.answer("Отправьте контакты, по которым с вами можно связаться 👇\n\n<i>Необходимо указать телеграм-аккаунт вашего менеджера и номер телефона</i>", reply_markup= decline_appl_kb())
        await registration.contacts.set()


    elif str(error) == "handle_albums_remont() missing 1 required positional argument: 'album'":
        dp = update.message.bot['dp']
        state = dp.current_state(chat=update.message.chat.id, user=update.message.from_user.id)
        current_state = await state.get_state()
        if current_state != user.photos.state:
            return
        
        message = update.message
        photo = message.photo[-1]
        
        file_info = await message.bot.get_file(photo.file_id)
        file = await message.bot.download_file(file_info.file_path)

        file_path = "tg_bot/photos/" + generate_random_string(20) + ".jpg"
        with open(file_path, 'wb') as f:
            f.write(file.getvalue())

        async with state.proxy() as data:
            data['photos_remont'] = [file_path]

            await message.answer(f"Модель: <i>{data['selected_model']}</i>\nОписание проблемы: <i>{data['desc']}</i>", reply_markup= final_appl_kb())
            await user.final.set()

    elif str(error) == "handle_albums_sell() missing 1 required positional argument: 'album'":
        dp = update.message.bot['dp']
        state = dp.current_state(chat=update.message.chat.id, user=update.message.from_user.id)
        current_state = await state.get_state()
        if current_state != sell.photos.state:
            return
        
        message = update.message
        photo = message.photo[-1]
        
        file_info = await message.bot.get_file(photo.file_id)
        file = await message.bot.download_file(file_info.file_path)

        file_path = "tg_bot/photos/" + generate_random_string(20) + ".jpg"
        with open(file_path, 'wb') as f:
            f.write(file.getvalue())

        async with state.proxy() as data:
            data['photos_sell'] = [file_path]
            await message.answer(f"Опишите состояние <i>{data['gadget']}</i> 👇", reply_markup= sellbacktochoice_kb())
            await sell.sost.set()





async def handle_albums(message: types.Message, album: List[types.Message], state: FSMContext):
    media_list = []
    for obj in album:
        if obj.photo:
            file_id = obj.photo[-1].file_id
        else:
            file_id = obj[obj.content_type].file_id
        
        file_info = await message.bot.get_file(file_id)
        file = await message.bot.download_file(file_info.file_path)
        file_path = "tg_bot/photos/" + generate_random_string(20) + ".jpg"
        
        with open(file_path, 'wb') as f:
            f.write(file.getvalue())
        media_list.append(file_path)
        
        async with state.proxy() as data:
            data['photos'] = media_list
    
    await message.answer("Отправьте контакты, по которым с вами можно связаться 👇\n\n<i>Необходимо указать телеграм-аккаунт вашего менеджера и номер телефона</i>", reply_markup= decline_appl_kb())
    await registration.contacts.set()





async def contacts(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data["contacts"] = message.text
    await message.answer("Чем занимается ваш сервис?", reply_markup= chem_zanimaetsya_kb())
    await registration.chem.set()


async def chem(call: types.CallbackQuery, state: FSMContext):
    chem_list = call.data.split("_")[1].split(",")
    async with state.proxy() as data:
        for i in range(len(chem_list)):
            if not chem_list[i]:
                chem_list.pop(i)
        data['chem'] = chem_list
    await registration.time.set()
    await call.message.answer("Укажите часы работы 👇", reply_markup= decline_appl_kb())


async def time(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['time'] = message.text
        zanyatia = ", ".join(data['chem'])
        await message.answer(f"Ознакомьтесь с вашей заявкой:\n\n<b>Название сервиса</b>: <i>{data['name']}</i>\n<b>Город</b>: <i>{data['city']}</i>\n<b>Адрес</b>: <i>{data['adress']}</i>\n<b>Контактные данные</b>: <i>{data['contacts']}</i>\n<b>Чем занимается</b>: <i>{zanyatia}</i>\n<b>Часы работы</b>: <i>{message.text}</i>\n\nЕсли все верно, она будет <i>направлена на одобрение администрации</i>.", reply_markup= final_kb())
        await registration.send.set()

async def decline(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if "photos" in data:
            for path in data['photos']:
                os.remove(path)

    await state.finish()

    await call.message.answer("Регистрация отменена ❌\nЕсли захотите зарегистрироваться, введите <i>/start</i> 👇")


async def final(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer("Ваша заявка в процессе рассмотрения администратором.\n\nКак только администратор примет решение, вам придёт уведомление. 🔔\nОжидайте... ⏳")
    async with state.proxy() as data:
        application_id = await add_service_application(call.from_user, data['name'], data['city'], data['adress'], data['contacts'], data['chem'], data['time'])
        for i in admin_ids:
            if len(data['photos']) == 1:
                await call.message.bot.send_photo(chat_id= i, photo = InputFile(data['photos'][0]))
            else:
                await call.message.bot.send_media_group(chat_id=i, media = [InputMediaPhoto(InputFile(path)) for path in data['photos']])
            zanyatia = ", ".join(data['chem'])
            await call.message.bot.send_message(chat_id= i, text = f"Появилась новая заявка на регистрацию сервиса: <b>Название сервиса</b>: <i>{data['name']}</i>\n<b>Город</b>: <i>{data['city']}</i>\n<b>Адрес</b>: <i>{data['adress']}</i>\n<b>Контактные данные</b>: <i>{data['contacts']}</i>\n<b>Чем занимается</b>: <i>{zanyatia}</i>\n<b>Часы работы</b>: <i>{data['time']}</i>\n\nОтправил фотографии сервиса выше ☝️", reply_markup=accept_kb(application_id))
        for j in data['photos']:
            os.remove(j)
    await state.finish()


            


