import os
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup, \
    InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
import sqlite3 as sq
from bs4 import BeautifulSoup


def sql_start():
    global base, cur
    base = sq.connect('html_text_info.db')
    cur = base.cursor()
    if base:
        print('Бот успешно подключен к базе данных')
        base.execute('CREATE TABLE IF NOT EXISTS info(controlnum TEXТ, color TEXT, begstr TEXT)')
        base.commit()


def user_info():
    global userrr, currrr
    userrr = sq.connect('user_info.db')
    currrr = userrr.cursor()
    if userrr:
        print('Бот успешно выдал права администраторам')
        userrr.execute('CREATE TABLE IF NOT EXISTS info(usernames TEXT)')
        userrr.commit()


async def sql_add_admins(state):
    async with state.proxy() as data:
        currrr.execute('INSERT INTO info VALUES(?)', tuple(data.values()))
        userrr.commit()


async def sql_add_command(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO info VALUES(?,?,?)', tuple(data.values()))
        base.commit()


async def sql_read(message):
    for ret in cur.execute('SELECT * FROM info').fetchall():
        await bot.send_message(message.from_user.id, f'Называние строки: {ret[0]}\nЦвет: {ret[1]}\nТекст: {ret[2]}')


async def sql_read2():
    return cur.execute('SELECT * FROM info').fetchall()


async def sql_delete_command(data):
    cur.execute('DELETE FROM info WHERE controlnum = ?', (data,))
    base.commit()


bot = Bot(token='5809475526:AAEhtExdDhiZ28ueRUQYzPOtKnDo3Al-MFE')


async def on_startup(_):
    print('Бот вышел в онлайн')
    sql_start()
    user_info()


storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
ID = "+XDFOSSjF64I3ZTFi"


class FSMAdmin(StatesGroup):
    controlnum = State()
    color = State()
    text = State()


class RegisterState(StatesGroup):
    username = State()


# подключение к базе данных
base = sq.connect('html_text_info.db')
cur = base.cursor()

# функция для получения данных из базы данных и генерации html кода
def generate_html():
    cur.execute("SELECT color, begstr FROM info")
    data = cur.fetchall()

    # создание html кода с заменой значений из базы данных
    html_code = '<html><body style="overflow-y:hidden"><big><h1><h1><marquee scrollamount="30" onselectstart="return false;">'

    for i in range(len(data)):
        color = data[i][0]
        begstr = data[i][1]
        html_code += f'<span style="color:{color}">{begstr}</span>'
        if i < len(data) - 1:
            html_code += '; '

    html_code += '</marquee><h1><h1><big></body></html>'

    return html_code

# обработчик команды /reload
@dp.message_handler(commands=['reload'])
async def reload_html(message: types.Message):
    html_code = generate_html()
    with open('index.html', 'w') as f:
        f.write(html_code)
    await message.answer('HTML страница успешно обновлена')



@dp.message_handler(commands=['register'])
async def register_user(message: types.Message):
    if message.from_user.username == 'ecark':
        await bot.send_message(message.chat.id, 'Какого пользователя вы хотите зарегистрировать?')
        await RegisterState.username.set()
    else:
        await message.reply('⛔️ У вас нет прав для выполнения этой команды!')


@dp.message_handler(state=RegisterState.username, content_types=types.ContentTypes.ANY)
async def process_username(message: types.Message, state: FSMContext):
    if message.text:
        if len(message.text) > 40:
            await message.reply('Ошибка. Длина вашего сообщения превышает 40 символов.')
            return
        username = message.text
        currrr.execute('INSERT INTO info(usernames) VALUES (?)', (username,))
        userrr.commit()
        await message.reply('Пользователь успешно зарегистрирован!')
        await state.finish()
    else:
        await message.reply('Ошибка. Отправьте текстовое сообщение.')
        return


@dp.message_handler(commands=['userlist'])
async def show_usernames(message: types.Message):
    if message.from_user.username == 'ecark':
        currrr.execute('SELECT usernames FROM info')
        result = currrr.fetchall()
        usernames = [row[0] for row in result]
        if usernames:
            await bot.send_message(message.from_user.id, '⚠️ Список активных юзернеймов ⚠️')
            for username in usernames:
                inline_keyboard = types.InlineKeyboardMarkup()
                button = types.InlineKeyboardButton(text='Удалить', callback_data=f'delete_username:{username}')
                inline_keyboard.add(button)
                await message.reply(username, reply_markup=inline_keyboard)
        else:
            await message.reply('⛔️ Список активных юзернеймов пуст!')
    else:
        await message.reply('⛔️ У вас нет прав для выполнения этой команды!')


@dp.callback_query_handler(lambda c: c.data.startswith('delete_username'))
async def delete_username(callback_query: types.CallbackQuery):
    if callback_query.from_user.username == 'ecark':
        username = callback_query.data.split(':')[1]
        currrr.execute('DELETE FROM info WHERE usernames = ?', (username,))
        userrr.commit()
        await bot.answer_callback_query(callback_query.id, text=f'⛔️ Юзернейм {username} удален ⛔️')
    else:
        await bot.answer_callback_query(callback_query.id, text='⛔️ У вас нет прав для выполнения этой операции!')


@dp.message_handler(commands=["some_command"])
async def some_command_handler(message: types.Message):
    username = message.from_user.username
    currrr = userrr.cursor()
    try:
        currrr.execute("SELECT usernames FROM info WHERE usernames=?", (username,))
        result = currrr.fetchone()
    finally:
        currrr.close()
    if result:
        await message.answer("Команда выполнена")
    else:
        await message.answer("⛔️ У вас нет прав для выполнения этой команды!")


@dp.message_handler(state="*", commands='exit')
@dp.message_handler(Text(equals='exit', ignore_case=True), state='*')
async def cansel_handler(message: types.Message, state: FSMContext):
    username = message.from_user.username
    currrr = userrr.cursor()
    try:
        currrr.execute("SELECT usernames FROM info WHERE usernames=?", (username,))
        result = currrr.fetchone()
    finally:
        currrr.close()
    if result:
        current_state = await state.get_state()
        if current_state is None:
            return
        await state.finish()
        await message.reply('Ввод данных успешно отменен')
    else:
        await message.answer("⛔️ У вас нет прав для выполнения этой команды!")


@dp.message_handler(commands='add_text', state=None)
async def cm_start(message: types.Message):
    username = message.from_user.username
    currrr = userrr.cursor()
    try:
        currrr.execute("SELECT usernames FROM info WHERE usernames=?", (username,))
        result = currrr.fetchone()
    finally:
        currrr.close()
    if result:
        await FSMAdmin.controlnum.set()
        await message.reply("Введите имя для новой строки")
    else:
        await message.answer("⛔️ У вас нет прав для выполнения этой команды!")


# список цветов для кнопок
colors = ['Fuchsia', 'Purple', 'Red', 'Maroon', 'Yellow', 'Olive', 'Lime', 'Green', 'Aqua', 'Teal', 'Blue', 'Navy',
          'Gray', 'Black', 'Honeydew', 'LavenderBlush']


@dp.message_handler(state=FSMAdmin.controlnum, content_types=types.ContentTypes.ANY)
async def set_name(message: types.Message, state: FSMContext):
    username = message.from_user.username
    currrr = userrr.cursor()
    try:
        currrr.execute("SELECT usernames FROM info WHERE usernames=?", (username,))
        result = currrr.fetchone()
    finally:
        currrr.close()
    if result:
        if message.text:
            if len(message.text) > 20:
                await message.reply("Нельзя указать имя строки, которое длиннее 20 символов.")
            else:
                async with state.proxy() as data:
                    data['controlnum'] = message.text
                    # создаем список кнопок с цветами
                    buttons = [InlineKeyboardButton(color, callback_data=color) for color in colors]
                    # создаем объект клавиатуры с кнопками
                    keyboard = InlineKeyboardMarkup().add(*buttons)
                    await FSMAdmin.next()
                    await message.reply('Укажите цвет текста', reply_markup=keyboard)
        else:
            await message.reply('Пожалуйста, введите имя строки.')
    else:
        await message.answer("⛔️ У вас нет прав для выполнения этой команды!")


# обработчик нажатия на кнопку
@dp.callback_query_handler(lambda c: c.data in colors, state=FSMAdmin.color)
async def process_color(callback_query: types.CallbackQuery, state: FSMContext):
    # записываем выбранный цвет в базу данных
    async with state.proxy() as data:
        data['color'] = callback_query.data

    # удаляем клавиатуру
    await bot.edit_message_reply_markup(callback_query.message.chat.id, callback_query.message.message_id,
                                        reply_markup=None)

    await FSMAdmin.next()
    await bot.send_message(callback_query.from_user.id, "Укажите текст бегущей строки")


@dp.message_handler(state=FSMAdmin.color, content_types=types.ContentTypes.ANY)
async def choise_color(message: types.Message, state: FSMContext):
    username = message.from_user.username
    currrr = userrr.cursor()
    try:
        currrr.execute("SELECT usernames FROM info WHERE usernames=?", (username,))
        result = currrr.fetchone()
    finally:
        currrr.close()
    if result:
        if message.text and message.text not in colors:
            await message.reply('Пожалуйста, выберите цвет из списка.')
            return
        if message.text:
            if len(message.text) > 20:
                await message.reply("Нельзя указать цвет, название которого длинне 20 символов.")
            else:
                async with state.proxy() as data:
                    data['color'] = message.text
                    await FSMAdmin.next()
                    await message.reply('Укажите текст')
        else:
            await message.reply('Пожалуйста, отправьте текстовое сообщение.')
    else:
        await message.answer("⛔️ У вас нет прав для выполнения этой команды!")


@dp.message_handler(state=FSMAdmin.text, content_types=types.ContentTypes.ANY)
async def choise_text(message: types.Message, state: FSMContext):
    username = message.from_user.username
    currrr = userrr.cursor()
    try:
        currrr.execute("SELECT usernames FROM info WHERE usernames=?", (username,))
        result = currrr.fetchone()
    finally:
        currrr.close()
    if result:
        if message.text:
            if len(message.text) > 2000:
                await message.reply("Текст не должен привышать длину 2000 симолов, сократите текст.")
            else:
                async with state.proxy() as data:
                    data['text'] = message.text
                await sql_add_command(state)
                await message.reply('Вы успешно добавили текст в бегущую строку.')
                await state.finish()
        else:
            await message.reply('Пожалуйста, отправьте текстовое сообщение.')
    else:
        await message.answer("⛔️ У вас нет прав для выполнения этой команды!")


@dp.callback_query_handler(lambda x: x.data and x.data.startswith('del '))
async def del_callback_run(callback_query: types.CallbackQuery):
    await sql_delete_command(callback_query.data.replace('del ', ''))
    await callback_query.answer(text=f'{callback_query.data.replace("del ", "")} удалена', show_alert=True)


@dp.message_handler(commands='list')
async def delete_item(message: types.Message):
    username = message.from_user.username
    currrr = userrr.cursor()
    try:
        currrr.execute("SELECT usernames FROM info WHERE usernames=?", (username,))
        result = currrr.fetchone()
    finally:
        currrr.close()
    if result:
        await bot.send_message(message.from_user.id, '⚠️ Список активных строк ⚠️')
        read = await sql_read2()
        for ret in read:
            await bot.send_message(message.from_user.id, f'Называние строки: {ret[0]}\nЦвет: {ret[1]}\nТекст: {ret[2]}',
                                   reply_markup=InlineKeyboardMarkup().add(
                                       InlineKeyboardButton(f'Удалить {ret[0]}', callback_data=f'del {ret[0]}')))
    else:
        await message.answer("⛔️ У вас нет прав для выполнения этой команды!")


@dp.message_handler(commands=['start', 'help'])
async def commands_start(message: types.Message):
    try:
        await bot.send_message(message.from_user.id, 'Я бот созданный для управления стендом', reply_markup=buttons)
        await message.delete()
    except:
        await message.reply('Напиши боту в ЛС для того чтобы узнать его команды:\n@Li79_stroka_bot')


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
