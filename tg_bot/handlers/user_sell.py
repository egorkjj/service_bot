from aiogram import Dispatcher, types, Bot
from aiogram.dispatcher import FSMContext
from aiogram.types import InputFile, InputMediaPhoto, MediaGroup

from tg_bot.keyboards import selltypes_kb, sellcreate_iphones_kb, sellmodels_kb, sellbacktochoice_kb, choice_new_kb, memory_kb, sizes_kb, finalsell_kb, user_menu, sell_appl_acception, after_registration_user, touser_link_kb
from tg_bot.DBSM import get_services_list_for_sell, add_application_sell, get_service_info, sell_application_info, close_appl_sell, is_active_sell_appl, sell_application_full_info
from tg_bot import generate_random_string
from tg_bot.states import sell

import json, os, asyncio
from typing import List
from threading import Thread as th

def register_sell_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(process_models, text_startswith = "smdl")
    dp.register_callback_query_handler(backtomodels, text = "sellbackfrommodels")
    dp.register_callback_query_handler(backtomodels, text = "sellbackfromiphones")
    dp.register_callback_query_handler(procmodel, text_startswith ="и_")
    dp.register_callback_query_handler(prociphone, text_startswith = "м_")
    dp.register_callback_query_handler(backtochoice, text = "sellbacktchs", state = sell.all_states)
    dp.register_callback_query_handler(memoryproc, state = sell.memory, text_startswith = "m_")
    dp.register_callback_query_handler(sizeproc, text_startswith = "s_", state = sell.size)
    dp.register_message_handler(handle_albums_sell, state = sell.photos, content_types= types.ContentType.ANY)
    dp.register_message_handler(proc_sost, state= sell.sost)
    dp.register_message_handler(proc_equip, state= sell.equip)
    dp.register_message_handler(proc_acum, state = sell.acum)
    dp.register_message_handler(proc_final, state = sell.final)
    dp.register_callback_query_handler(proc_choice, state = sell.final, text_startswith = "fsell_")
    dp.register_callback_query_handler(proc_decision_sell, text_startswith = "rsell_")


async def process_models(call: types.CallbackQuery, state: FSMContext):
    mdl = call.data.split("_")[1]
    if mdl == "back":
        await call.message.edit_text("Что вас интересует?", reply_markup= choice_new_kb())
        return
    else:
        await call.message.edit_text("Выберите интересующую вас модель ниже 👇", reply_markup= selltypes_kb(mdl))


async def backtomodels(call: types.CallbackQuery, state: FSMContext):
    if call.data == "sellbackfrommodels":
        await call.message.edit_text("Что бы вы хотели продать/обменять?", reply_markup= sellmodels_kb())
    else:
        await call.message.edit_text("Выберите интересующую вас модель ниже 👇", reply_markup= selltypes_kb("iPhone"))


async def procmodel(call: types.CallbackQuery, state: FSMContext):
    gadget = call.data.split("_")[1]
    mdl_id = int(call.data.split("_")[2])
    with open("tg_bot/models.json", 'r') as file:
        data_js = json.load(file)
    if "iPhone" not in gadget:
        async with state.proxy() as data:
            data['model'] = data_js[gadget][mdl_id]
            data['gadget'] = gadget
            if gadget not in ["MacBook", "iPad"]:
                data['memory'] = "-"
                if gadget != "Apple Watch":
                    await call.message.edit_text(f"Выбрана модель: <i>{data_js[gadget][mdl_id]}</i> ✅\nПрикрепите фотографии 👇", reply_markup= sellbacktochoice_kb())
                    await sell.photos.set()
                    data['size'] = "-"
                else:
                    await call.message.edit_text("Выберите размер экрана ваших часов <i>Apple Watch</i> 👇", reply_markup= sizes_kb())
                    await sell.size.set()
            else:
                if gadget == "MacBook":
                    await call.message.edit_text(f"Выбрана модель: <i>{data_js[gadget][mdl_id]}</i> ✅\nВыберите объем памяти вашего <i>MacBook</i> 👇", reply_markup= memory_kb())
                else:
                    await call.message.edit_text(f"Выбрана модель: <i>{data_js[gadget][mdl_id]}</i> ✅\nВыберите объем памяти вашего <i>iPad</i> 👇", reply_markup= memory_kb())
                await sell.memory.set()
                data['size'] = "-"

    else:
        await call.message.edit_text("Выберите интересующую вас модель ниже 👇", reply_markup= sellcreate_iphones_kb(mdl_id))


async def prociphone(call: types.CallbackQuery, state: FSMContext):
    key = call.data.split("_")[1]
    idx = int(call.data.split("_")[2])
    with open("tg_bot/models.json", 'r') as file:
        data_js = json.load(file)
    model = data_js['iPhone'][key][idx]
    await call.message.edit_text(f"Выбрана модель: <i>{model}</i> ✅\nВыберите объем памяти вашего <i>iPhone</i> 👇", reply_markup= memory_kb())
    await sell.memory.set()
    async with state.proxy() as data:
        data['model'] = model
        data['gadget'] = "iPhone"
        data['size'] = "-"

