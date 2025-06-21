# =================================================================
# === کد کامل و نهایی بات تلگرام با هوش مصنوعی جمنای برای Render ===
# =================================================================

import os
import logging
import google.generativeai as genai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# تنظیمات اولیه برای نمایش لاگ‌ها
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# خواندن کلیدهای محرمانه از تنظیمات Render
try:
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
    # بررسی اینکه آیا کلیدها وجود دارند یا نه
    if not TELEGRAM_BOT_TOKEN or not GEMINI_API_KEY:
        logger.error("خطای مهم: یک یا هر دو کلید محرمانه (TELEGRAM_BOT_TOKEN, GEMINI_API_KEY) تعریف نشده‌اند!")
        exit()
except Exception as e:
    logger.error(f"خطا در خواندن کلیدهای محرمانه: {e}")
    exit()

# تنظیمات هوش مصنوعی جمنای
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-pro')
    logger.info("ارتباط با هوش مصنوعی Gemini موفقیت آمیز بود.")
except Exception as e:
    logger.error(f"خطا در تنظیم مدل Gemini: {e}")
    exit()

# این تابع برای دستور /start است
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_name = update.message.from_user.first_name
    await update.message.reply_text(
        f"سلام {user_name} عزیز!\n"
        "من یک بات هستم که به هوش مصنوعی قدرتمند Gemini متصلم. "
        "مرا در یک گروه اضافه کن و با منشن کردن نام کاربری‌ام سوالت را بپرس."
    )

# این تابع برای زمانی است که بات را در گروه منشن می‌کنند
async def handle_mention(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    bot_username = (await context.bot.get_me()).username

    # بررسی اینکه پیام، منشن بات ما هست یا نه
    if message.text and filters.Entity("mention").filter(message):
        question = ""
        # پیدا کردن متن بعد از اولین منشن بات
        for entity in message.entities:
            if entity.type == "mention":
                mention_text = message.text[entity.offset : entity.offset + entity.length]
                if mention_text == f"@{bot_username}":
                    question = message.text[entity.offset + entity.length:].strip()
                    break # فقط اولین منشن بات را پردازش می‌کند

        # اگر سوالی بعد از منشن نبود
        if not question:
            await message.reply_text("جانم؟ در خدمتم! لطفاً بعد از منشن کردن من، سوالت رو هم بپرس.")
            return

        # ارسال سوال به جمنای و دریافت پاسخ
        try:
            processing_message = await message.reply_text("🧠 دریافت شد! در حال تجزیه و تحلیل...")
            response = model.generate_content(question)
            await context.bot.edit_message_text(
                chat_id=processing_message.chat_id,
                message_id=processing_message.message_id,
                text=response.text
            )
        except Exception as e:
            logger.error(f"خطا در پردازش Gemini: {e}")
            await message.reply_text("😔 وای! در ارتباط با سرورهای هوش مصنوعی مشکلی پیش آمد.")

# تابع اصلی برای اجرای بات
def main() -> None:
    logger.info("در حال ساخت اپلیکیشن بات...")
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    logger.info("در حال تعریف کردن دستورها...")
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Entity("mention") & filters.GROUP, handle_mention))
    
    logger.info("بات با موفقیت راه‌اندازی شد و آماده به کار است...")
    application.run_polling()

if __name__ == '__main__':
    main()
