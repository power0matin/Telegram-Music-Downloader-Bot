# 🎵 ربات دانلود موزیک تلگرام از اسپاتیفای

<div align="center">

![Telegram](https://img.shields.io/badge/Telegram-Bot-blue?style=for-the-badge&logo=telegram)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)
![Spotify](https://img.shields.io/badge/Spotify-Downloader-green?style=for-the-badge&logo=spotify)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**ربات قدرتمند و کاربرپسند تلگرام برای دانلود موزیک از اسپاتیفای**

[🇺🇸 English](../README.md) • [📖 مستندات](#مستندات) • [🚀 شروع سریع](#شروع-سریع) • [🛠️ نصب و راه‌اندازی](#نصب-و-راه‌اندازی)

</div>

---

## ✨ ویژگی‌ها

- 🎵 **دانلود چندفرمته**: دانلود تک‌آهنگ، آلبوم کامل و پلی‌لیست
- 🔊 **انتخاب کیفیت**: انتخاب بین کیفیت 128 kbps و 320 kbps
- 🤖 **رابط کاربری تعاملی**: دکمه‌های کاربرپسند و به‌روزرسانی پیشرفت در زمان واقعی
- 🛡️ **مدیریت خطای قوی**: اعتبارسنجی جامع و پیام‌های خطای مفید
- 🗂️ **مدیریت هوشمند فایل**: پاکسازی خودکار و دانلودهای سازمان‌یافته
- ⚡ **عملکرد بالا**: منطق تکرار، محدودیت نرخ و دانلودهای بهینه‌شده
- 🔧 **استقرار آسان**: راه‌اندازی تک‌اسکریپت با مدیریت خودکار وابستگی‌ها
- 🌐 **پشتیبانی چندزبانه**: مستندات انگلیسی و فارسی

<a name="شروع-سریع"></a>
## 🚀 شروع سریع

### پیش‌نیازها

قبل از شروع، اطمینان حاصل کنید که دارید:

- **Python 3.8+** روی سیستم خود نصب شده
- **توکن ربات تلگرام** (از [@BotFather](https://t.me/BotFather) دریافت کنید)
- **Git** برای کلون کردن مخزن
- اتصال اینترنت برای دانلود وابستگی‌ها

### 1. کلون کردن مخزن

```bash
git clone https://github.com/power0matin/Telegram-Music-Downloader-Bot.git
cd Telegram-Music-Downloader-Bot
```

### 2. راه‌اندازی محیط مجازی

```bash
# ایجاد محیط مجازی
python3 -m venv venv

# فعال‌سازی
source venv/bin/activate  # Linux/Mac
# یا
venv\Scripts\activate     # Windows
```

### 3. نصب وابستگی‌ها

```bash
pip install -r requirements.txt
```

### 4. پیکربندی توکن ربات

یکی از این روش‌ها را انتخاب کنید:

**روش 1: متغیر محیطی**
```bash
export BOT_TOKEN="توکن_ربات_شما"
```

**روش 2: ایجاد فایل .env**
```bash
echo "BOT_TOKEN=توکن_ربات_شما" > .env
```

**روش 3: ایجاد فایل config.py**
```bash
cp config.example.py config.py
# سپس config.py را ویرایش کنید و توکن خود را اضافه کنید
```

### 5. راه‌اندازی ربات

**استفاده از اسکریپت راه‌اندازی (توصیه می‌شود):**
```bash
chmod +x start_bot.sh
./start_bot.sh
```

**یا به صورت دستی:**
```bash
python3 bot.py
```

## 🛠️ نصب و راه‌اندازی

### دریافت توکن ربات

1. تلگرام را باز کنید و [@BotFather](https://t.me/BotFather) را جستجو کنید
2. دستور `/newbot` را ارسال کنید و دستورالعمل‌ها را دنبال کنید
3. نام و نام کاربری برای ربات خود انتخاب کنید
4. توکن ربات را کپی کنید (فرمت: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### وابستگی‌های سیستم

ربات به صورت خودکار FFmpeg را در صورت نبودن نصب می‌کند. برای نصب دستی:

**Ubuntu/Debian:**
```bash
sudo apt update && sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
از [وبسایت FFmpeg](https://ffmpeg.org/download.html) دانلود کنید یا از مدیران بسته مثل Chocolatey استفاده کنید.

### گزینه‌های پیکربندی

برای پیکربندی پیشرفته فایل `config.py` ایجاد کنید:

```python
# ضروری
BOT_TOKEN = 'توکن_ربات_شما'

# تنظیمات اختیاری
MAX_DOWNLOAD_SIZE = 50  # مگابایت
DOWNLOAD_TIMEOUT = 300  # ثانیه
CLEANUP_INTERVAL = 3600  # ثانیه
SUPPORTED_FORMATS = ['mp3', 'flac', 'ogg']
```

## 📱 نحوه استفاده

### استفاده پایه

1. **شروع ربات**: دستور `/start` را به ربات ارسال کنید
2. **ارسال لینک اسپاتیفای**: هر URL اسپاتیفای را کپی کرده و به ربات ارسال کنید
3. **انتخاب کیفیت**: 128 kbps یا 320 kbps را انتخاب کنید
4. **دانلود**: منتظر پردازش و ارسال موزیک خود باشید

### انواع URL پشتیبانی‌شده

- **🎵 ترک‌ها**: `https://open.spotify.com/track/...`
- **💿 آلبوم‌ها**: `https://open.spotify.com/album/...`
- **📜 پلی‌لیست‌ها**: `https://open.spotify.com/playlist/...`

### نمونه گردش کار

```
کاربر: https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh
ربات: 🎵 پیدا شد: "Never Gonna Give You Up" توسط Rick Astley
     کیفیت مورد نظر خود را انتخاب کنید:
     [128 kbps] [320 kbps]

کاربر: [کلیک روی 320 kbps]
ربات: ⬇️ در حال دانلود...
     ✅ دانلود کامل شد! در حال ارسال فایل...
     [فایل صوتی ارسال شد]
```

## 🏗️ ساختار پروژه

```
Telegram-Music-Downloader-Bot/
├── 🤖 bot.py                    # نقطه ورودی اصلی ربات
├── ⚙️ config.py                 # مدیریت پیکربندی
├── 📋 requirements.txt          # وابستگی‌های پایتون
├── 🚀 start_bot.sh             # اسکریپت راه‌اندازی
├── 📁 handlers/                # کنترل‌کننده‌های پیام ربات
│   ├── __init__.py
│   ├── spotify_handler.py       # پردازش URL اسپاتیفای
│   └── callback_handler.py     # تعاملات دکمه
├── 🛠️ utils/                   # ماژول‌های کمکی
│   ├── __init__.py
│   ├── downloader.py           # عملکرد دانلود
│   ├── queue_functions.py      # مدیریت صف
│   └── variables.py            # متغیرهای سراسری
├── 📂 queue/                   # ذخیره‌سازی صف (خودکار ایجاد می‌شود)
├── ⬇️ downloads/               # دانلودهای موقت (خودکار ایجاد می‌شود)
└── 📚 فایل‌های مستندات
```

## 🔧 عیب‌یابی

### مشکلات رایج

**1. "BOT_TOKEN تنظیم نشده"**
```bash
# راه‌حل: توکن ربات خود را تنظیم کنید
export BOT_TOKEN="توکن_شما"
```

**2. "FFmpeg پیدا نشد"**
```bash
# راه‌حل: FFmpeg را نصب کنید
sudo apt install ffmpeg  # Ubuntu/Debian
brew install ffmpeg      # macOS
```

**3. خطاهای "ماژول پیدا نشد"**
```bash
# راه‌حل: محیط مجازی را فعال کرده و مجدداً نصب کنید
source venv/bin/activate
pip install -r requirements.txt
```

**4. شکست در دانلود**
- ✅ اطمینان حاصل کنید URL اسپاتیفای معتبر و عمومی است
- ✅ اتصال اینترنت خود را بررسی کنید
- ✅ برخی محتوا ممکن است محدود جغرافیایی یا در دسترس نباشد

**5. خطاهای دسترسی**
```bash
# راه‌حل: اسکریپت‌ها را قابل اجرا کنید
chmod +x start_bot.sh
```

### حالت اشکال‌زدایی

اجرا با لاگ دقیق:
```bash
python3 bot.py --debug
```

### دریافت کمک

- 📖 [دستورالعمل‌های راه‌اندازی](../SETUP_INSTRUCTIONS.md) را بررسی کنید
- 🐛 باگ‌ها را در [Issues](https://github.com/power0matin/Telegram-Music-Downloader-Bot/issues) گزارش دهید
- 💡 ویژگی‌های جدید را از طریق [Discussions](https://github.com/power0matin/Telegram-Music-Downloader-Bot/discussions) درخواست کنید

## 🔒 امنیت و حریم خصوصی

- ✅ **بدون جمع‌آوری داده**: ربات داده‌های کاربران یا تاریخچه دانلود را ذخیره نمی‌کند
- ✅ **مدیریت امن توکن**: توکن‌های ربات به صورت امن از طریق متغیرهای محیطی ذخیره می‌شوند
- ✅ **پاکسازی خودکار**: فایل‌های موقت پس از ارسال خودکار حذف می‌شوند
- ✅ **محدودیت نرخ**: حفاظت داخلی در برابر هرزنامه و سوءاستفاده

## 🚀 گزینه‌های استقرار

### توسعه محلی
```bash
./start_bot.sh
```

### استقرار تولید

**استفاده از systemd (Linux):**
```bash
# کپی فایل سرویس
sudo cp systemd/spotify-bot.service /etc/systemd/system/
sudo systemctl enable spotify-bot
sudo systemctl start spotify-bot
```

**استفاده از Docker:**
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python3", "bot.py"]
```

**استفاده از PM2:**
```bash
npm install -g pm2
pm2 start bot.py --interpreter python3 --name spotify-bot
```

## 🤝 مشارکت

از مشارکت‌ها استقبال می‌کنیم! این‌طور می‌توانید کمک کنید:

1. **🍴 Fork** کردن مخزن
2. **🌟 ایجاد** شاخه ویژگی: `git checkout -b feature/amazing-feature`
3. **💾 Commit** تغییرات: `git commit -m 'Add amazing feature'`
4. **📤 Push** به شاخه: `git push origin feature/amazing-feature`
5. **🔄 ایجاد** Pull Request

### راه‌اندازی توسعه

```bash
# کلون fork خود
git clone https://github.com/yourusername/Telegram-Music-Downloader-Bot.git
cd Telegram-Music-Downloader-Bot

# ایجاد محیط توسعه
python3 -m venv dev-env
source dev-env/bin/activate
pip install -r requirements.txt

# نصب وابستگی‌های توسعه
pip install black pylint pytest

# اجرای تست‌ها
python3 -m pytest tests/
```

## 📊 عملکرد

- ⚡ **دانلودهای سریع**: بهینه‌سازی شده برای سرعت با پردازش موازی
- 💾 **بهره‌وری حافظه**: مدیریت هوشمند حافظه برای فایل‌های بزرگ
- 🔄 **منطق تکرار**: تکرار خودکار در شکست‌های موقت
- 📈 **مقیاس‌پذیر**: طراحی شده برای مدیریت چندین کاربر همزمان

## 📋 نیازمندی‌ها

- **Python**: 3.8 یا بالاتر
- **FFmpeg**: برای پردازش صوتی (خودکار نصب می‌شود)
- **SpotDL**: 4.2.1+ (در requirements شامل است)
- **فضای ذخیره‌سازی**: حداقل 100 مگابایت فضای آزاد برای فایل‌های موقت

## 📞 پشتیبانی

- 🆘 **مسائل**: [GitHub Issues](https://github.com/power0matin/Telegram-Music-Downloader-Bot/issues)
- 💬 **بحث‌ها**: [GitHub Discussions](https://github.com/power0matin/Telegram-Music-Downloader-Bot/discussions)
- 📧 **ایمیل**: [تماس با نگهدارنده](mailto:power0matin@example.com)

## 📄 مجوز

این پروژه تحت مجوز **MIT** منتشر شده است - فایل [LICENSE](../LICENSE) را برای جزئیات ببینید.

## 🙏 تشکرات

- **SpotDL**: برای کتابخانه عالی دانلود اسپاتیفای
- **pyTelegramBotAPI**: برای فریمورک قوی ربات تلگرام
- **مشارکت‌کنندگان**: تشکر از همه کسانی که در این پروژه مشارکت کرده‌اند

---

<div align="center">

**⭐ اگر این مخزن مفید بود، ستاره بدهید!**

با ❤️ توسط جامعه متن‌باز ساخته شده

</div>
