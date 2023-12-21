from telebot import *
import json
from info import *

bot = TeleBot(token)


def write(message, arg):
    with open("users.json", encoding="utf-8") as file:
        date = json.load(file)
        date["users"][message.chat.username][arg] = message.text
        with open('users.json', 'w', encoding='utf-8') as outfile:
            json.dump(date, outfile, ensure_ascii=False, indent=2)


def sd(message):
    with open("users.json", encoding="utf-8") as file:
        date = json.load(file)
    return message.chat.username in date["users"]


def see(message):
    with open("users.json", encoding="utf-8") as file:
        date = json.load(file)
    return message.chat.username in date["users"] and message.text.lower() in date["users"][message.chat.username]


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(chat_id=message.chat.id, text=start_text)


@bot.message_handler(commands=["help"])
def helper(message):
    bot.send_message(chat_id=message.chat.id, text=help_text)


@bot.message_handler(commands=["create"])
def creat(message):
    bot.send_message(chat_id=message.chat.id, text=create_text)
    msg = bot.reply_to(message, 'Введите имя героя')
    with open("users.json", encoding="utf-8") as file:
        date = json.load(file)
        date["users"][message.chat.username] = {}
        with open('users.json', 'w', encoding='utf-8') as outfile:
            json.dump(date, outfile, ensure_ascii=False, indent=2)
    bot.register_next_step_handler(msg, user)


def user(message):
    write(message, "name")
    msg = bot.reply_to(message, 'Введите информацию вашего героя')
    bot.register_next_step_handler(msg, inf)


def inf(message):
    write(message, "info")
    mes = bot.reply_to(message, 'Отправьте голосовое сообщение от лица вашего героя')
    bot.register_next_step_handler(mes, voice)


def voice(message):
    if message.content_type != "voice":
        mess = bot.reply_to(message, 'Отправь Голос героя')
        bot.register_next_step_handler(message, voice)
    else:
        file_info = bot.get_file(message.voice.file_id)
        print(file_info)
        downloaded_file = bot.download_file(file_info.file_path)
        save_path = f'files/{message.chat.id}.ogg'
        with open(save_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        with open("users.json", encoding="utf-8") as file:
            date = json.load(file)
            date["users"][message.chat.username]["voice"] = save_path
        with open('users.json', 'w', encoding='utf-8') as outfile:
            json.dump(date, outfile, ensure_ascii=False, indent=2)
        mes = bot.reply_to(message, 'Отправьте фото вашего героя')
        bot.register_next_step_handler(mes, photo)


def photo(message):
    if message.content_type != "photo":
        mess = bot.reply_to(message, 'Отправь Фото героя')
        bot.register_next_step_handler(message, photo)
    else:
        files = message.photo[-1]
        file_info = bot.get_file(files.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        save_path = f"files/{message.chat.id}.jpg"
        with open(save_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.reply_to(message, 'Фотография сохранена.')
        with open("users.json", encoding="utf-8") as file:
            date = json.load(file)
            date["users"][message.chat.username]["photo"] = save_path
        with open('users.json', 'w', encoding='utf-8') as outfile:
            json.dump(date, outfile, ensure_ascii=False, indent=2)
        bot.send_message(chat_id=message.chat.id, text="Создание окончено")


@bot.message_handler(commands=["talk"], func=sd)
def talk(message):
    msg = bot.reply_to(message, "Напишите кодовую фразу для начала диалога")
    bot.register_next_step_handler(msg, talk_2)


def talk_2(message):
    with open("users.json", encoding="utf-8") as file:
        date = json.load(file)
        date["users"][message.chat.username][message.text] = ""
        with open('users.json', 'w', encoding='utf-8') as outfile:
            json.dump(date, outfile, ensure_ascii=False, indent=2)
    mess = bot.reply_to(message, "Напишите кодовую фразу для поддержания диалога")
    bot.register_next_step_handler(mess, talk_3)


def talk_3(message):
    with open("users.json", encoding="utf-8") as file:
        date = json.load(file)
        for i in date["users"][message.chat.username]:
            if date["users"][message.chat.username][i] == "":
                date["users"][message.chat.username][i] = message.text
                break
        with open('users.json', 'w', encoding='utf-8') as outfile:
            json.dump(date, outfile, ensure_ascii=False, indent=2)
        bot.send_message(chat_id=message.chat.id, text="Создание окончено")


@bot.message_handler(commands=["info"], func=sd)
def information(message):
    with open("users.json", encoding="utf-8") as file:
        date = json.load(file)
        name = date["users"][message.chat.username]["name"]
        info = date["users"][message.chat.username]["info"]
        phot = date["users"][message.chat.username]["photo"]
        voic = date["users"][message.chat.username]["voice"]
    bot.send_message(chat_id=message.chat.id, text=f"Мое имя: {name}\nИнформация обо мне:\n {info}")
    bot.send_photo(chat_id=message.chat.id, photo=open(phot, 'rb'))
    bot.send_voice(chat_id=message.chat.id, voice=open(voic, "rb"))


@bot.message_handler(content_types=['text'], func=see)
def se(message):
    with open("users.json", encoding="utf-8") as file:
        date = json.load(file)
    bot.send_message(chat_id=message.chat.id, text=date["users"][message.chat.username][message.text])


@bot.message_handler(content_types=["text"])
def unknown(message):
    bot.send_message(chat_id=message.chat.id, text=unknow_text)


bot.polling()
