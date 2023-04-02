from imports import *

bot = aio.Bot(token=config.TOKEN_BOT)
dp = aio.Dispatcher(bot)

logging.basicConfig(level=logging.DEBUG)
#Открываем файл с сохраненными данными о городе пользователя, если файла нету то создаем словарь и записывает его в новый файл
try:
    with open('user_city.pickle', 'rb') as f:
        user_city = pickle.load(f)
except FileNotFoundError:
    user_city = {}
    with open('user_city.pickle', 'wb') as f:
        pickle.dump(user_city, f)


@dp.message_handler(commands=['start'])
async def process_start_command(message: aio.types.Message):
    await message.reply("""Привет! Я бот который подскажет тебе какая погода за окном! 
Напиши название города. Я запомню его. 
Затем ты можешь просто написать /weather и я покажу погоду в этом городе""")

@dp.message_handler(commands=['weather'])
async def send_weather(message: aio.types.Message):
    user_id = message.from_user.id
    city = user_city.get(user_id)
    if city:
        async with aiohttp.ClientSession() as session:
            async with session.get(f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={config.TOKEN_WEATHER}&units=metric') as resp:
                data = await resp.json()
                if data.get('cod') == 200:
                    temp = data['main']['temp']
                    humidity = data['main']['humidity']
                    wind_speed = data['wind']['speed']
                    pressure = data['main']['pressure']
                    await message.answer(f'''Текущая температура в городе {city} составляет {temp}°C. 
Влажность: {humidity}%. 
Скорость ветра: {wind_speed} м/с. 
Давление: {pressure} гПа.''')
                else:
                    await message.answer(f'Извините, я не смог найти информацию о погоде для города {city}.')
    else:
        await message.answer('Я не знаю твоего города. Напиши мне название города и я запомню его.')


@dp.message_handler()
async def set_city(message: aio.types.Message):
    user_id = message.from_user.id
    city = message.text
    user_city[user_id] = city
    # Сохраняем словарь в файл
    with open('user_city.pickle', 'wb') as f:
        pickle.dump(user_city, f)
    await message.answer(f'Я запомнил твой город: {city}. Теперь ты можешь написать /weather и я покажу тебе текущую погоду.')