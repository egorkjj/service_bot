from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import InputFile, InputMediaPhoto

from tg_bot.keyboards import user_menu, choice_new_kb, models_kb, types_kb, create_iphones_kb, backtochoice_kb, photos_user_kb, final_appl_kb, remont_appl_acception, after_registration_user, pay_kb
from tg_bot.keyboards import toredact_kb, toredakt_user_kb, categories_appl_kb, back_from_appl_info_kb, all_applications, fromprofile_kb,  touser_link_kb, back_fromcity_redakt, sub_kb, sellmodels_kb, back_from_sell_info_kb, back_fromredakt_kb
from tg_bot.DBSM import add_application, get_services_list_for_remont, remont_application_info, close_appl_remont, get_service_info, remont_appl_info_for_stat, decline_remont_application, user_info, change_city_request, sell_appl_info_for_stat, decline_sell_application, is_phone, get_sub_price
from tg_bot.DBSM import fetch, user_info, change_phone, change_adress
from tg_bot import generate_random_string
from tg_bot.states import user

import json, os
from typing import List

admin_ids = [1261888898, 1441962095]

def register_user_handlers(dp: Dispatcher):
    dp.register_message_handler(proc_info_sub, state = [user.phone, user.adress])
    dp.register_callback_query_handler(showmenu, text = "callmenu_user")
    dp.register_callback_query_handler(process_my_appl, text_startswith = "my")
    dp.register_callback_query_handler(show_appl_remont, text_startswith = "arem_")
    dp.register_callback_query_handler(show_appl_sell, text_startswith = "asell_")
    dp.register_callback_query_handler(delapl_remont, text_startswith = "сн_")
    dp.register_callback_query_handler(delapl_sell, text_startswith = "т_")
    dp.register_callback_query_handler(process_menu, text_startswith = "usermenu")
    dp.register_callback_query_handler(process_edit, text_startswith = "toredakt")
    dp.register_message_handler(process_redakt, state = [user.phone_edit, user.adress_edit])
    dp.register_callback_query_handler(process_cityedit, text_startswith = "er_", state = [user.city_edit, user.phone_edit, user.adress_edit])
    dp.register_callback_query_handler(decision_remont, text_startswith = "racc")
    dp.register_callback_query_handler(process_new, text_startswith = "newtype")
    dp.register_callback_query_handler(process_models, text_startswith = "mdl")
    dp.register_callback_query_handler(backtomodels, text = "backfrommodels")
    dp.register_callback_query_handler(backtomodels, text = "backfromiphones")
    dp.register_callback_query_handler(procmodel, text_startswith ="ф_")
    dp.register_callback_query_handler(prociphone, text_startswith = "г_")
    dp.register_callback_query_handler(backtochoice, text = "backtchs", state = [user.desc, user.photos, user.final])
    dp.register_message_handler(procdesc, state = user.desc)
    dp.register_callback_query_handler(skip, text = "skip", state = user.photos)
    dp.register_message_handler(handle_albums_remont, state = user.photos, content_types= types.ContentType.ANY)
    dp.register_callback_query_handler(process_final, state = user.final, text_startswith = "fremont_")
    dp.register_callback_query_handler(redakt_desc, state = user.final, text_startswith = "tochange_")