async def backtochoice(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        if "photos_sell" in data:
            for path in data['photos_sell']:
                os.remove(path)

    await call.message.edit_text("Что бы вы хотели продать/обменять?", reply_markup= sellmodels_kb())
    await state.finish()


async def memoryproc(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['memory'] = call.data.split("_")[1]
        await call.message.edit_text(f"Выбрана модель: <i>{data['model']}</i> ✅\nВыбран объем памяти: <i>{data['memory']}</i> ✅\nПрикрепите фотографии 👇", reply_markup= sellbacktochoice_kb())
        await sell.photos.set()


async def sizeproc(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['size'] = call.data.split("_")[1]
        await call.message.edit_text(f"Выбрана модель: <i>{data['model']}</i> ✅\nВыбран размер экрана: <i>{data['size']}</i> ✅\nПрикрепите фотографии 👇", reply_markup= sellbacktochoice_kb())
        await sell.photos.set()


async def handle_albums_sell(message: types.Message, album: List[types.Message], state: FSMContext):
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
            data['photos_sell'] = media_list

    async with state.proxy() as data:
        await message.answer(f"Опишите состояние <i>{data['gadget']}</i> 👇", reply_markup= sellbacktochoice_kb())
        await sell.sost.set()
    

async def proc_sost(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['sost'] = message.text
        await message.answer(f"Напишите, что входит в комплект с <i>{data['gadget']}</i> 👇", reply_markup= sellbacktochoice_kb())
        await sell.equip.set()


async def proc_equip(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['equip'] = message.text
        if data['gadget'] != "AirPods":
            await message.answer(f"Укажите емкость акумулятора <i>{data['gadget']}</i> 👇", reply_markup= sellbacktochoice_kb())
            await sell.acum.set()
        else:
            data['acum'] = "-"
            await message.answer("Какую сумму или какое устройство вы хотели бы получить за ваши <i>AirPods</i> ?", reply_markup= sellbacktochoice_kb())
            await sell.final.set()


async def proc_acum(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['acum'] = message.text
        await message.answer(f"Какую сумму или какое устройство вы хотели бы получить за <i>{data['gadget']}</i> ?", reply_markup= sellbacktochoice_kb())
        await sell.final.set()


async def proc_final(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['final_sell'] = message.text
        if data['size'] != "-":
            await message.answer(f"Категория: <i>Apple Watch</i>\nМодель: <i>{data['model']}</i>\n\nРазмер экрана: <i>{data['size']}</i>\nОстаточная емкость аккумулятора: <i>{data['acum']}</i>\nЧто входит в комплект: <i>{data['equip']}</i>\nСостояние устройства: <i>{data['sost']}</i>\nПредложенная цена/устройство: <i>{message.text}</i>", reply_markup= finalsell_kb())
        else:
            if data['gadget'] == "AirPods":
                await message.answer(f"Категория: <i>AirPods</i>\nМодель: <i>{data['model']}</i>\n\nЧто входит в комплект: <i>{data['equip']}</i>\nСостояние устройства: <i>{data['sost']}</i>\nПредложенная цена/устройство: <i>{message.text}</i>", reply_markup= finalsell_kb())
            else:
                await message.answer(f"Категория: <i>{data['gadget']}</i>\nМодель: <i>{data['model']}</i>\n\nВстроенная память: <i>{data['memory']}</i>\nОстаточная емкость аккумулятора: <i>{data['acum']}</i>\nЧто входит в комплект: <i>{data['equip']}</i>\nСостояние устройства: <i>{data['sost']}</i>\nПредложенная цена/устройство: <i>{message.text}</i>", reply_markup= finalsell_kb())
    


async def proc_choice(call: types.CallbackQuery, state: FSMContext):
    action = int(call.data.split("_")[1])
    if action:
        async with state.proxy() as data:
            appl_id = await add_application_sell(call.from_user, data['model'], data['size'], data['memory'], data['equip'], data['final_sell'], data['acum'], data['sost'])
            th(target= thread_runner, args= (appl_id, )).start()
            for i in await get_services_list_for_sell(call.from_user.id):

                if len(data['photos_sell']) == 1:
                    await call.message.bot.send_photo(chat_id= i, photo= InputFile(data['photos_sell'][0]))
                else:
                    await call.message.bot.send_media_group(chat_id= i, media = [InputMediaPhoto(InputFile(path)) for path in data['photos_sell']])

                if data['size'] != "-":
                    await call.message.bot.send_message(chat_id= i, text = f"Пользователь хочет отремонтировать <i>{data['model']}</i>\n\nРазмер экрана: <i>{data['size']}</i>\nОстаточная емкость аккумулятора: <i>{data['acum']}</i>\nЧто входит в комплект: <i>{data['equip']}</i>\nСостояние устройства: <i>{data['sost']}</i>\nПредложенная цена/устройство: <i>{data['final_sell']}</i>\n\nФотографии отправил выше ☝", reply_markup= sell_appl_acception(appl_id))
                else:
                    if data['gadget'] == "AirPods":
                        await call.message.bot.send_message(chat_id= i, text = f"Пользователь хочет отремонтировать <i>{data['model']}</i>\n\nЧто входит в комплект: <i>{data['equip']}</i>\nСостояние устройства: <i>{data['sost']}</i>\nПредложенная цена/устройство: <i>{data['final_sell']}</i>\n\nФотографии отправил выше ☝", reply_markup= sell_appl_acception(appl_id))
                    else:
                        await call.message.bot.send_message(chat_id= i, text = f"Пользователь хочет отремонтировать <i>{data['model']}</i>\n\nВстроенная память: <i>{data['memory']}</i>\nОстаточная емкость аккумулятора: <i>{data['acum']}</i>\nЧто входит в комплект: <i>{data['equip']}</i>\nСостояние устройства: <i>{data['sost']}</i>\nПредложенная цена/устройство: <i>{data['final_sell']}</i>\n\nФотографии отправил выше ☝", reply_markup= sell_appl_acception(appl_id))
            
            for i, path in enumerate(data['photos_sell']):
                os.rename(path, f"tg_bot/photos/sellappl{appl_id}_{i}.jpg")
            
            await call.message.edit_text(f"Готово! Ваша заявка на продажу/обмен № {appl_id} была успешно отправлена сервисам ✅", reply_markup= after_registration_user())
            await state.finish()

    else:
        await call.message.edit_text("Здравствуйте!\n\nВыберите интересующий вас раздел в меню 👇", reply_markup= user_menu())
        
        async with state.proxy() as data:
            if "photos_sell" in data:
                for path in data['photos_sell']:
                    os.remove(path)
        
        await state.finish()
        return



async def proc_decision_sell(call: types.CallbackQuery, state: FSMContext):
    if call.data == "rsell_decl":
        
        await call.message.reply("Успешно отказано ✅")
    
    else:
        service_id = int(call.data.split("_")[1])
        link = (await get_service_info(service_id))[0]
        if not call.from_user.username:
            await call.message.answer("Чтобы принять ответ сервиса, вам нужно установить юзернейм в Telegram\n\nЭто обязательное условие для организации корректного взаимодействия пользователей с сервисами через бота!")
            return
        
        appl_id = int(call.message.text[call.message.text.index("№") + 1:].strip().split()[0])
        user_id, model, price = await sell_application_info(appl_id)
        user_link = f'https://t.me/{call.from_user.username}'

        await call.message.bot.send_message(chat_id= service_id, text = f"Заявка № {appl_id}\n\n<a href = '{user_link}'>Пользователь</a> согласен на ваши условия по продаже/обмену <i>{model}</i> ✅", reply_markup= touser_link_kb(user_link))
    
        await close_appl_sell(appl_id, link)
          
        await call.message.reply(text = "Ваш ответ успешно отправлен сервису ✅")
    
    try:
        await call.message.edit_reply_markup(reply_markup= None)
    except:
        pass


async def send_push_to_admins(appl_id):
    await asyncio.sleep(21) #57601
    bot = Bot(token = "7060072417:AAEMd9zhYgaQoE_m-HldTbsSex0EvkTomNI")
    if (await is_active_sell_appl(appl_id))[1] == "К сожалению, данную заявку нельзя принять (":
        info = await sell_application_full_info(appl_id)
        text = f"Заявку на продажу/обмен не приняли за 16 часов!!\nМодель: {info[0]}\nКомплект: {info[1]}\nСостояние: {info[2]}\nБатарея: {info[3]}\nЖелаемая цена: {info[4]}\nПамять: {info[5]}\nРазмер дисплея: {info[6]}"
        count = 1
        if not os.path.isfile(f"tg_bot/photos/sellappl{appl_id}_1.jpg"):
            await bot.send_photo(chat_id= 1441962095, photo= InputFile(f"tg_bot/photos/sellappl{appl_id}_0.jpg"), caption = text)
        else:
            group = MediaGroup()
            while os.path.isfile(f"tg_bot/photos/sellappl{appl_id}_{count}.jpg"):

                group.attach_photo(InputFile(f"tg_bot/photos/sellappl{appl_id}_{count}.jpg"))
                count += 1

            await bot.send_media_group(chat_id= 1441962095, text = text)
        
    count = 0
    while os.path.isfile(f"tg_bot/photos/sellappl{appl_id}_{count}.jpg"):
        os.remove(f"tg_bot/photos/sellappl{appl_id}_{count}.jpg")
        count += 1

def thread_runner(appl_id):
    asyncio.run(send_push_to_admins(appl_id))