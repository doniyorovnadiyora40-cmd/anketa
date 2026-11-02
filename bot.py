import telebot
from telebot import types, custom_filters
from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage
from config import TOKEN
import db

bot = telebot.TeleBot(TOKEN, state_storage=StateMemoryStorage())

TILLAR = {
    "uz": "uz O'zbek",
    "ru": "ru Русский",
    "en": "en English"
}
class Royxat(StatesGroup):
    ism = State()
    yosh = State()
    til = State()
def menyu():
    key = types.ReplyKeyboardMarkup(resize_keyboard=True)
    key.row("Ro'yxat", "Men")
    key.row("Statistika", "Yordam")
    return key
def til_tugma():
    key = types.InlineKeyboardMarkup(row_width=3)
    for i, v in TILLAR.items():
        key.add(types.InlineKeyboardButton(
            v, callback_data=f"til_{i}"
        ))
    return key
@bot.message_handler(commands=['start'])
def start(message):
    user = db.user_ol(message.chat.id)
    if user:
        bot.send_message(
            message.chat.id,
            f"Salom, {user['ism']}! Siz ro'yxatdasiz",
            reply_markup=menyu()
        )
    else:
        bot.send_message(
            message.chat.id,
            "Salom! Ro'yxatdan o'tish uchun ro'yxat tugmasini bosing.",
            reply_markup=menyu()
        )
@bot.message_handler(commands=['cancel'])
def cancel(message):
    bot.delete_state(message.from_user.id, message.chat.id)
    bot.send_message(
        message.chat.id,
        "Ro'yxatdan o'tish bekor qilindi.",
        reply_markup=menyu()
    )
@bot.message_handler(commands=['royxat'])
@bot.message_handler(func=lambda message: message.text == "Ro'yxat")
def royxat(message):
    bot.set_state(message.from_user.id, Royxat.ism, message.chat.id)
    bot.send_message(
        message.chat.id,
        "Ismingizni kiriting: ",
        reply_markup=types.ReplyKeyboardRemove()
    )
@bot.message_handler(state=Royxat.ism)
def ism_qabul(message):
    if not message.text or not message.text.strip():
        bot.send_message(message.chat.id, "Ismingizni kiriting: ")
        return
    with bot.retrieve_data(message.from_user.id, message.chat.id) as f:
        f["ism"] = message.text.strip()
    bot.set_state(message.from_user.id, Royxat.yosh, message.chat.id)
    bot.send_message(message.chat.id, "Yoshingizni kiriting: ")
@bot.message_handler(state=Royxat.yosh)
def yosh_qabul(message):
    if not message.text or not message.text.isdigit():
        bot.send_message(message.chat.id, "Yoshingizni raqamda kiriting: ")
        return
    yosh = int(message.text)
    if yosh < 1 or yosh > 120:
        bot.send_message(message.chat.id, "Yosh 1 dan 100 gacha bo'lishi kerak.")
        return
    with bot.retrieve_data(message.from_user.id, message.chat.id) as f:
        f["yosh"] = yosh
    bot.set_state(message.from_user.id, Royxat.til, message.chat.id)
    bot.send_message(
        message.chat.id,
        "Tilni tanlang: ",
        reply_markup=til_tugma()
    )
@bot.callback_query_handler(
    func=lambda call: call.data.startswith("til_"),
    state=Royxat.til
)
def til_tanlandi(call):
    til = call.data.split("_")[1]
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as f:
        ism = f["ism"]
        yosh = f["yosh"]
    db.user_saqla(call.message.chat.id, ism, yosh, til)
    bot.delete_state(call.from_user.id, call.message.chat.id)
    bot.answer_callback_query(call.id, "Saqlandi!")
    bot.edit_message_text(
        f"Tanlangan til: {TILLAR[til]}",
        call.message.chat.id,
        call.message.message_id
    )
    bot.send_message(
        call.message.chat.id,
        f"{ism}, {yosh} yosh. Ro'yxatdan o'tdingiz!",
        reply_markup=menyu()
    )
@bot.message_handler(state=Royxat.til)
def til_matn(message):
    bot.send_message(
        message.chat.id,
        "Iltimos, tilni tugmalardan tanlang."
    )
@bot.message_handler(commands=['men'])
@bot.message_handler(func=lambda message: message.text == "Men")
def men(message):
    user = db.user_ol(message.chat.id)
    if user is None:
        bot.send_message(message.chat.id, "Siz hali ro'yxatdan o'tmagansiz.")
        return
    bot.send_message(
        message.chat.id,
        f"Ism: {user['ism']}\n"
        f"Yosh: {user['yosh']}\n"
        f"Til: {TILLAR[user['til']]}"
    )
@bot.message_handler(commands=['stat'])
@bot.message_handler(func=lambda message: message.text == "Statistika")
def stat(message):
    natija = db.til_boyicha()
    matn = f"Jami foydalanuvchilar: {db.jami()} ta\n\n"
    for i, v in natija.items():
        matn += f"{TILLAR.get(i, i)}: {v} ta\n"
    bot.send_message(message.chat.id, matn)
@bot.message_handler(commands=['help'])
@bot.message_handler(func=lambda message: message.text == "Yordam")
def yordam(message):
    bot.send_message(
        message.chat.id,
        "/start - Botni boshlash\n"
        "/royxat - Ro'yxatdan o'tish\n"
        "/men - Ma'lumotlarim\n"
        "/stat - Statistika\n"
        "/cancel - Bekor qilish"
    )
@bot.callback_query_handler(func=lambda call: True)
def eski_tugma(call):
    bot.answer_callback_query(
        call.id,
        "Bu tugma eskirgan. Qaytadan ro'yxatdan o'ting."
    )
@bot.message_handler(func=lambda message: True)
def boshqa(message):
    bot.send_message(message.chat.id, "Tushunmadim. /help")
bot.add_custom_filter(custom_filters.StateFilter(bot))
print("Anketa bot ishga tushdi...")
bot.infinity_polling()
