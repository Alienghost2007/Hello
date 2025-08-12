import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # تنظیمات تلگرام
    CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME")
    if not CHANNEL_USERNAME:
        raise ValueError("❌ نام کانال تلگرام تنظیم نشده")
    
    # تنظیمات یوتیوب
    YT_UPLOAD_URL = os.getenv("YT_UPLOAD_URL", "https://studio.youtube.com")
    YT_LOGIN_URL = os.getenv("YT_LOGIN_URL", "https://youtube.com")
    YT_COOKIES = os.getenv("YT_COOKIES")
    if not YT_COOKIES:
        raise ValueError("❌ کوکی‌های یوتیوب تنظیم نشده‌اند")
    
    # تنظیمات پردازش
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "processed_videos")
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", 5))
    DELAY_BETWEEN_ATTEMPTS = int(os.getenv("DELAY_BETWEEN_ATTEMPTS", 30))
    
    # تنظیمات ویدیو
    TARGET_HEIGHT = int(os.getenv("TARGET_HEIGHT", 1920))
    TARGET_FPS = int(os.getenv("TARGET_FPS", 60))
    BITRATE = os.getenv("BITRATE", "8000k")
    
    # تنظیمات محتوا
    DEFAULT_TAGS = os.getenv("DEFAULT_TAGS", "شورت,طنز,میم,سرگرمی,ایرانی").split(",")
    CONTACT_INFO = os.getenv("CONTACT_INFO", "📌 پیج اینستاگرام: @example\n🌐 وبسایت: example.com")
    
    # تنظیمات سلنیوم
    WEBDRIVER_TIMEOUT = int(os.getenv("WEBDRIVER_TIMEOUT", 60))
    PAGE_LOAD_TIMEOUT = int(os.getenv("PAGE_LOAD_TIMEOUT", 120))
