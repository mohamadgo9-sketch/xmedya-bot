import os
import telebot
from telebot import types
import yt_dlp
import uuid
from flask import Flask
from threading import Thread

TOKEN = "8851143949:AAH4osueyBkhkNZYpRgHXdAjRMxoTJgfnj4"
bot = telebot.TeleBot(TOKEN)

# Render'ın "Web Service" olarak görmesi ve 502 hatası vermemesi için mini web sunucusu
app = Flask('')

@app.route('/')
def home():
    return "Bot aktif ve çalışıyor! - TEKMD İLETİŞİM"

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

def keep_alive():
    t = Thread(target=run_web)
    t.start()

# Bot Mantığı
link_storage = {}
user_languages = {}

translations = {
    'tr': {
        'welcome': "Merhaba! Ben **TEKMD İLETİŞİM** Medya İndirme Botu.\n\nBana herhangi bir link gönder, hemen indirme seçeneklerini getireyim!\n\n📱 **Instagram:** https://www.instagram.com/tekmdiletisimavcilar\n🌍 Dil değiştirmek için: /dil",
        'invalid_link': "Lütfen geçerli bir bağlantı (link) gönderin.",
        'choose': "Bu bağlantı için ne yapmak istersiniz?",
        'btn_video': "📥 Video İndir",
        'btn_audio': "🎵 MP3 İndir",
        'start_process': "İşlem başlatıldı...",
        'dl_video': "📥 Video indiriliyor, lütfen bekleyin...",
        'dl_audio': "🎵 Müzik (MP3) dönüştürülüyor, lütfen bekleyin...",
        'err_video': "Video indirilirken hata oluştu: ",
        'err_audio': "Müzik indirilirken hata oluştu: ",
        'expired': "Bağlantı süresi dolmuş, lütfen linki tekrar gönderin.",
        'lang_select': "Lütfen bir dil seçin / Please select a language / اختر لغة:",
        'lang_changed': "Dil başarıyla Türkçe olarak ayarlandı! 🇹🇷",
        'shop_info': "🏪 **TEKMD İLETİŞİM**\n📱 Güvenilir Mobil Servis ve Aksesuarlar\n\n🔗 Instagram: instagram.com/senin_instagram_adresin"
    },
    'en': {
        'welcome': "Hello! I am **TEKMD İLETİŞİM** Media Downloader Bot.\n\nSend me any link and I'll give you the download buttons!\n\n📱 **Instagram:** instagram.com/senin_instagram_adresin\n🌍 To change language: /lang",
        'invalid_link': "Please send a valid link.",
        'choose': "What would you like to do with this link?",
        'btn_video': "📥 Download Video",
        'btn_audio': "🎵 Download MP3",
        'start_process': "Process started...",
        'dl_video': "📥 Downloading video, please wait...",
        'dl_audio': "🎵 Converting music (MP3), please wait...",
        'err_video': "Error downloading video: ",
        'err_audio': "Error downloading audio: ",
        'expired': "Connection expired, please send the link again.",
        'lang_select': "Please select a language / Lütfen dil seçin / اختر لغة:",
        'lang_changed': "Language successfully changed to English! 🇬🇧",
        'shop_info': "🏪 **TEKMD İLETİŞİM**\n📱 Reliable Mobile Service & Accessories\n\n🔗 Instagram: instagram.com/senin_instagram_adresin"
    },
    'ar': {
        'welcome': "مرحباً! أنا بوت التحميل الخاص بـ **TEKMD İLETİŞİM**.\n\nأرسل لي أي رابط وسأعطيك أزرار التحميل!\n\n📱 **إنستغرام:** instagram.com/senin_instagram_adresin\n🌍 لتغيير اللغة: /lang",
        'invalid_link': "الرجاء إرسال رابط صالح.",
        'choose': "ماذا تريد أن تفعل بهذا الرابط؟",
        'btn_video': "📥 تحميل الفيديو",
        'btn_audio': "🎵 تحميل MP3",
        'start_process': "بدء العملية...",
        'dl_video': "📥 جاري تحميل الفيديو، يرجى الانتظار...",
        'dl_audio': "🎵 جاري تحويل الموسيقى (MP3)، يرجى الانتظار...",
        'err_video': "حدث خطأ أثناء تحميل الفيديو: ",
        'err_audio': "حدث خطأ أثناء تحميل الموسيقى: ",
        'expired': "انتهت صلاحية الرابط، يرجى إرسال الرابط مرة أخرى.",
        'lang_select': "الرجاء اختيار اللغة / Please select a language / Lütfen dil seçin:",
        'lang_changed': "تم تغيير اللغة بنجاح إلى العربية! 🇸🇦",
        'shop_info': "🏪 **TEKMD İLETİŞİM**\n📱 خدمات وصيانة الهواتف المحمولة\n\n🔗 إنستغرام: instagram.com/senin_instagram_adresin"
    }
}

