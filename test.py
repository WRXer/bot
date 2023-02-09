import asyncio
from auth_data import token
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from datetime import datetime, timedelta
import pytz
import json
import time
import aioschedule

timez = time
#import config

bot = Bot(token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class InputDateTime(StatesGroup):
    input_date = State()
    input_time = State()


def user_dates(user_date):

    with open('user_date_as.json', 'r', encoding='utf-8') as file:
        raw_json = file.read()
        words = json.loads(raw_json)
        user_data = words
        # Вычисляем самое ближайшее время
        z = user_data[0]["0"]["year"], user_data[0]["0"]["month"], user_data[0]["0"]["day"], user_data[0]["0"]["hour"], \
        user_data[0]["0"]["minute"]
        day_z = "".join(list(z))
        key_z = 0
        tz_samara = pytz.timezone("Europe/Samara")
        dt = datetime.now(tz_samara)
        dtn = dt.strftime('%Y%m%d%H%M')  # DAtetime NOW
        usdt = user_date["year"], user_date["month"], user_date["day"], user_date["hour"], user_date["minute"]
        usdt = "".join(list(usdt))
        for i in user_data:
            for key, value in i.items():
                k = datetime.strptime(f"{value['day']}/{value['month']}/{value['year']} {value['hour']}:{value['minute']}",
                                      "%d/%m/%Y %H:%M")
                if timedelta.total_seconds((k) - datetime.now()) > timedelta.total_seconds(timedelta(hours=4)):
                    print(k)
                    x = value["year"], value["month"], value["day"], value["hour"], value["minute"]
                    x = "".join(list(x))
                    if day_z > dtn and x > dtn:
                        if day_z > x:
                            day_z = x
                            key_z = key

                        else:
                            continue
                    elif day_z < dtn:
                        day_z = usdt
                        key_z = key

                else:
                    continue
        return key_z

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Меня зовут remind_bot! Для создания уведомления сначала пиши дату, после напоминание! 'ДД.ММ.ГГГГ ЧЧ:ММ'")
    await InputDateTime.input_time.set()


@dp.message_handler(content_types=['text'])
async def input_time(message: types.Message, state: FSMContext):
    tz_samara = pytz.timezone("Europe/Samara")
    dt = datetime.now(tz_samara)
    print("start 1")
    user_date = {}
    word = message.text.split(' ')

    if ":" in word[0]:
        time = word[0].split(":")
        user_date['year'] = dt.strftime('%Y')
        user_date['month'] = dt.strftime('%m')
        user_date['day'] = dt.strftime('%d')
        user_date['hour'] = time[0]
        user_date['minute'] = time[1]
        user_date["user_text"] = word[1:]
        with open('user_date_as.json', 'r', encoding='utf-8') as file:
            raw_json = file.read()
            words = json.loads(raw_json)
            user_data = words
        count = 0
        for i in user_data:
            for key in i.keys():
                x = int(key)
                if count != x:
                    count = x
                else:
                    continue
        new_count = count + 1
        if new_count > count:
            i = {}
            i[new_count] = user_date
            user_data.append(i)
        with open('user_date_as.json', 'w') as outfile:
            json.dump(user_data, outfile, indent=1)
        async with state.proxy() as data:
            data['datetime'] = datetime.strptime(f"{user_date['day']}/{user_date['month']}/{user_date['year']} {user_date['hour']}:{user_date['minute']}", "%d/%m/%Y %H:%M")
            print(data['datetime'])
            if data['datetime'] > datetime.now():
                await message.answer("Ваше напоминание принято!")
                print("принято")
                with open('user_date_as.json', 'r', encoding='utf-8') as file:
                    raw_json = file.read()
                    words = json.loads(raw_json)
                    user_data = words

                    print(datetime.now()+ timedelta(hours=4))
                    key_z = user_dates(user_date)
                    for p in user_data:
                        for w, t in p.items():
                            if w == key_z:
                                data['datetime'] = datetime.strptime(f"{t['day']}/{t['month']}/{t['year']} {t['hour']}:{t['minute']}", "%d/%m/%Y %H:%M")
                                print(data['datetime'])
                                await asyncio.sleep(timedelta.total_seconds(data['datetime'] - datetime.now() + timedelta(hours=4)))
                                await message.answer(f"Время пришло: {t['user_text']}")

                            else:
                                continue

    else:
        await message.answer("НЕВЕРНЫЙ формат! Введите дату в самом начале!")





if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)