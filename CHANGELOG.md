# Changelog

All notable user-facing and operational changes are documented here.

## [1.2.0] - 2026-11-08

### Added
- Added a persistent SQLite store for pending quality callbacks. Pending selections retain their original expiration time across restarts, are scoped to their owner, and can be consumed only once.
- Added recovery for worker startup failures: a consumed callback is restored with its remaining original lifetime, and reserved worker capacity is released safely.
- Added explicit reporting for partial provider failures and skipped local audio files.
- Added CI coverage for Python 3.11, 3.12, 3.13, and 3.14.

### Changed
- Changed the default operating mode to Spotify metadata preview and a direct Spotify link. Metadata is obtained through Spotify's official oEmbed endpoint; the bot no longer relies on scraping Spotify embed pages.
- Kept the legacy audio-delivery path disabled by default. It is available only behind `ENABLE_AUTHORIZED_AUDIO_DELIVERY=true`, and only for operators who have obtained all required written platform permissions and rights-holder licences.
- Pinned `spotdl` to `4.6.0` and added regression checks for the CLI contract and incompatible dependency versions.
- Improved the VPS installer to validate the selected Python runtime, support an explicit `PYTHON_BIN`, and recreate virtual environments that use unsupported Python versions.
- Made Telegram audio uploads more resilient to transient network and rate-limit errors, including timeouts, with bounded retries.
- Enforced a conservative audio upload ceiling of 49,000,000 bytes and report oversized files separately from Telegram upload failures.
- Truncate Telegram audio captions within the 1,024 UTF-16-unit limit while preserving track identity.
- Updated English and Persian setup and compliance documentation.

### Fixed
- Fixed the historical Telegram upload timeout case by reopening the audio file for each retry.
- Fixed pending quality selections being lost when a worker thread could not start.
- Fixed callback ownership, expiry, and duplicate-consumption edge cases.

### Compatibility and migration notes
- This release intentionally defaults to metadata-preview-only behavior. Existing installations should review their `.env` file and keep `ENABLE_AUTHORIZED_AUDIO_DELIVERY=false` unless they have obtained the written permissions and licences described in [docs/COMPLIANCE.md](docs/COMPLIANCE.md).
- Setting `ENABLE_AUTHORIZED_AUDIO_DELIVERY=true` is an operator attestation only. It does not grant Spotify, provider, or copyright permissions.
- Python 3.11–3.14 is supported. The automated VPS installer targets Ubuntu 24.04; Ubuntu 22.04 needs a separately installed compatible Python runtime selected with `PYTHON_BIN`.

### Validation
- GitHub Actions CI passed on Python 3.11, 3.12, 3.13, and 3.14 for the release candidate source.
- Automated tests, Python bytecode compilation, and shell syntax validation run in the CI workflow.

---

## نسخهٔ ۱.۲.۰ — ۱۷ آبان ۱۴۰۵

### قابلیت‌ها و بهبودها
- ذخیرهٔ پایدار انتخاب کیفیت در SQLite؛ انتخاب‌های در انتظار پس از راه‌اندازی مجدد باقی می‌مانند، به کاربر اصلی محدود هستند و فقط یک‌بار مصرف می‌شوند.
- بازیابی انتخاب کیفیت در صورت شکست شروع worker، بدون تمدید زمان انقضای اولیه.
- گزارش جداگانهٔ خطاهای منبع دانلود، فایل‌های محلی ردشده و فایل‌های بیش‌ازحد بزرگ.
- افزودن ماتریس CI برای Python نسخه‌های ۳.۱۱ تا ۳.۱۴.
- محدودکردن حجم فایل صوتی ارسالی به ۴۹٬۰۰۰٬۰۰۰ بایت و کنترل مجدد آن پیش از ارسال به تلگرام.
- محدودکردن کپشن صوتی به سقف ۱۰۲۴ واحد UTF-16 با حفظ عنوان و نام هنرمند.
- افزایش پایداری ارسال با تلاش مجدد کنترل‌شده برای خطاهای موقت، از جمله timeout و محدودیت نرخ تلگرام.
- پین‌کردن spotDL روی نسخهٔ ۴.۶.۰ و اعتبارسنجی سازگاری آرگومان‌های CLI و وابستگی‌ها.
- بهبود نصب‌کنندهٔ VPS برای اعتبارسنجی نسخهٔ Python و پشتیبانی از `PYTHON_BIN`.

### تغییر مهم در رفتار پیش‌فرض
- حالت پیش‌فرض ربات فقط پیش‌نمایش محدود اطلاعات Spotify و لینک مستقیم به Spotify است.
- اطلاعات از endpoint رسمی oEmbed دریافت می‌شود و استخراج اطلاعات با scraping صفحات embed انجام نمی‌شود.
- مسیر قدیمی ارسال فایل صوتی به‌صورت پیش‌فرض غیرفعال است. فعال‌سازی آن فقط با `ENABLE_AUTHORIZED_AUDIO_DELIVERY=true` و پس از دریافت مجوزهای کتبی لازم از پلتفرم‌ها و صاحبان حقوق محتوا مجاز است.
- مقداردهی این متغیر به `true` به‌تنهایی هیچ مجوزی ایجاد نمی‌کند؛ جزئیات در [سند انطباق پروژه](docs/COMPLIANCE.md) آمده است.

### اصلاحات
- رفع خطای timeout هنگام ارسال فایل به تلگرام با بازگشایی فایل در هر تلاش مجدد.
- بازیابی انتخاب کیفیت در صورت شکست ایجاد thread پردازش.
- رفع لبه‌های مرتبط با مالکیت callback، انقضا و مصرف تکراری.

### سازگاری و مهاجرت
- Python نسخه‌های ۳.۱۱ تا ۳.۱۴ پشتیبانی می‌شوند.
- نصب‌کنندهٔ خودکار برای Ubuntu 24.04 آماده شده است؛ در Ubuntu 22.04 باید نسخهٔ سازگار Python جداگانه نصب و با `PYTHON_BIN` انتخاب شود.
- پس از ارتقا، تنظیم `ENABLE_AUTHORIZED_AUDIO_DELIVERY` را بررسی کنید و آن را در حالت عادی `false` نگه دارید.
