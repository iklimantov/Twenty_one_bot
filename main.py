import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from services.scripts import start_layout, read_arm, count_points, more_card
from environs import Env

env = Env()  # Создаем экземпляр класса Env
env.read_env()  # Методом read_env() читаем файл .env и загружаем из него переменные в окружение

BOT_TOKEN = env('BOT_TOKEN')


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

users = {} # Словарь всех пользователей


# Хэндлер /start. Инициализируем нового пользователя
async def process_start_command(message: Message):
    await message.answer(text='Привет! Я бот для игры в 21.\n\n'
                              'Для начала игры введите /game\n'
                              'Для получения списка команд введите /help')
    if message.from_user.id not in users:
        users[message.from_user.id] = {'in_game': False,
                                       'total_games': 0,
                                       'wins': 0, 'user_deck': None,
                                       'deck': None,
                                       'dealer_deck': None}


# Хэндлер /help
async def process_help_command(message: Message):
    await message.answer(text='Список доступных команд:\n'
                              '/game - начать игру\n'
                              '/quit - закончить игру\n'
                              '/rules - посмотреть правила игры\n'
                              '/stat - посмотреть статистику')

# Хэндлер /rules
async def process_rules_command(message: Message):
    with open('lexicon/rules.txt', encoding='UTF-8') as file:
        lines = file.read()
    await message.answer(text=lines)
    await message.answer(text='Список доступных команд: /help')


# Хэндлер /game
async def process_game_command(message: Message):
    if users[message.from_user.id]['in_game']:
        await message.answer(text='Игра и так в процессе.\n'
                                  'Если хотите закончить, введите /quit')
    else:
        await message.answer(text='Список очков:\n'
                                  '2 - 10 в соответствии с номиналом\n'
                                  'Валет - 10\n'
                                  'Дама - 10\n'
                                  'Король - 10\n'
                                  'Туз - 1 или 11')
        await asyncio.sleep(2)
        await message.answer(text='Тасую колоду...')
        await asyncio.sleep(1)
        users[message.from_user.id]['in_game'] = True
        users[message.from_user.id]['total_games'] += 1
        (users[message.from_user.id]['dealer_deck'],
         users[message.from_user.id]['user_deck'],
         users[message.from_user.id]['deck']) = start_layout() # Раскладываем колоду дилера и
                                                                        # пользователя. Получаем оставшуюся колоду
        await message.answer(text=f'Рука дилера:\n'
                                  f'{read_arm(users[message.from_user.id]['dealer_deck'], True)}')
        await message.answer(text=f'Ваша рука:\n'
                                  f'{read_arm(users[message.from_user.id]['user_deck'])}')
        await asyncio.sleep(3)
        await message.answer(text='Еще или хватит?\n'
                                  'Напечатайте пожалуйста текстом')


# Хэндлер сообщений добора карт
async def process_more_answer(message: Message):
    if not users[message.from_user.id]['in_game']:
        await message.answer(text='Я не пониманию, что вы сейчас хотите.\n'
                                  'Если хотите сыграть, введите /game\n'
                                  'Полный список команд: /help')
    else:
        more_card(users[message.from_user.id]['user_deck'], users[message.from_user.id]['deck'])
        await message.answer(text=f'Ваша рука:\n'
                                  f'{read_arm(users[message.from_user.id]['user_deck'])}')
        if count_points(users[message.from_user.id]['user_deck']) > 21:
            users[message.from_user.id]['in_game'] = False
            await message.answer(text='У вас перебор. Вы проиграли :(\nСыграем еще?\n/game')
        else:
            await message.answer(text='Еще или хватит?')