async def showmenu(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("Здравствуйте!\n\nВыберите интересующий вас раздел в меню 👇", reply_markup= user_menu())


async def process_menu(call: types.CallbackQuery, state: FSMContext):
    action = call.data.split("_")[1]
    if action == "new":
        await call.message.edit_text("Что вас интересует?", reply_markup= choice_new_kb())
    
    elif action == "my":
        await call.message.edit_text("Выберите категорию 👇", reply_markup= categories_appl_kb())

    elif action == "profile":
        res = await user_info(call.from_user.id)
        sub = "неактивна ❌" if not res[2] else "активна ✅"
        await call.message.edit_text(f"<b>{res[0]}</b>\n\nГород: <i>{res[1]}</i>\nПодписка: {sub}", reply_markup= fromprofile_kb(res[4])) if not res[4] else await call.message.edit_text(f"<b>{res[0]}</b>\n\nГород: <i>{res[1]}</i>\nПодписка: {sub}\nАдрес: <i>{res[4]}</i>\nТелефон: <i>{res[3]}</i>", reply_markup= fromprofile_kb(res[2]))

    elif action == "redact":
        await call.message.edit_text("Что вы хотите изменить?", reply_markup= toredact_kb("Адрес:" in call.message.text))
    
    elif action == "sub":
        await call.message.edit_text('''Что даёт подписка?\n\n- Чехол на ваш iPhone раз в 2 месяца\n- 3 защитных стекла раз в месяц\n- Особое оформление объявлений''', reply_markup= sub_kb())

    elif action == "activate":
        if await is_phone(call.from_user.id):
            price = (await get_sub_price())[1].value
            if price != "-":
                await call.message.bot.send_invoice(chat_id= call.from_user.id, title= "Оплата подписки", description= "Оплатить подписку ✅", payload= "user", currency= "RUB", provider_token= "381764678:TEST:94152" , prices=[{"label": "Руб", "amount": int(price) * 100}], start_parameter= "test", reply_markup= pay_kb())
            else:
                await call.message.answer("Оплата подписки в данный момент невозможна")
        else:
            await user.phone.set()
            await call.message.answer("Введите модель своего телефона для оформления подписки")



async def proc_info_sub(message: types.Message, state: FSMContext):
    if await state.get_state() == user.phone.state:
        async with state.proxy() as data:
            data['phone'] = message.text
        await message.answer("Введите свой точный адрес 👇")
        await user.adress.set()
    else:
        async with state.proxy() as data:
            await fetch(message.from_user.id, data['phone'], message.text)
        price = (await get_sub_price())[1].value
        if price != "-":
            await message.bot.send_invoice(chat_id= message.from_user.id, title= "Оплата подписки", description= "Оплатить подписку ✅", payload= "user", currency= "RUB", provider_token= "381764678:TEST:94152" , prices=[{"label": "Руб", "amount": int(price) * 100}], start_parameter= "test", reply_markup= pay_kb())
        else:
            await message.answer("Оплата подписки в данный момент невозможна")
        await state.finish()


async def process_edit(call: types.CallbackQuery, state: FSMContext):
    action = call.data.split("_")[1]
    if action == "back":

        res = await user_info(call.from_user.id)
        sub = "неактивна ❌" if not res[2] else "активна ✅"
        await call.message.edit_text(f"<b>{res[0]}</b>\n\nГород: <i>{res[1]}</i>\nПодписка: {sub}", reply_markup= fromprofile_kb(res[4])) if not res[4] else await call.message.edit_text(f"<b>{res[0]}</b>\n\nГород: <i>{res[1]}</i>\nПодписка: {sub}\nАдрес: <i>{res[4]}</i>\nТелефон: <i>{res[3]}</i>", reply_markup= fromprofile_kb(res[2]))
        return
        
    if action == "city":
        await call.message.edit_text("Выберите город ниже 👇", reply_markup= await back_fromcity_redakt())
        await user.city_edit.set()
    
    elif action == "adress":
        await call.message.edit_text("Введите новый адрес ниже 👇", reply_markup= back_fromredakt_kb())
        await user.adress_edit.set()
    
    elif action == "phone":
        await call.message.edit_text("Введите новую модель телефона ниже 👇", reply_markup= back_fromredakt_kb())
        await user.phone_edit.set()



async def process_redakt(message: types.Message, state: FSMContext):
    if await state.get_state() == user.phone_edit.state:
        await change_phone(message.from_user.id, message.text)
        await message.answer(f"Модель телефона изменена на <i>{message.text}</i> ✅", reply_markup= after_registration_user())
    else:
        await change_adress(message.from_user.id, message.text)
        await message.answer(f"Адрес изменен на <i>{message.text}</i> ✅", reply_markup= after_registration_user())
    await state.finish()



async def process_cityedit(call: types.CallbackQuery, state: FSMContext):
    if call.data == "er_back":
        res = await user_info(call.from_user.id)
        await call.message.edit_text("Что вы хотите изменить?", reply_markup= toredact_kb(res[4]))
        await state.finish()
        return
    
    if await state.get_state() == user.city_edit.state:

        city = call.data.split("_")[1]
        await change_city_request(call.from_user.id, city)
        await state.finish()
        await call.message.answer(f"Город изменен на <i>{city}</i> ✅",  reply_markup= after_registration_user())
        await call.message.delete()



async def process_my_appl(call: types.CallbackQuery, state: FSMContext):
    is_closed = bool(int(call.data.split("_")[1]))
    keyboard = await all_applications(call.from_user.id, is_closed)
    text = ("Список завершенных объявлений 👇" if is_closed else "Список активных объявлений 👇") if len(keyboard['inline_keyboard']) != 1 else ("У вас нет завершенных объявлений ❌" if is_closed else "У вас нет активных объявлений ❌")
    await call.message.edit_text(text=text, reply_markup= keyboard)



async def show_appl_remont(call: types.CallbackQuery, state: FSMContext):
    if call.data == "arem_back":        
        await call.message.edit_text("Выберите категорию 👇", reply_markup= categories_appl_kb())
        return

    appl_id = int(call.data.split("_")[1])
    desc, model, service, date =  await remont_appl_info_for_stat(appl_id)
    if desc is None:
        await call.message.edit_text("Данное объявление было снять с публикации", reply_markup= back_from_appl_info_kb(1, None))
        return
    
    if service is not None:
        await call.message.edit_text(f"Объявление на ремонт <i>{model}</i>\nЗавершено - <i>{date}</i> ✅\n\nОписание проблемы - <i>{desc}</i>\n<i><a href = '{service}'>Выбранный сервис</a></i>", reply_markup= back_from_appl_info_kb(1, None))
    else:
        await call.message.edit_text(f"Объявление на ремонт <i>{model}</i>\nНе завершено ❌\n\nОписание проблемы - <i>{desc}</i>", reply_markup= back_from_appl_info_kb(0, appl_id))



async def show_appl_sell(call: types.CallbackQuery, state: FSMContext):
    if call.data == "asell_back":        
        await call.message.edit_text("Выберите категорию 👇", reply_markup= categories_appl_kb())
        return

    appl_id = int(call.data.split("_")[1])
    model, battery, memory, equipment, condition, display_size, date, service =  await sell_appl_info_for_stat(appl_id)
    if model is None:
        await call.message.edit_text("Данное объявление было снять с публикации", reply_markup= back_from_appl_info_kb(1, None))
        return
    
    if service is not None:
        if display_size == "-":
            await call.message.edit_text(f"Объявление на продажу/обмен <i>{model}</i>\nЗавершено - <i>{date}</i> ✅\n\nОбъем аккумулятора - <i>{battery}</i>\nПамять - <i>{memory}</i>\nКомплект - <i>{equipment}</i>\nСостояние - <i>{condition}</i>\n<i><a href = '{service}'>Выбранный сервис</a></i>", reply_markup= back_from_sell_info_kb(1, None))
        else:
            await call.message.edit_text(f"Объявление на продажу/обмен <i>{model}</i>\nЗавершено - <i>{date}</i> ✅\n\nРазмер экрана - <i>{display_size}</i>\nОбъем аккумулятора - <i>{battery}</i>\nПамять - <i>{memory}</i>\nКомплект - <i>{equipment}</i>\nСостояние - <i>{condition}</i>\n<i><a href = '{service}'>Выбранный сервис</a></i>", reply_markup= back_from_sell_info_kb(1, None))
    else:
        if display_size == "-":
            await call.message.edit_text(f"Объявление на продажу/обмен <i>{model}</i>\nНе завершено ❌\n\nОбъем аккумулятора - <i>{battery}</i>\nПамять - <i>{memory}</i>\nКомплект - <i>{equipment}</i>\nСостояние - <i>{condition}</i>", reply_markup= back_from_sell_info_kb(0, appl_id))
        else:
            await call.message.edit_text(f"Объявление на продажу/обмен <i>{model}</i>\nНе завершено ❌\n\nРазмер экрана - <i>{display_size}</i>\nОбъем аккумулятора - <i>{battery}</i>\nПамять - <i>{memory}</i>\nКомплект - <i>{equipment}</i>\nСостояние - <i>{condition}</i>", reply_markup= back_from_sell_info_kb(0, appl_id))
    


async def delapl_remont(call: types.CallbackQuery, state: FSMContext):
    appl_id = int(call.data.split("_")[1])
    await decline_remont_application(appl_id)
    await call.message.edit_text("Объявление на ремонт успешно снято с публикации ✅", reply_markup= back_from_appl_info_kb(1, None))


async def delapl_sell(call: types.CallbackQuery, state: FSMContext):
    appl_id = int(call.data.split("_")[1])
    await decline_sell_application(appl_id)
    await call.message.edit_text("Объявление на продажу/обмен успешно снято с публикации ✅", reply_markup= back_from_sell_info_kb(1, None))











async def process_new(call: types.CallbackQuery, state: FSMContext):
    action = int(call.data.split("_")[1])
    if not action:
        await call.message.edit_text("Здравствуйте!\n\nВыберите интересующий вас раздел в меню 👇", reply_markup= user_menu())
        await state.finish()
        return
    
    if action == 1: 
        await call.message.edit_text("Что бы вы хотели продать/обменять?", reply_markup= sellmodels_kb())

    elif action == 2:
        await call.message.edit_text("Что бы вы хотели отремонтировать?", reply_markup= models_kb())


async def process_models(call: types.CallbackQuery, state: FSMContext):
    mdl = call.data.split("_")[1]
    if mdl == "back":
        await call.message.edit_text("Что вас интересует?", reply_markup= choice_new_kb())
        return
    else:
        await call.message.edit_text("Выберите интересующую вас модель ниже 👇", reply_markup= types_kb(mdl))


async def backtomodels(call: types.CallbackQuery, state: FSMContext):
    if call.data == "backfrommodels":
        await call.message.edit_text("Что бы вы хотели отремонтировать?", reply_markup= models_kb())
    else:
        await call.message.edit_text("Выберите интересующую вас модель ниже 👇", reply_markup= types_kb("iPhone"))


async def procmodel(call: types.CallbackQuery, state: FSMContext):
    gadget = call.data.split("_")[1]
    mdl_id = int(call.data.split("_")[2])
    with open("tg_bot/models.json", 'r') as file:
        data_js = json.load(file)
    if "iPhone" not in gadget:
        async with state.proxy() as data:
            data['selected_model'] = data_js[gadget][mdl_id]
        await call.message.edit_text(f"Выбрана модель: <i>{data_js[gadget][mdl_id]}</i> ✅\nОпишите вашу поломку 👇", reply_markup= backtochoice_kb())
        await user.desc.set()
    else:
        await call.message.edit_text("Выберите интересующую вас модель ниже 👇", reply_markup= create_iphones_kb(mdl_id))


async def prociphone(call: types.CallbackQuery, state: FSMContext):
    key = call.data.split("_")[1]
    idx = int(call.data.split("_")[2])
    with open("tg_bot/models.json", 'r') as file:
        data_js = json.load(file)
    model = data_js['iPhone'][key][idx]
    await call.message.edit_text(f"Выбрана модель: <i>{model}</i> ✅\nОпишите вашу поломку 👇", reply_markup= backtochoice_kb())
    await user.desc.set()
    async with state.proxy() as data:
        data['selected_model'] = model


async def backtochoice(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("Что бы вы хотели отремонтировать?", reply_markup= models_kb())
    async with state.proxy() as data:
        if "photos_remont" in data:
            for path in data['photos_remont']:
                os.remove(path)
    await state.finish()


async def procdesc(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['desc'] = message.text
    await user.photos.set()
    await message.answer("Добавьте фотографии, если это необходимо", reply_markup= photos_user_kb())


async def skip(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['photos_remont'] = []
        await call.message.edit_text(f"Модель: <i>{data['selected_model']}</i>\nОписание проблемы: <i>{data['desc']}</i>", reply_markup= final_appl_kb())
        await user.final.set()
        

async def handle_albums_remont(message: types.Message, album: List[types.Message], state: FSMContext):
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
            data['photos_remont'] = media_list

        await message.answer(f"Модель: <i>{data['selected_model']}</i>\nОписание проблемы: <i>{data['desc']}</i>", reply_markup= final_appl_kb())
        await user.final.set()
    

    

async def process_final(call: types.CallbackQuery, state: FSMContext):
    if call.data == "fremont_redakt":
        await call.message.edit_text("Выберите, что вы хотите отредактировать 👇", reply_markup= toredakt_user_kb())
        return

    action = int(call.data.split("_")[1])
    
    if not action:
        await call.message.edit_text("Здравствуйте!\n\nВыберите интересующий вас раздел в меню 👇", reply_markup= user_menu())

        async with state.proxy() as data:
            if "photos_remont" in data:
                for path in data['photos_remont']:
                    os.remove(path)

        await state.finish()
        return
    
    async with state.proxy() as data:
        id = await add_application(call.from_user, data['desc'],  data['selected_model'])
        services = await get_services_list_for_remont(call.from_user.id)
        for i in services:
            if len(data['photos_remont']) != 0:
                if len(data['photos_remont']) == 1:
                    await call.message.bot.send_photo(chat_id= i, photo= InputFile(data['photos_remont'][0]))
                
                elif len(data['photos_remont']) > 1:
                    await call.message.bot.send_media_group(chat_id= i, media = [InputMediaPhoto(InputFile(path)) for path in data['photos_remont']])
                        
                await call.message.bot.send_message(chat_id=i, text = f"Заявка на ремонт № {id}\n\nПользователь хочет отремонтировать <i>{data['selected_model']}</i>\nОписание проблемы: <i>{data['desc']}</i>\n\nПользователь также прикрепил фото к заявке, отправил их выше ☝", reply_markup= remont_appl_acception(id))
                
            else:
                await call.message.bot.send_message(chat_id=i, text = f"Заявка на ремонт № {id}\n\nПользователь хочет отремонтировать <i>{data['selected_model']}</i>\nОписание проблемы: <i>{data['desc']}</i>", reply_markup= remont_appl_acception(id))
        
        for i in data['photos_remont']:
            os.remove(i)
    
    await call.message.edit_text(f"Готово! Ваша заявка № {id} была успешно отправлена сервисам ✅", reply_markup= after_registration_user())
    await state.finish()


async def redakt_desc(call: types.CallbackQuery, state: FSMContext):
    if call.data == "tochange_back":
        async with state.proxy() as data:
            await call.message.edit_text(f"Модель: <i>{data['selected_model']}</i>\nОписание проблемы: <i>{data['desc']}</i>", reply_markup= final_appl_kb())
            return
    

    async with state.proxy() as data:
        if "desc" in data and "photo_remont" in data:
            del data['desc']
            del data['photos_remont']
            for path in data['photos_remont']:
                os.remove(path)

    await call.message.edit_text("Опишите вашу поломку 👇", reply_markup= backtochoice_kb())
    await user.desc.set()


async def decision_remont(call: types.CallbackQuery, state: FSMContext):
    if call.data == "racc_decl":
        
        await call.message.reply("Успешно отказано ✅")
    
    else:
        service_id = int(call.data.split("_")[1])
        link = (await get_service_info(service_id))[0]
        if not call.from_user.username:
            await call.message.answer("Чтобы принять ответ сервиса, вам нужно установить юзернейм в Telegram\n\nЭто обязательное условие для организации корректного взаимодействия пользователей с сервисами через бота!")
            return
        
        appl_id = int(call.message.text[call.message.text.index("№") + 1:].strip().split()[0])
        price = call.message.text.split("\n\n")[1].split("\n")[0].split(": ")[1]
        user_id, desc, model = await remont_application_info(appl_id)
        user_link = f'https://t.me/{call.from_user.username}'

        await call.message.bot.send_message(chat_id= service_id, text = f"Заявка № {appl_id}\n\n<a href = '{user_link}'>Пользователь</a> согласен на ваши условия по ремонту <i>{model}</i> ✅\nОписание проблемы: <i>{desc}</i>\nСтоимость: <i>{price}</i>", reply_markup= touser_link_kb(user_link))
    
        await close_appl_remont(appl_id, link)

        

        await call.message.reply("Ваш ответ успешно отправлен сервису ✅")
    
    try:
        await call.message.edit_reply_markup(None)
    except:
        pass

            
                
            


        
        

        
        