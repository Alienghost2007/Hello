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
            WebDriverWait(driver, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
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
            WebDriverWait(driver, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            print("[DEBUG] Cookies loaded successfully")
            return True
        except Exception as e:
            print(f"❌ خطا در بارگذاری کوکی‌ها: {str(e)}")
            return False

    @staticmethod
    def check_login(driver):
        """بررسی وضعیت ورود با روش‌های بهبود یافته"""
        try:
            driver.get("https://studio.youtube.com")
            WebDriverWait(driver, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            # بررسی وجود آواتار کاربر یا عناصر مربوط به حساب
            elements = driver.find_elements(By.CSS_SELECTOR, "img#img")
            print(f"[DEBUG] Avatar elements found: {len(elements)}")
            if len(elements) > 0:
                print("[INFO] Login verified successfully")
                return True
            
            # روش جایگزین: بررسی وجود منوی حساب
            account_menu = driver.find_elements(By.XPATH, "//a[contains(@href, 'account')]")
            print(f"[DEBUG] Account menu elements found: {len(account_menu)}")
            return len(account_menu) > 0
        except Exception as e:
            print(f"❌ خطا در بررسی وضعیت ورود: {str(e)}")
            return False

    @staticmethod
    def upload_shorts(video_path, title, description):
        """آپلود ویدیو به یوتیوب شورت با روش بهبود یافته"""
        for attempt in range(1, Config.MAX_RETRIES + 1):
            print(f"\n🔄 تلاش آپلود {attempt} از {Config.MAX_RETRIES}")
            driver = None
            
            try:
                # تنظیمات پیشرفته کروم
                options = Options()
                options.add_argument("--headless=chrome")  # استفاده از headless mode پایدار
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--window-size=1920,1080")
                options.add_argument("--start-maximized")
                options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
                options.add_argument("--disable-extensions")
                options.add_argument("--disable-gpu")
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
                WebDriverWait(driver, 120).until(
                    lambda d: d.execute_script("return document.readyState") == "complete"
                )
                
                # 3. آپلود فایل
                print("📤 در حال آپلود ویدیو...")
                file_input = WebDriverWait(driver, 90).until(
                    EC.visibility_of_element_located((By.CSS_SELECTOR, 'input[type="file"][accept*="video/*"]'))
                )
                if not file_input.is_enabled():
                    raise Exception("File input is not enabled")
                file_input.send_keys(os.path.abspath(video_path))
                time.sleep(20)  # زمان برای تکمیل آپلود
                
                # 4. تنظیم عنوان
                print("✏️ در حال تنظیم عنوان...")
                try:
                    title_field = WebDriverWait(driver, 30).until(
                        EC.element_to_be_clickable((By.XPATH, '//div[@id="title-textarea"]//textarea'))
                    )
                    title_field.clear()
                    title_field.send_keys(title)
                except:
                    print("⚠️ تلاش برای یافتن عنوان با روش جایگزین...")
                    title_field = WebDriverWait(driver, 30).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[name="title"], [aria-label="Title"]'))
                    )
                    title_field.clear()
                    title_field.send_keys(title)
                
                # 5. تنظیم توضیحات
                print("📝 در حال تنظیم توضیحات...")
                desc_field = WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[@id="description-textarea"]//textarea'))
                )
                desc_field.clear()
                desc_field.send_keys(description)
                time.sleep(3)
                
                # 6. کلیک روی دکمه‌های بعدی
                for step in range(3):
                    print(f"[DEBUG] Clicking next button, step {step + 1}")
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
                print(traceback.format_exc())
                os.makedirs("screenshots", exist_ok=True)
                if driver:
                    driver.save_screenshot(f"screenshots/upload_error_{attempt}_{int(time.time())}.png")
                    with open(f"screenshots/error_page_{attempt}_{int(time.time())}.html", "w", encoding="utf-8") as f:
                        f.write(driver.page_source)
                time.sleep(Config.DELAY_BETWEEN_ATTEMPTS)
                
            finally:
                if driver:
                    try:
                        driver.quit()
                    except:
                        print("[WARNING] Failed to quit WebDriver")
        
        print("❌ تمام تلاش‌های آپلود ناموفق بودند")
        return False
