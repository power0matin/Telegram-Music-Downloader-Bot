# Telegram Music Downloader Bot
For Enlglish : **README.en.md**

این پروژه شامل یک ربات تلگرام است که به کاربران این امکان را می‌دهد تا آهنگ‌ها، آلبوم‌ها و پلی‌لیست‌ها را از اسپاتیفای دانلود کنند. کاربران می‌توانند با ارسال لینک اسپاتیفای به ربات، آهنگ‌های خود را با کیفیت‌های مختلف (128 kbps و 320 kbps) دریافت کنند.

## ویژگی‌ها

- **دانلود آهنگ‌ها، آلبوم‌ها و پلی‌لیست‌ها**: از اسپاتیفای با کیفیت‌های مختلف.
- **انتخاب کیفیت دانلود**: 128 kbps یا 320 kbps.
- **ارسال فایل‌های دانلود شده**: به کاربران از طریق تلگرام.

## پیش‌نیازها

برای اجرای این ربات، نیاز به نصب ابزارهای زیر است:

- **Python 3.7+**: نسخه‌ای از Python برای اجرای کد.
- **SpotDL**: برای دانلود آهنگ‌ها از اسپاتیفای.
- **python-telegram-bot**: برای تعامل با API تلگرام.

## نصب

### 1. کلون کردن مخزن

برای شروع، مخزن را از GitHub کلون کنید:

```bash
git clone https://github.com/yourusername/telegram-music-downloader-bot.git
cd telegram-music-downloader-bot
```


### 2. نصب وابستگی‌ها

پیش‌نیازها را با استفاده از `pip` نصب کنید:

```bash
pip install -r requirements.txt
```

### 3. پیکربندی

#### الف) تنظیم توکن بات تلگرام

در فایل `config.py`، توکن بات تلگرام خود را اضافه کنید:

```python
BOT_TOKEN = 'YOUR_BOT_TOKEN'
```

#### ب) تنظیمات SpotDL

اطمینان حاصل کنید که SpotDL به درستی نصب شده است و به پیکربندی‌های پیش‌فرض نیاز ندارد.

## استفاده

### 1. اجرای ربات

برای اجرای ربات، از دستور زیر استفاده کنید:

```bash
python main.py
```

### 2. استفاده از ربات

- **شروع کار**: با ارسال `/start` به ربات، راهنمایی اولیه را دریافت خواهید کرد.
- **ارسال لینک**: لینک اسپاتیفای آهنگ، آلبوم یا پلی‌لیست مورد نظر خود را ارسال کنید.
- **انتخاب کیفیت**: پس از ارسال لینک، دکمه‌های انتخاب کیفیت (128 kbps یا 320 kbps) برای شما ارسال خواهد شد.
- **دریافت فایل**: پس از انتخاب کیفیت، فایل MP3 با کیفیت انتخاب شده به شما ارسال خواهد شد.

## توسعه

اگر می‌خواهید تغییراتی در ربات اعمال کنید، مراحل زیر را دنبال کنید:

### 1. ایجاد شاخه جدید

برای اعمال تغییرات، یک شاخه جدید ایجاد کنید:

```bash
git checkout -b feature-branch
```

### 2. انجام تغییرات

تغییرات مورد نظر را در کد اعمال کنید.

### 3. اضافه کردن تغییرات

تغییرات را به شاخه اضافه کنید:

```bash
git add .
git commit -m "Description of the changes"
```

### 4. ارسال تغییرات

تغییرات را به مخزن GitHub ارسال کنید:

```bash
git push origin feature-branch
```

### 5. ایجاد درخواست کشش (Pull Request)

از طریق GitHub، یک درخواست کشش برای ادغام تغییرات با شاخه اصلی ایجاد کنید.

## مشکلات و مشارکت

برای گزارش مشکلات یا پیشنهادات به [Issues](https://github.com/power0matin/telegram-music-downloader-bot/issues) بروید. اگر می‌خواهید به توسعه ربات کمک کنید، لطفاً یک [Pull Request](https://github.com/power0matin/telegram-music-downloader-bot/pulls) ارسال کنید.

## لایسنس

این پروژه تحت [MIT License](LICENSE) منتشر شده است.
```

### نکات مهم:

- **لینک‌ها**: جایگزین لینک‌های مربوطه با URL‌های واقعی پروژه‌ی شما شوید.
- **توکن بات**: توکن واقعی بات تلگرام خود را در فایل `config.py` قرار دهید.
- **سفارشی‌سازی**: به‌روزرسانی توضیحات و نام‌های مربوطه با جزئیات پروژه‌ی واقعی شما.

این README.md شامل تمام اطلاعات مورد نیاز برای راه‌اندازی، استفاده، و مشارکت در پروژه است و به کاربران کمک می‌کند تا به راحتی با پروژه آشنا شوند.

---
