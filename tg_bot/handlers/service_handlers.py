from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.types import ContentType

from tg_bot.DBSM import remont_application_info, get_service_info, is_active_remont_appl, is_active_sell_appl, sell_application_info, get_sub_price, user_subscription, service_subscription, user_info
from tg_bot.keyboards import decline_remont_kb, choice_comm_kb, remont_decision, sell_decision, toskip, pay_kb
from tg_bot.states import service

admin_ids = [1261888898]

def register_service_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(proc_send_invoice, text = "serivicesub")
    dp.register_callback_query_handler(proc_appl_remont, text_startswith = "sgl")
    dp.register_callback_query_handler(proc_appl_sell, text_startswith = "ssgl")
    dp.register_callback_query_handler(decline_remont, state = service.all_states, text = "declineremont")
    dp.register_message_handler(proc_price_remont, state = service.remont_price)
    dp.register_callback_query_handler(choice_comm, state = service.remont_choice, text_startswith = "comm")
    dp.register_message_handler(proc_comm, state = service.remont_comm)
    dp.register_message_handler(proc_price, state = service.price)
    dp.register_callback_query_handler(skip, state = service.comm, text = "skip")
    dp.register_message_handler(process_final_sell, state = service.comm)
    dp.register_pre_checkout_query_handler(process_pre_checkout_query, state = "*")
    dp.register_message_handler(process_pay, content_types= ContentType.SUCCESSFUL_PAYMENT, state = "*")


async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await pre_checkout_query.bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


async def process_pay(message: types.Message, state: FSMContext):
    if message.successful_payment.invoice_payload == "service":
        await service_subscription(message.from_user.id, True)
        await message.answer("Ваша подписка активирована ✅️")
        
        
    elif message.successful_payment.invoice_payload == "user":
        await user_subscription(message.from_user.id, True)
        await message.answer("Ваша подписка активирована ✅️")
        info = await user_info(message.from_user.id)
        phone, adress = info[3:]
        for i in admin_ids:
            await message.bot.send_message(chat_id= i, text = f"Новый пользователь активировал подписку!!!\n\nЮзернейм телеграм - @{message.from_user.username}\nАдрес - {adress}\nТелефон - {phone}")




async def proc_appl_sell(call: types.CallbackQuery, state: FSMContext):

    action = int(call.data[4])
    if not action:
        try:
            await call.message.delete()
        except:
            pass
    else:
        sell_id = int(call.data.split("_")[1])
        check = await is_active_sell_appl(sell_id)
        if not check[0]:
            await call.message.answer(check[1] + "\n\nДля вызова главного меню введите <i>/start</i>")
            try:
                await call.message.delete()
            except:
                pass
            return
        
        if action == 2:
            user_id, model, price = await sell_application_info(sell_id)
            link, name = await get_service_info(call.from_user.id)
            await call.message.bot.send_message(chat_id= user_id, text = f"Сервис <a href = '{link}'>{name}</a> откликнулся на вашу заявку № {sell_id} на продажу/обмен <i>{model}</i>\n\nЦена или устройство на обмен, предложенное вами: <i>{price}</i>\n\nСервсис согласен на ваши условия ✅", reply_markup= sell_decision(call.from_user.id))
            await call.message.reply("Ответ на заявку отправлен пользователю ✅\n\nДля вызова главного меню введите <i>/start</i>")
            await call.message.edit_reply_markup(reply_markup= None)

        else:     
            await service.price.set()
            await call.message.answer("Введите стоимость/устройство, на которое готовы обменять 👇", reply_markup= decline_remont_kb())
            async with state.proxy() as data:
                data['sell_id'] = sell_id
                data['ishmsg'] = call.message



async def proc_send_invoice(call: types.CallbackQuery, state: FSMContext):
    price = (await get_sub_price())[0].value
    if price != "-":
        await call.message.bot.send_invoice(chat_id= call.from_user.id, title= "Оплата подписки", description= "Вы сможете получать заявки от пользователей после активации подписки ✅", payload= "service", currency= "RUB", provider_token= "381764678:TEST:94152" , prices=[{"label": "Руб", "amount": int(price) * 100}], start_parameter= "test", reply_markup= pay_kb())
    else:
        await call.message.answer("К сожалению, оплата подписки сейчас невозможна")


