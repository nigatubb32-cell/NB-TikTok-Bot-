import os
import telebot
import requests
import time
from threading import Thread
from flask import Flask

# ለሰርቨር መቆያ የሚሆን አነስተኛ የድረ-ገጽ መዋቅር
app = Flask('')

@app.route('/')
def home():
    return "NB Bot is running 24/7 with Channel Verification!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

BOT_TOKEN = "8657876892:AAEK2bAMhmfkZZaXgsHYf9EqZdsiXHp5gXw"
# እዚህ ጋር ያንተን አዲስ የቻናል ሊንክ አስገብተነዋል
CHANNEL_USERNAME = "@ufolink1" 

bot = telebot.TeleBot(BOT_TOKEN, threaded=True)

# ተጠቃሚው ቻናሉን Join ማድረጉን ቼክ የሚያደርግ ተግባር (Function)
def check_membership(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
        return False
    except Exception as e:
        print(f"አባልነትን ለማረጋገጥ አልተቻለም: {e}")
        # ቦቱ አድሚን ካልተደረገ በስተቀር ለጊዜው True ይመልሳል
        return True

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "👋 እንኳን ወደ NB ማውረጃ ቦት በሰላም መጡ!\n\n"
        "🎬 ከ TikTok (ያለ watermark) ቪዲዮዎችን ለማውረድ "
        "የቪዲዮውን ሊንክ ብቻ ቀጥታ ወደ እኔ ይላኩት።"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    url = message.text
    
    # 1. መጀመሪያ ቻናሉን Join ማድረጉን ያረጋግጣል
    if not check_membership(user_id):
        join_msg = (
            "⚠️ ቦቱን ለመጠቀም መጀመሪያ የኛን ቻናል መቀላቀል (Join) አለብዎት! ⚠️\n\n"
            f"እባክዎ እዚህ ይግቡ 👉 {CHANNEL_USERNAME}\n\n"
            "ቻናሉን ከተቀላቀሉ በኋላ ሊንኩን ድጋሚ ይላኩት።"
        )
        bot.reply_to(message, join_msg)
        return

    # 2. ቻናሉን Join ካደረገ ወደ ቲክቶክ ማውረጃው ያልፋል
    if "tiktok.com" in url:
        status_msg = bot.reply_to(message, "⏳ የቲክቶክ ቪዲዮህን በማዘጋጀት ላይ ነኝ... እባክህ ጥቂት ሰከንዶች ጠብቀኝ።")
        try:
            api_url = f"https://www.tikwm.com/api/?url={url}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(api_url, headers=headers, timeout=10).json()
            
            if response.get("code") == 0:
                video_url = response["data"]["play"]
                bot.delete_message(message.chat.id, status_msg.message_id)
                bot.send_video(message.chat.id, video_url, caption="✨ በ NB Bot በተሳካ ሁኔታ ተወረደ!\n\n🤖 @NBtokan_bot")
                return
        except Exception as e:
            print(f"ስህተት: {e}")

        bot.edit_message_text("❌ ይቅርታ፣ የቲክቶክ ሰርቨሮች አሁን ላይ በጣም ተጨናንቀዋል። እባክህ ሊንኩን ከጥቂት ደቂቃዎች በኋላ ድጋሚ ላከው።", message.chat.id, status_msg.message_id)
    else:
        bot.reply_to(message, "⚠️ እባክህ ትክክለኛ የቲክቶክ ቪዲዮ ሊንክ ብቻ ላክልኝ።")

def keep_alive():
    t = Thread(target=run)
    t.start()

if __name__ == "__main__":
    keep_alive()
    print("NB Bot ከቻናል ማስገደጃ ጋር በሰርቨር ላይ ዝግጁ ነው...")
    while True:
        try:
            bot.polling(none_stop=True, timeout=90, long_polling_timeout=10)
        except Exception as e:
            time.sleep(5)
