# Telegram Music Downloader Bot

این پروژه شامل یک ربات تلگرام است که به کاربران این امکان را می‌دهد تا آهنگ‌ها، آلبوم‌ها و پلی‌لیست‌ها را از اسپاتیفای دانلود کنند. کاربران می‌توانند با ارسال لینک اسپاتیفای به ربات، آهنگ‌های خود را با کیفیت‌های مختلف (128 kbps و 320 kbps) دریافت کنند.

## ویژگی‌ها

- دانلود آهنگ‌ها، آلبوم‌ها و پلی‌لیست‌ها از اسپاتیفای.
- انتخاب کیفیت دانلود (128 kbps یا 320 kbps).
- ارسال آهنگ‌های دانلود شده به کاربران.

## پیش‌نیازها

برای اجرای این ربات، نیاز به نصب ابزارهای زیر است:

- [Python 3.7+](https://www.python.org/downloads/)
- [SpotDL](https://github.com/spotDL/spotify-downloader) - برای دانلود آهنگ‌ها از اسپاتیفای
- [python-telegram-bot](https://pypi.org/project/pyTelegramBotAPI/) - برای تعامل با API تلگرام

## نصب

### 1. کلون کردن مخزن

برای شروع، مخزن را از GitHub کلون کنید:

```bash
git clone https://github.com/yourusername/telegram-music-downloader-bot.git
cd telegram-music-downloader-bot