async def proc_price(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['pr_price'] = message.text
    await service.comm.set()
    await message.answer("Введите комментарий, если требуется 👇", reply_markup= toskip())


async def skip(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data['comment'] = "-"
        msg = data['ishmsg']
        user_id, model, price = await sell_application_info(data['sell_id'])
        link, name = await get_service_info(call.from_user.id)
        await call.message.bot.send_message(chat_id= user_id, text = f"Сервис <a href = '{link}'>{name}</a> откликнулся на вашу заявку № {data['sell_id']} на продажу/обмен <i>{model}</i>\n\nЦена или устройство на обмен, предложенное вами: <i>{price}</i>\n\nУсловия, предложенные сервисом: <i>{data['pr_price']}</i>\nКомментарий сервиса: <i>{data['comment']}</i>", reply_markup= sell_decision(call.from_user.id))
        await state.finish()
        await msg.reply("Ответ на заявку отправлен пользователю ✅\n\nДля вызова главного меню введите <i>/start</i>")
        await msg.edit_reply_markup(reply_markup=None)



async def process_final_sell(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['comment'] = message.text
        msg = data['ishmsg']
        user_id, model, price = await sell_application_info(data['sell_id'])
        link, name = await get_service_info(message.from_user.id)
        await message.bot.send_message(chat_id= user_id, text = f"Сервис <a href = '{link}'>{name}</a> откликнулся на вашу заявку № {data['sell_id']} на продажу/обмен <i>{model}</i>\n\nЦена или устройство на обмен, предложенное вами: <i>{price}</i>\n\nУсловия, предложенные сервисом: <i>{data['pr_price']}</i>\nКомментарий сервиса: <i>{data['comment']}</i>", reply_markup= sell_decision(message.from_user.id))
        await state.finish()
        await msg.reply("Ответ на заявку отправлен пользователю ✅\n\nДля вызова главного меню введите <i>/start</i>")
        await msg.edit_reply_markup(reply_markup=None)






async def proc_appl_remont(call: types.CallbackQuery, state: FSMContext):
    action = int(call.data[3])
    if not action:
        try:
            await call.message.delete()
        except:
            pass
    else:
        remont_id = int(call.data.split("_")[1])
        check = await is_active_remont_appl(remont_id)
        if not check[0]:
            await call.message.answer(check[1] + "\n\nДля вызова главного меню введите <i>/start</i>")
            try:
                await call.message.delete()
            except:
                pass
            return
            
                
        async with state.proxy() as data:
            data['remont_id'] = int(call.data.split("_")[1])
            data['msgg'] = call.message
        
        await service.remont_price.set()
        await call.message.answer("Введите стоимость ремонта 👇", reply_markup= decline_remont_kb())


async def decline_remont(call: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await call.message.edit_text("Добавления отклика отменено ❌\n\nДля вызова главного меню введите <i>/start</i>")


async def proc_price_remont(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['price_remont'] = message.text
    await service.remont_choice.set()
    await message.answer("Хотите оставить комментарий?", reply_markup= choice_comm_kb())


async def choice_comm(call: types.CallbackQuery, state: FSMContext):
    action = int(call.data[4])
    if not action:
        async with state.proxy() as data:
            data['comment'] = "-"
            msg = data['msgg']
            link, name = await get_service_info(call.from_user.id)
            user_id, desc, model = await remont_application_info(data['remont_id'])
            await call.message.bot.send_message(chat_id= user_id, text = f"Сервис <a href = '{link}'>{name}</a> принял вашу заявку № {data['remont_id']} на <i>ремонт {model}</i> ✅\n\nСтоимость: <i>{data['price_remont']}</i>\nКомментарий: <i>{data['comment']}</i>", reply_markup= remont_decision(call.from_user.id))
            await msg.reply("Ваш ответ был успешно отправлен пользователю ✅\n\nДля вызова главного меню введите <i>/start</i>")
            try:
                msg.edit_reply_markup(None)
            except:
                pass
            await state.finish()

    else:
        await service.remont_comm.set()
        await call.message.answer("Введите комментарий ниже 👇", reply_markup= decline_remont_kb())



async def proc_comm(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['comment'] = message.text
        msg = data['msgg']
        link, name = await get_service_info(message.from_user.id)
        user_id, desc, model = await remont_application_info(data['remont_id'])
        await message.bot.send_message(chat_id= user_id, text = f"Сервис <a href = '{link}'>{name}</a> принял вашу заявку № {data['remont_id']} на <i>ремонт {model}</i> ✅\n\nСтоимость: <i>{data['price_remont']}</i>\nКомментарий: <i>{data['comment']}</i>", reply_markup= remont_decision(message.from_user.id))
        await msg.reply("Ваш ответ был успешно отправлен пользователю ✅\n\nДля вызова главного меню введите <i>/start</i>")
        try:
            msg.edit_reply_markup(None)
        except:
            pass
        await state.finish()
            

            

            
        
