from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import os
import traceback
from config import Config

class YouTubeUploader:
    @staticmethod
    def load_cookies(driver):
        """بارگذاری کوکی‌های یوتیوب با روش بهبود یافته"""
        try:
            cookies = json.loads(Config.YT_COOKIES)
            driver.get("https://youtube.com")
            time.sleep(3)
            
            # حذف تمام کوکی‌های موجود
            driver.delete_all_cookies()
            time.sleep(2)
            
            # اضافه کردن کوکی‌های جدید با کنترل خطا
            for cookie in cookies:
                try:
                    if 'expiry' in cookie:
                        cookie.pop('expiry')
                    driver.add_cookie(cookie)
                except Exception as e:
                    print(f"⚠️ خطا در اضافه کردن کوکی: {str(e)}")
                    continue
            
            driver.refresh()
            time.sleep(5)
            return True
        except Exception as e:
            print(f"❌ خطا در بارگذاری کوکی‌ها: {str(e)}")
            return False

    @staticmethod
    def check_login(driver):
        """بررسی وضعیت ورود با روش‌های مختلف"""
        try:
            driver.get("https://youtube.com")
            time.sleep(5)
            
            # چندین روش برای بررسی لاگین
            logged_in = any([
                driver.find_elements(By.CSS_SELECTOR, "img#img"),  # آواتار کاربر
                driver.find_elements(By.XPATH, "//a[contains(@href, 'account')]"),
                driver.find_elements(By.CSS_SELECTOR, "yt-img-shadow.ytd-topbar-menu-button-renderer")
            ])
            
            return logged_in
        except:
            return False

    @staticmethod
    def upload_shorts(video_path, title, description):
        """آپلود ویدیو به یوتیوب شورت با روش جدید"""
        for attempt in range(1, Config.MAX_RETRIES + 1):
            print(f"\n🔄 تلاش آپلود {attempt} از {Config.MAX_RETRIES}")
            driver = None
            
            try:
                # تنظیمات پیشرفته کروم
                options = Options()
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--window-size=1920,1080")
                options.add_argument("--headless=new")
                options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option("useAutomationExtension", False)
                
                # راه‌اندازی درایور
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=options)
                driver.implicitly_wait(30)
                
                # 1. احراز هویت
                if not (YouTubeUploader.load_cookies(driver) and YouTubeUploader.check_login(driver)):
                    raise Exception("❌ احراز هویت ناموفق بود")
                
                # 2. رفتن به صفحه آپلود
                print("🔵 در حال بارگذاری صفحه آپلود...")
                driver.get(Config.YT_UPLOAD_URL)
                time.sleep(15)  # افزایش زمان انتظار
                
                # 3. آپلود فایل
                print("📤 در حال آپلود ویدیو...")
                file_input = WebDriverWait(driver, 60).until(
                    EC.presence_of_element_located((By.XPATH, '//input[@type="file"]'))
                )
                file_input.send_keys(os.path.abspath(video_path))
                time.sleep(20)  # افزایش زمان برای آپلود
                
                # 4. تنظیم عنوان (با 3 روش مختلف)
                print("✏️ در حال تنظیم عنوان...")
                try:
                    title_field = WebDriverWait(driver, 30).until(
                        EC.element_to_be_clickable((By.XPATH, '//div[@id="title-textarea"]//textarea'))
                    )
                    title_field.clear()
                    title_field.send_keys(title)
                except:
                    try:
                        title_field = driver.find_element(By.NAME, "title")
                        title_field.send_keys(title)
                    except:
                        title_field = driver.find_element(By.CSS_SELECTOR, "[aria-label='Title']")
                        title_field.send_keys(title)
                
                # 5. تنظیم توضیحات
                print("📝 در حال تنظیم توضیحات...")
                desc_field = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@id="description-textarea"]//textarea'))
                )
                desc_field.send_keys(description)
                time.sleep(3)
                
                # 6. کلیک روی دکمه‌های بعدی
                for _ in range(3):
                    next_btn = WebDriverWait(driver, 30).until(
                        EC.element_to_be_clickable((By.XPATH, '//ytcp-button[@id="next-button"]'))
                    )
                    next_btn.click()
                    time.sleep(5)
                
                # 7. انتشار نهایی
                print("🚀 در حال انتشار ویدیو...")
                publish_btn = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, '//ytcp-button[@id="done-button"]'))
                )
                publish_btn.click()
                time.sleep(15)
                
                print("✅ ویدیو با موفقیت آپلود شد!")
                return True
                
            except Exception as e:
                print(f"❌ خطا در تلاش {attempt}: {str(e)}")
                if driver:
                    driver.save_screenshot(f"upload_error_{attempt}.png")
                time.sleep(Config.DELAY_BETWEEN_ATTEMPTS)
                
            finally:
                if driver:
                    driver.quit()
        
        print("❌ تمام تلاش‌های آپلود ناموفق بودند")
        return False