# Хэндлер сообщений остановки набора кард
async def process_enough_answer(message: Message):
    if not users[message.from_user.id]['in_game']:
        await message.answer(text='Как жаль, что вы не хотите со мной играть :(\n'
                                  'Как надумаете, заходите.')
    else:
        await message.answer(text=f'Отлично! Ваша сумма очков: {count_points(users[message.from_user.id]['user_deck'])}')
        await asyncio.sleep(2)
        await message.answer(text='Посмотрим, что у дилера.')
        await asyncio.sleep(1)
        await message.answer(text=f'Рука дилера:\n'
                                  f'{read_arm(users[message.from_user.id]['dealer_deck'])}')
        await asyncio.sleep(3)
        while count_points(users[message.from_user.id]['dealer_deck']) < 17:
            more_card(users[message.from_user.id]['dealer_deck'], users[message.from_user.id]['deck'])
            await message.answer(text=f'Рука дилера:'
                                      f'\n{read_arm(users[message.from_user.id]['dealer_deck'])}')
            await asyncio.sleep(3)

        user_points = count_points(users[message.from_user.id]['user_deck'])
        dealer_points = count_points(users[message.from_user.id]['dealer_deck'])
        if dealer_points <= 21:
            await message.answer(text=f"Дилер остановился.\n"
                                      f"Сумма очков дилера: {dealer_points}\n"
                                      f"Ваша: {user_points}")
            await asyncio.sleep(2)

            if dealer_points == user_points:
                await message.answer(text='У вас ничья!\nСыграем еще раз?\n/game')
                users[message.from_user.id]['in_game'] = False
            elif dealer_points > user_points:
                await message.answer(text='К сожалению, вы проиграли :(.\n'
                                          'Но не отчаивайтесь! Всегда можно сыграть еще!\n/game')
                users[message.from_user.id]['in_game'] = False
            else:
                await message.answer(text='ВЫ ПОБЕДИЛИ!!!\n\n'
                                          'Сердечно вас поздравляю и предлагаю сыграть снова -> /game')
                users[message.from_user.id]['in_game'] = False
                users[message.from_user.id]['wins'] += 1
        else:
            await message.answer(text='У дилера перебор, а это значит, что\n'
                                      'ВЫ ПОБЕДИЛИ!!!\n\n'
                                      'Сердечно вас поздравляю и предлагаю сыграть снова -> /game')
            users[message.from_user.id]['in_game'] = False
            users[message.from_user.id]['wins'] += 1


# Хэндлер команды /stat
async def process_stat_command(message: Message):
    if users[message.from_user.id]['in_game']:
        await message.answer(text='Мы же сейчас играем!\nВот закончим, и спросишь еще раз.'
                                  '\nДля выхода из игры введи /quit')
    else:
        await message.answer(text=f'Статистика.\n'
                                  f'Игр сыграно: {users[message.from_user.id]['total_games']}\n'
                                  f'Побед: {users[message.from_user.id]['wins']}\n'
                                  f'Процент побед: '
                                  f'{round(users[message.from_user.id]['wins'] / 
                                           users[message.from_user.id]['total_games'] * 100) 
                                  if users[message.from_user.id]['total_games'] > 0 else 0} %')


# Хэндлер команды /quit
async def process_quit_command(message: Message):
    if not users[message.from_user.id]['in_game']:
        await message.answer(text='Мы же и так с вами не играем (к сожалению).\n'
                                  'Если захотите, просто введите /game')
    else:
        users[message.from_user.id]['in_game'] = False
        await message.answer(text='Спасибо за игру!\n'
                                  'Буду рад видеть вас снова :)\n'
                                  'Список доступных команд: /help')


# Хэндлер всех остальных сообщений пользователя
async def process_other_messages(message: Message):
    await message.answer(text='Я еще не очень умный бот, на понимаю, что это значит :(\n'
                              'Для списка доступных команд введите /help')


dp.message.register(process_start_command, Command(commands='start'))
dp.message.register(process_help_command, Command(commands='help'))
dp.message.register(process_rules_command, Command(commands='rules'))
dp.message.register(process_game_command, Command(commands='game'))
dp.message.register(process_stat_command, Command(commands='stat'))
dp.message.register(process_quit_command, Command(commands='quit'))
dp.message.register(process_more_answer, F.text.lower().in_(['еще', 'да', 'давай', 'давай еще', 'ещё', 'давай ещё',
                                                             'ок', 'угу']))
dp.message.register(process_enough_answer, F.text.lower().in_(['хватит', 'стоп', 'достаточно', 'все', 'я все', 'всё',
                                                               'я всё', 'нет']))
dp.message.register(process_other_messages)


if __name__ == '__main__':
    dp.run_polling(bot)