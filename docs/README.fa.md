# ربات پیش‌نمایش لینک Spotify برای تلگرام

[![وضعیت CI](https://github.com/power0matin/Telegram-Music-Downloader-Bot/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/power0matin/Telegram-Music-Downloader-Bot/actions/workflows/ci.yml)
[![آخرین نسخه](https://img.shields.io/github/v/release/power0matin/Telegram-Music-Downloader-Bot)](https://github.com/power0matin/Telegram-Music-Downloader-Bot/releases/latest)
[![Python](https://img.shields.io/badge/Python-3.11--3.14-blue)](https://www.python.org/)
[![License](https://img.shields.io/github/license/power0matin/Telegram-Music-Downloader-Bot)](../LICENSE)

این ربات لینک آهنگ، آلبوم یا پلی‌لیست Spotify را در تلگرام تشخیص می‌دهد، در صورت دسترس بودن اطلاعات محدودی مثل عنوان و نام سازنده را نمایش می‌دهد و لینک مستقیم همان محتوا در Spotify را در اختیار کاربر می‌گذارد.

**نکته مهم:** حالت پیش‌فرض ربات فقط پیش‌نمایش لینک است. در این حالت هیچ آهنگی دانلود یا به تلگرام ارسال نمی‌شود.

**زبان دیگر:** [English README](../README.md) · **راهنمای نصب کامل‌تر:** [آموزش نصب و راه‌اندازی](SETUP_INSTRUCTIONS.md) · [یادداشت‌های انتشار](../CHANGELOG.md)

---

## ربات چه کاری انجام می‌دهد؟

- لینک آهنگ، آلبوم و پلی‌لیست Spotify را تشخیص می‌دهد.
- ساختار لینک را بررسی و پارامترهای اضافی آن را پاک می‌کند.
- از endpoint رسمی oEmbed اسپاتیفای، اطلاعات محدودی مثل عنوان و نام سازنده را دریافت می‌کند.
- لینک مستقیم برای باز کردن محتوا در Spotify نمایش می‌دهد.
- پیام‌های ربات را به فارسی و انگلیسی ارائه می‌کند.
- برای جلوگیری از ارسال بیش‌ازحد پیام، محدودیت نرخ دارد.

## در حالت پیش‌فرض چه کاری انجام نمی‌دهد؟

- آهنگ دانلود نمی‌کند.
- برای پیدا کردن نسخهٔ آهنگ به یوتیوب، ساندکلاد یا سرویس‌های دیگر مراجعه نمی‌کند.
- فایل MP3 یا فایل صوتی برای کاربر ارسال نمی‌کند.
- در صورت در دسترس نبودن oEmbed، صفحه‌های Spotify را برای استخراج اطلاعات اسکرپ نمی‌کند.

اگر Spotify اطلاعات پیش‌نمایش را برنگرداند، ربات همچنان می‌تواند لینک اصلی Spotify را نمایش دهد. دلیل غیرفعال بودن مسیر ارسال صوتی در [سند انطباق و حقوق محتوا](COMPLIANCE.md) توضیح داده شده است.

---

## راه‌اندازی سریع

برای اجرای ربات شخصی خودت، مراحل زیر را انجام بده. لازم نیست کدهای Python را تغییر بدهی.

### ۱. ساخت ربات تلگرام و دریافت توکن

1. در تلگرام به [@BotFather](https://t.me/BotFather) پیام بده.
2. دستور `/newbot` را ارسال کن.
3. طبق راهنمای BotFather یک نام و یک نام کاربری برای ربات انتخاب کن.
4. توکنی را که دریافت می‌کنی کپی کن و در اختیار دیگران قرار نده.

در مرحلهٔ پنجم این توکن را در فایل تنظیمات پروژه قرار می‌دهیم.

### ۲. نصب پیش‌نیازها

موارد زیر لازم است:

- Python نسخهٔ **۳.۱۱ تا ۳.۱۴**
- Git
- اتصال اینترنت
- حساب تلگرام

برای بررسی نسخهٔ Python:

**Linux / macOS:**

```bash
python3 --version
```

**Windows:**

```powershell
py --version
```

FFmpeg برای حالت پیش‌فرض پیش‌نمایش لازم نیست؛ فقط در مسیر اختیاری پردازش و ارسال صوتی کاربرد دارد.

### ۳. دریافت سورس پروژه

در Terminal یا PowerShell دستورهای زیر را اجرا کن:

```bash
git clone https://github.com/power0matin/Telegram-Music-Downloader-Bot.git
cd Telegram-Music-Downloader-Bot
```

### ۴. ساخت محیط مجازی و نصب کتابخانه‌ها

محیط مجازی باعث می‌شود کتابخانه‌های این پروژه از بقیهٔ برنامه‌های Python سیستم جدا باشند.

**Linux / macOS**

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

**Windows PowerShell**

ابتدا نسخه‌های نصب‌شدهٔ Python را ببین:

```powershell
py -0p
```

در مثال زیر، اگر Python نسخهٔ ۳.۱۲ را نصب نداری، شمارهٔ نسخه را با یکی از نسخه‌های نصب‌شده بین ۳.۱۱ تا ۳.۱۴ جایگزین کن:

```powershell
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

**Windows CMD**

```cmd
py -3.12 -m venv venv
venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

بعد از فعال‌سازی محیط مجازی معمولاً عبارت `(venv)` در ابتدای خط فرمان دیده می‌شود. از این به بعد دستورهای نصب و اجرای پروژه را در همین محیط اجرا کن.

### ۵. تنظیم توکن ربات

در پوشهٔ اصلی پروژه یک فایل تنظیمات به نام `.env` بساز. برای این کار فایل نمونه را کپی کن:

**Linux / macOS**

```bash
cp .env.example .env
```

**Windows PowerShell**

```powershell
Copy-Item .env.example .env
```

فایل `.env` را با Notepad، VS Code یا هر ویرایشگر متنی باز کن و مقدارهای اصلی را تنظیم کن:

```dotenv
BOT_TOKEN=توکن_واقعی_دریافت_شده_از_BotFather
DEFAULT_LANGUAGE=fa
ENABLE_AUTHORIZED_AUDIO_DELIVERY=false
```

- مقدار `BOT_TOKEN` را با توکن واقعی خودت جایگزین کن.
- برای زبان فارسی مقدار `fa` و برای انگلیسی مقدار `en` را قرار بده.
- مقدار `ENABLE_AUTHORIZED_AUDIO_DELIVERY` را روی `false` نگه دار.

فایل `.env` شامل اطلاعات محرمانه است و نباید آن را برای کسی بفرستی یا در GitHub منتشر کنی. این فایل در `.gitignore` قرار دارد و به‌صورت عادی وارد commit نمی‌شود.

### ۶. اجرای ربات

در حالی که محیط مجازی فعال است، دستور زیر را اجرا کن:

```bash
python bot.py
```

اگر توکن معتبر باشد، ربات به تلگرام متصل می‌شود. پنجرهٔ ترمینال را تا زمانی که می‌خواهی ربات فعال باشد باز نگه دار. برای متوقف کردن آن `Ctrl+C` را بزن.

در Linux و macOS می‌توانی از اسکریپت کمکی هم استفاده کنی:

```bash
chmod +x start_bot.sh
./start_bot.sh
```

این اسکریپت انتظار دارد محیط مجازی در پوشه‌ای به نام `venv` ساخته شده باشد. در ویندوز از دستور `python bot.py` استفاده کن.

### ۷. آزمایش ربات در تلگرام

1. صفحهٔ رباتی را که با BotFather ساخته‌ای باز کن.
2. دستور `/start` را بفرست.
3. با دستور `/help` راهنمای داخل ربات را ببین.
4. یک لینک عمومی آهنگ، آلبوم یا پلی‌لیست Spotify ارسال کن.

نمونهٔ لینک:

```
https://open.spotify.com/track/4iV5W9uYEdYUVa79Axb7Rh
```

ربات اطلاعاتی را که Spotify در اختیار می‌گذارد و لینک باز کردن محتوا در Spotify نمایش می‌دهد. برای گوش دادن، همان لینک را باز کن.

---

## تنظیمات پروژه

برای دیدن تمام تنظیمات به فایل [نمونه تنظیمات `.env.example`](../.env.example) مراجعه کن. تنظیمات اصلی:

| متغیر | کاربرد | مقدار پیش‌فرض |
|---|---|---|
| `BOT_TOKEN` | توکن ربات؛ الزامی است | باید وارد شود |
| `DEFAULT_LANGUAGE` | زبان پیام‌های ربات: `fa` یا `en` | در فایل نمونه `fa` |
| `ENABLE_AUTHORIZED_AUDIO_DELIVERY` | فعال یا غیرفعال بودن مسیر اختیاری ارسال صوتی | `false` |
| `RATE_LIMIT_REQUESTS` | تعداد پیام مجاز در بازهٔ محدودیت نرخ | `20` |
| `RATE_LIMIT_WINDOW_SECONDS` | مدت بازهٔ محدودیت نرخ، بر حسب ثانیه | `60` |
| `LOG_LEVEL` | سطح جزئیات گزارش‌ها | `INFO` |

برنامه فایل `.env` را هنگام شروع می‌خواند. بعد از تغییر تنظیمات، ربات را متوقف و دوباره اجرا کن.

### دربارهٔ ارسال فایل صوتی

قابلیت قدیمی ارسال فایل صوتی به‌صورت پیش‌فرض غیرفعال است. صرفاً برای دانلود آهنگ از لینک Spotify این گزینه را فعال نکن. استفاده از آن نیازمند مجوزهای کتبی پلتفرم‌ها و مجوز صاحبان حقوق محتوا برای همان کاربرد مشخص است. تغییر مقدار این متغیر به `true` به‌تنهایی مجوز ایجاد نمی‌کند. قبل از هر تغییری [سند انطباق پروژه](COMPLIANCE.md) را بخوان.

---

## نصب روی سرور Ubuntu

اگر می‌خواهی ربات پس از بستن SSH هم به کار خود ادامه دهد، از نصب‌کنندهٔ systemd پروژه استفاده کن:

- سیستم‌عامل پیشنهادی: Ubuntu 24.04.
- در Ubuntu 22.04 باید Python نسخهٔ ۳.۱۱ تا ۳.۱۴ را جداگانه نصب و با `PYTHON_BIN` معرفی کنی.
- نصب‌کننده یک کاربر مستقل به نام `spotifybot` و سرویس `spotify-bot` می‌سازد.
- در نصب اول توکن را از تو می‌پرسد و هنگام به‌روزرسانی، فایل تنظیمات موجود را حفظ می‌کند.

قبل از اجرا، [راهنمای نصب و راه‌اندازی](SETUP_INSTRUCTIONS.md) را بخوان. نصب‌کننده علاوه بر نصب وابستگی‌ها، بسته‌های Ubuntu را نیز به‌روزرسانی می‌کند؛ بنابراین آن را روی سروری اجرا کن که برای دریافت این به‌روزرسانی‌ها آماده باشد.

در حال حاضر Dockerfile یا Docker Compose رسمی برای این پروژه ارائه نشده است.

---

## رفع مشکلات رایج

### خطای `BOT_TOKEN is required` یا نامعتبر بودن توکن

- مطمئن شو فایل `.env` در کنار فایل `bot.py` قرار دارد.
- نام متغیر دقیقاً `BOT_TOKEN` باشد.
- کل توکن را از BotFather کپی کن و فاصلهٔ اضافی نداشته باشد.
- اگر توکن را جایی منتشر کرده‌ای، آن را از طریق BotFather باطل کن و توکن جدید بگیر.

### خطای `No module named 'telebot'` یا پیدا نشدن کتابخانه

ابتدا محیط مجازی را فعال کن و سپس وابستگی‌ها را نصب کن:

```bash
python -m pip install -r requirements.txt
```

### نسخهٔ Python پشتیبانی نمی‌شود

نسخه باید بین ۳.۱۱ تا ۳.۱۴ باشد. نسخهٔ فعال را بررسی کن:

```bash
python --version
```

اگر محیط مجازی را با نسخهٔ اشتباه ساخته‌ای، آن پوشه را حذف کن و با نسخهٔ درست دوباره بساز.

### عنوان آهنگ یا نام سازنده نمایش داده نمی‌شود

دریافت اطلاعات از oEmbed به‌صورت best-effort انجام می‌شود؛ ممکن است Spotify برای بعضی لینک‌ها اطلاعات پیش‌نمایش برنگرداند. در این حالت لینک اصلی Spotify همچنان قابل نمایش است و ربات از scraping صفحهٔ HTML استفاده نمی‌کند.

### پیام محدودیت تعداد درخواست دریافت می‌کنم

محدودیت داخلی ربات فعال شده است. طبق زمانی که در پاسخ ربات نمایش داده می‌شود صبر کن و سپس لینک بعدی را بفرست.

### چند نمونه از ربات هم‌زمان اجرا شده‌اند

برای هر توکن فقط یک فرایند polling باید فعال باشد. اگر خطای تداخل دریافت پیام از تلگرام دیدی، نمونه‌های تکراری ربات را متوقف کن.

---

## ساختار پروژه

```text
.
├── bot.py
├── config.py
├── requirements.txt
├── requirements-dev.txt
├── .env.example
├── start_bot.sh
├── setup_vps.sh
├── handlers/
├── utils/
├── scripts/
├── systemd/
├── tests/
└── docs/
    ├── README.fa.md
    ├── SETUP_INSTRUCTIONS.md
    └── COMPLIANCE.md
```

## مشارکت در توسعه

برای نصب ابزار تست و اجرای تست‌ها:

```bash
python -m pip install -r requirements-dev.txt
pytest -q
```

CI پروژه علاوه بر تست‌ها، کامپایل فایل‌های Python و اعتبارسنجی اسکریپت‌های shell را روی نسخه‌های Python ۳.۱۱ تا ۳.۱۴ انجام می‌دهد.

## پشتیبانی و مجوز

- گزارش باگ: [GitHub Issues](https://github.com/power0matin/Telegram-Music-Downloader-Bot/issues)
- مجوز: [MIT](../LICENSE)
- صفحهٔ پروژه: [matinshahabadi.ir](https://matinshahabadi.ir/projects/telegram-music-downloader-bot/)

**نگه‌دارندهٔ پروژه:** [Matin Shahabadi](https://github.com/power0matin)
