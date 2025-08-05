# 🎵 Installation Summary - خلاصه نصب

## 📋 What's Been Improved / بهبودهای انجام شده

### ✅ Files Created / فایل‌های ایجاد شده
- `setup_bot.sh` - Automatic setup script / اسکریپت نصب خودکار
- `start_bot.sh` - Bot startup script / اسکریپت شروع ربات  
- `.env.example` - Configuration template / قالب تنظیمات
- `README.md` - Complete English documentation / مستندات کامل انگلیسی
- `README.fa.md` - Complete Persian documentation / مستندات کامل فارسی

### ✅ Features Added / ویژگی‌های اضافه شده
- One-command installation / نصب با یک دستور
- Automatic dependency management / مدیریت خودکار وابستگی‌ها
- Cross-platform support / پشتیبانی چندپلتفرمه
- Enhanced error handling / مدیریت خطای بهبود یافته
- Interactive setup wizard / راهنمای نصب تعاملی
- Complete documentation in both languages / مستندات کامل به دو زبان

## 🚀 Quick Setup / نصب سریع

### For English Users:
```bash
git clone <your-repo-url>
cd spotify-downloader-bot
./setup_bot.sh
```

### برای کاربران فارسی:
```bash
git clone <آدرس-مخزن-شما>
cd spotify-downloader-bot
./setup_bot.sh
```

## 📖 Documentation Links / لینک‌های مستندات

- **English Guide**: [README.md](README.md)
- **راهنمای فارسی**: [README.fa.md](README.fa.md)

## 🔑 Bot Token Setup / تنظیم توکن ربات

### Get Token / دریافت توکن:
1. Message @BotFather on Telegram / پیام به @BotFather در تلگرام
2. Send `/newbot` / ارسال `/newbot`
3. Follow instructions / دستورالعمل‌ها را دنبال کنید
4. Copy the token / توکن را کپی کنید

### Configure Token / تنظیم توکن:
```bash
# Edit .env file / ویرایش فایل .env
nano .env

# Add your token / توکن خود را اضافه کنید
BOT_TOKEN=your_actual_token_here
```

## 🎯 Usage / نحوه استفاده

1. **Start bot / شروع ربات**: `./start_bot.sh`
2. **Send Spotify links / ارسال لینک‌های اسپاتیفای** to your bot
3. **Choose quality / انتخاب کیفیت** (128kbps or 320kbps)
4. **Receive music / دریافت موزیک**! 🎵

## 🔧 Troubleshooting / رفع مشکلات

### Common Issues / مشکلات رایج:

**Dependencies missing / وابستگی‌ها نصب نشده:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**Token not set / توکن تنظیم نشده:**
```bash
nano .env
# Add: BOT_TOKEN=your_token
```

**Permission errors / خطای دسترسی:**
```bash
chmod +x setup_bot.sh start_bot.sh
```

## 🆘 Support / پشتیبانی

- **English**: Check [README.md](README.md)
- **فارسی**: [README.fa.md](README.fa.md) را بررسی کنید
- **Issues**: Open a GitHub issue / در گیت‌هاب issue باز کنید

## 🎉 Success! / موفقیت!

Your Spotify Downloader Bot is now ready to use!
ربات دانلود اسپاتیفای شما آماده استفاده است!

Happy downloading! 🎵 / دانلود شاد! 🎵