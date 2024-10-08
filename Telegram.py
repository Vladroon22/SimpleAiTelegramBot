import telebot
from telebot import types
import os
from AI import AI
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Замените 'YOUR_BOT_TOKEN' на токен вашего бота, который вы получили от BotFather
token = os.getenv("TOKEN")
bot = telebot.TeleBot(token=token)


user_states = {}

# Словарь для хранения состояния кнопок
button_states = {}
mistake = False

def check_email(email):
    port = 0
    if "@gmail.com" in email:
        port = 587
        return "smtp.gmail.com", port
    elif "@mail.ru" in email:
        port = 25
        return "smtp.mail.ru", port
    elif "@yandex.ru" in email:
        port = 465
        return "smtp.yandex.ru", port
    elif "@zoho.com" in email:
        port = 587
        return "smtp.zoho.com", port
    else:
        None, None

def send_email(chat_id, email, password, message):
    email_type, port = check_email(email)
    if email_type:
        getter = email
        sender = email
        password = password

        msg = MIMEMultipart()
        subject = "Сообщение из телеграмм-бота"
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = sender
        msg['To'] = getter

        msg.attach(MIMEText(message, 'plain', 'utf-8'))

        server = smtplib.SMTP(email_type, port)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(sender, password)
        server.sendmail(sender, getter, msg.as_string())
        server.quit()

        bot.send_message(chat_id, "Сообщение успешно отправлено")

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton('/start')
    item2 = types.KeyboardButton('Разработчики')
    item3 = types.KeyboardButton('Нашел Ошибку')
    item4 = types.KeyboardButton('Помощь')
    markup.add(item1, item2, item3, item4)
    button_states[message.from_user.id] = markup

    bot.send_message(message.from_user.id, "Привет, {0.first_name}! Я телеграм бот BAI, и я здесь, чтобы сделать вашу студенческую жизнь проще.".format(message.from_user), reply_markup=markup)

@bot.message_handler(content_types=['text'])
def handle_text(message):
    global mistake
    chat_id = message.chat.id
    markup = button_states.get(message.from_user.id, None)
    text = message.text
    email = os.getenv("EMAIL")
    password = os.getenv("PASS")
    if markup:
        if text == 'Нашел Ошибку':
            mistake = True
            bot.send_message(message.from_user.id, "Напишите найденную неточность одним сообщением", reply_markup=markup)
        elif text == "Помощь":
            bot.send_message(message.from_user.id, "Данный бот разрабатывался с целью упрощения получения информации об высшем учебном заведении СПБГУТ имени М.А.Бонч-Бруевиче, преподавателях и студенческом совете. Вы можете задать любой интересующий вас вопрос. В случае каких-либо ошибок или неточности полученной информации вы можете описать свою проблему и отправить разработчикам, выбрав 'Разработчики' или 'Нашел Ошибку'", reply_markup=markup)
        elif text == 'Разработчики':
            bot.send_message(chat_id, "Введите ваше пожелание/замечание одним сообщением в формате /mess ваше сообщение", reply_markup=markup)
        elif "/mess" in text:
            text = text.replace("/mess ", "")
            send_email(chat_id=chat_id,email=email,password=password,message=text)
        else:
            if mistake:
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                with open("./logs/errorList.txt", "a") as file:
                    file.write(f"\n{message.from_user.first_name} | {current_time} | {message.text}")
                bot.send_message(message.from_user.id, "Ваша информация будет обработана в ближайшее время", reply_markup=markup)
                mistake = False
            else:
                chatAI = AI()
                bot.send_message(message.from_user.id, chatAI.askAI(input=message.text), reply_markup=markup)          
    else:
        bot.send_message(message.from_user.id, "Произошла ошибка. Пожалуйста, начните заново с команды /start.")

bot.polling(none_stop=True, interval=0)