def get_lang(chat_id):
    return user_languages.get(chat_id, 'tr')

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    lang = get_lang(message.chat.id)
    bot.reply_to(message, translations[lang]['welcome'], parse_mode="Markdown")

@bot.message_handler(commands=['dukkan', 'iletisim', 'shop'])
def shop_info_command(message):
    lang = get_lang(message.chat.id)
    bot.reply_to(message, translations[lang]['shop_info'], parse_mode="Markdown")

@bot.message_handler(commands=['dil', 'lang'])
def change_language(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("Türkçe 🇹🇷", callback_data="lang_tr"),
        types.InlineKeyboardButton("English 🇬🇧", callback_data="lang_en"),
        types.InlineKeyboardButton("العربية 🇸🇦", callback_data="lang_ar")
    )
    lang = get_lang(message.chat.id)
    bot.reply_to(message, translations[lang]['lang_select'], reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def ask_download_type(message):
    chat_id = message.chat.id
    lang = get_lang(chat_id)
    url = message.text

    if not url.startswith("http"):
        bot.reply_to(message, translations[lang]['invalid_link'])
        return

    unique_id = str(uuid.uuid4())[:8]
    link_storage[unique_id] = url

    markup = types.InlineKeyboardMarkup()
    btn_video = types.InlineKeyboardButton(translations[lang]['btn_video'], callback_data=f"vid_{unique_id}")
    btn_audio = types.InlineKeyboardButton(translations[lang]['btn_audio'], callback_data=f"mp3_{unique_id}")
    markup.add(btn_video, btn_audio)

    bot.reply_to(message, translations[lang]['choose'], reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id = call.message.chat.id
    lang = get_lang(chat_id)

    if call.data.startswith("lang_"):
        new_lang = call.data.split("_")[1]
        user_languages[chat_id] = new_lang
        bot.answer_callback_query(call.id, "OK")
        bot.edit_message_text(
            chat_id=chat_id, 
            message_id=call.message.message_id, 
            text=translations[new_lang]['lang_changed']
        )
        return

    data_parts = call.data.split('_', 1)
    action = data_parts[0]
    unique_id = data_parts[1]

    url = link_storage.get(unique_id)
    if not url:
        bot.answer_callback_query(call.id, translations[lang]['expired'])
        return

    bot.answer_callback_query(call.id, translations[lang]['start_process'])
    
    if action == "vid":
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=translations[lang]['dl_video'])
        ydl_opts = {'outtmpl': 'downloaded_video.%(ext)s', 'format': 'bestvideo+bestaudio/best'}
        filename = None
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
            with open(filename, 'rb') as video:
                bot.send_video(chat_id, video)
            if os.path.exists(filename):
                os.remove(filename)
        except Exception as e:
            bot.send_message(chat_id, f"{translations[lang]['err_video']}{str(e)}")
            if filename and os.path.exists(filename):
                os.remove(filename)

    elif action == "mp3":
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text=translations[lang]['dl_audio'])
        ydl_opts = {
            'outtmpl': 'downloaded_audio.%(ext)s',
            'format': 'bestaudio/best',
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
        }
        filename = None
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                filename = os.path.splitext(filename)[0] + ".mp3"
            with open(filename, 'rb') as audio:
                bot.send_audio(chat_id, audio)
            if os.path.exists(filename):
                os.remove(filename)
        except Exception as e:
            bot.send_message(chat_id, f"{translations[lang]['err_audio']}{str(e)}")
            if filename and os.path.exists(filename):
                os.remove(filename)

if __name__ == '__main__':
    print("Web sunucusu ve bot başlatılıyor...")
    keep_alive()
    bot.infinity_polling()
