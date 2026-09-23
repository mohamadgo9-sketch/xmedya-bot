import os
import telebot
from telebot import types
import yt_dlp
import uuid

TOKEN = "8851143949:AAH4osueyBkhkNZYpRgHXdAjRMxoTJgfnj4"
bot = telebot.TeleBot(TOKEN)

# Uzun linkleri hafızada tutmak için geçici sözlük
link_storage = {}

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(
        message, 
        "Merhaba! Ben XMedyaDownloaderBot.\n\n"
        "Bana herhangi bir YouTube, TikTok, Instagram veya Pinterest linki gönder, hemen butonları getireyim!"
    )

@bot.message_handler(func=lambda message: True)
def ask_download_type(message):
    url = message.text
    if not url.startswith("http"):
        bot.reply_to(message, "Lütfen geçerli bir bağlantı (link) gönderin.")
        return

    # Uzun link için kısa bir benzersiz ID oluşturuyoruz
    unique_id = str(uuid.uuid4())[:8]
    link_storage[unique_id] = url

    # Butonlara sadece kısa ID'yi ekliyoruz (Hata çözüldü!)
    markup = types.InlineKeyboardMarkup()
    btn_video = types.InlineKeyboardButton("📥 Video İndir", callback_data=f"vid_{unique_id}")
    btn_audio = types.InlineKeyboardButton("🎵 MP3 İndir", callback_data=f"mp3_{unique_id}")
    
    markup.add(btn_video, btn_audio)

    bot.reply_to(message, "Bu bağlantı için ne yapmak istersiniz?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    data_parts = call.data.split('_', 1)
    action = data_parts[0]
    unique_id = data_parts[1]

    url = link_storage.get(unique_id)
    if not url:
        bot.answer_callback_query(call.id, "Bağlantı süresi dolmuş, lütfen linki tekrar gönderin.")
        return

    bot.answer_callback_query(call.id, "İşlem başlatıldı...")
    
    if action == "vid":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="📥 Video indiriliyor, lütfen bekleyin...")
        
        ydl_opts = {
            'outtmpl': 'downloaded_video.%(ext)s',
            'format': 'bestvideo+bestaudio/best',
        }
        filename = None
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)

            with open(filename, 'rb') as video:
                bot.send_video(call.message.chat.id, video)

            if os.path.exists(filename):
                os.remove(filename)
        except Exception as e:
            bot.send_message(call.message.chat.id, f"Video indirilirken hata oluştu: {str(e)}")
            if filename and os.path.exists(filename):
                os.remove(filename)

    elif action == "mp3":
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="🎵 Müzik (MP3) dönüştürülüyor, lütfen bekleyin...")
        
        ydl_opts = {
            'outtmpl': 'downloaded_audio.%(ext)s',
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        filename = None
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                filename = os.path.splitext(filename)[0] + ".mp3"

            with open(filename, 'rb') as audio:
                bot.send_audio(call.message.chat.id, audio)

            if os.path.exists(filename):
                os.remove(filename)
        except Exception as e:
            bot.send_message(call.message.chat.id, f"Müzik indirilirken hata oluştu: {str(e)}")
            if filename and os.path.exists(filename):
                os.remove(filename)

if __name__ == '__main__':
    print("Bot güncellendi ve çalışıyor...")
    bot.infinity_polling()