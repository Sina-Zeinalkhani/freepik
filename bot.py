#!/usr/bin/env python3
"""
Simple Telegram Bot with pyTelegramBotAPI
Stable Version for Render
"""

import os
import time
import random
import requests
from urllib.parse import quote_plus
import telebot

# تنظیمات
BOT_TOKEN = "8458966976:AAGvp6xc5t3z62RAmNgHpBOxeQmVye0MUME"

# ایجاد ربات
bot = telebot.TeleBot(BOT_TOKEN)

class ImageProvider:
    def __init__(self):
        self.session = requests.Session()
        self.setup_session()
    
    def setup_session(self):
        """تنظیم session"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.session.headers.update(headers)
    
    def get_image_urls(self, query, num_images):
        """دریافت لینک عکس‌ها از Unsplash"""
        try:
            image_urls = []
            
            # استفاده از Unsplash برای عکس‌های رایگان
            for i in range(num_images):
                unique_id = random.randint(1000, 9999)
                url = f"https://source.unsplash.com/800x600/?{quote_plus(query)}&{unique_id}"
                image_urls.append(url)
            
            return image_urls
            
        except Exception as e:
            print(f"خطا در دریافت عکس: {e}")
            return self.get_fallback_images(num_images)
    
    def get_fallback_images(self, num_images):
        """عکس‌های جایگزین"""
        fallback_urls = [
            "https://images.unsplash.com/photo-1501854140801-50d01698950b",  # طبیعت
            "https://images.unsplash.com/photo-1441974231531-c6227db76b6e",  # جنگل
            "https://images.unsplash.com/photo-1465146344425-f00d5f5c8f07",  # کوه
            "https://images.unsplash.com/photo-1506905925346-21bda4d32df4",  # دریا
        ]
        return fallback_urls[:num_images]

# ایجاد نمونه
image_provider = ImageProvider()

# دیکشنری برای ذخیره وضعیت کاربران
user_states = {}

# دستور /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = """
🤖 **ربات ارائه عکس**

🔍 **نحوه استفاده:**
عبارت جستجو رو بفرستید تا عکس‌های مرتبط رو دریافت کنید

📝 **مثال:**
• طبیعت
• شهر  
• حیوانات
• غذا

حالا عبارت مورد نظر رو بفرستید...
    """
    bot.reply_to(message, welcome_text)
    user_states[message.chat.id] = {'step': 'query'}

# دستور /help
@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = """
📖 **راهنمای ربات**

**دستورات:**
/start - شروع ربات
/help - نمایش این راهنما

**نحوه استفاده:**
1. عبارت جستجو رو بفرست
2. تعداد عکس رو مشخص کن
3. عکس‌ها رو دریافت کن
    """
    bot.reply_to(message, help_text)

# پردازش تمام پیام‌های متنی
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    user_message = message.text
    
    # اگر کاربر وضعیت ندارد، شروع کن
    if chat_id not in user_states:
        user_states[chat_id] = {'step': 'query'}
    
    user_data = user_states[chat_id]
    
    if user_data['step'] == 'query':
        # مرحله اول: دریافت عبارت جستجو
        user_data['query'] = user_message
        user_data['step'] = 'num_images'
        bot.reply_to(message, f"🔍 عبارت: {user_message}\n\n📊 تعداد عکس مورد نظر رو وارد کن (1-5):")
    
    elif user_data['step'] == 'num_images':
        # مرحله دوم: دریافت تعداد عکس
        try:
            num_images = int(user_message)
            if not 1 <= num_images <= 5:
                bot.reply_to(message, "⚠️ لطفاً عدد بین 1-5 وارد کن:")
                return
            
            query = user_data['query']
            bot.reply_to(message, f"⏳ در حال دریافت {num_images} عکس برای '{query}'...")
            
            # دریافت لینک عکس‌ها
            image_urls = image_provider.get_image_urls(query, num_images)
            
            if image_urls:
                # ارسال عکس‌ها
                for i, url in enumerate(image_urls, 1):
                    try:
                        bot.send_photo(chat_id, url, caption=f"📸 عکس {i} - {query}")
                        time.sleep(1)  # تاخیر بین ارسال
                    except Exception as e:
                        print(f"خطا در ارسال عکس: {e}")
                        continue
                
                bot.send_message(chat_id, "🎉 عملیات کامل شد! برای جستجوی جدید، عبارت جدید رو بفرست.")
            else:
                bot.send_message(chat_id, "❌ خطا در دریافت عکس‌ها. لطفاً دوباره تلاش کنید.")
            
            # ریست وضعیت کاربر
            user_states[chat_id] = {'step': 'query'}
            
        except ValueError:
            bot.reply_to(message, "⚠️ لطفاً یک عدد معتبر وارد کن:")

# اجرای ربات
if __name__ == "__main__":
    print("🤖 ربات در حال راه‌اندازی...")
    print("✅ ربات آماده است!")
    bot.infinity_polling()
