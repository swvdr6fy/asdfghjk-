# ArchiSMS-Bot

بات تلگرام مستقل برای مدیریت ثبت‌نام کاربران، دوره آزمایشی (Trial)، وضعیت حساب و پنل ادمین.

> **مهم:** این بات در حال حاضر مستقل از اپلیکیشن اندروید ArchiSMS است و **هیچ پیامک، رمز یکبار مصرف، کد بانکی یا محتوای حساس دیگری را دریافت، ذخیره یا فوروارد نمی‌کند.** فقط برای ثبت کاربر، وضعیت حساب، Trial و تست اتصال استفاده می‌شود.

## ساختار پروژه

```
ArchiSMS-Bot/
├── bot.py              # نقطه ورود اصلی
├── config.py           # خواندن تنظیمات از Environment Variables
├── database.py         # لایه دسترسی به SQLite
├── keyboards.py        # کیبوردهای Inline
├── handlers.py         # هندلرهای دستورات و دکمه‌ها
├── requirements.txt
├── Procfile
├── runtime.txt
├── .env.example
├── .gitignore
└── README.md
```

## تکنولوژی

- Python 3.12
- python-telegram-bot 21.x (async)
- SQLite (کتابخانه استاندارد sqlite3)

---

## ۱. ساخت بات در BotFather

1. در تلگرام به [@BotFather](https://t.me/BotFather) پیام دهید.
2. دستور `/newbot` را بفرستید.
3. یک نام و یک username (باید به `bot` ختم شود) برای بات انتخاب کنید.
4. BotFather یک **BOT_TOKEN** به شما می‌دهد، مثل:
   `123456789:AAExxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
5. این توکن را جایی امن نگه دارید — هرگز آن را در کد یا GitHub قرار ندهید.

## ۲. پیدا کردن Telegram ID ادمین

1. به [@userinfobot](https://t.me/userinfobot) پیام دهید (یا هر بات مشابه دیگری).
2. عدد Telegram ID خودتان را دریافت کنید — همین عدد مقدار `ADMIN_ID` است.

## ۳. اجرای Local

```bash
git clone <آدرس-ریپوی-شما>
cd ArchiSMS-Bot

python3.12 -m venv venv
source venv/bin/activate      # ویندوز: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# سپس مقادیر BOT_TOKEN و ADMIN_ID را داخل .env ویرایش کنید

python bot.py
```

## ۴. ساخت Repository در GitHub

```bash
git init
git add .
git commit -m "Initial commit: ArchiSMS-Bot"
git branch -M main
git remote add origin https://github.com/<your-username>/ArchiSMS-Bot.git
git push -u origin main
```

فایل `.env` به‌خاطر `.gitignore` هرگز Push نمی‌شود — همیشه قبل از Push با `git status` مطمئن شوید که `.env` در لیست فایل‌های stage شده نیست.

## ۵. Deploy روی Railway

1. وارد [railway.app](https://railway.app) شوید و یک پروژه جدید بسازید.
2. گزینه **Deploy from GitHub repo** را انتخاب کرده و ریپوی `ArchiSMS-Bot` را انتخاب کنید.
3. Railway به‌طور خودکار `Procfile` را تشخیص داده و پروسه `worker` را اجرا می‌کند.
4. به بخش **Variables** پروژه بروید و متغیرهای زیر را اضافه کنید:

   | Key         | Value                              |
   |-------------|-------------------------------------|
   | `BOT_TOKEN` | توکن دریافتی از BotFather            |
   | `ADMIN_ID`  | Telegram ID شما                     |
   | `DB_PATH`   | `archisms_bot.db` (یا مسیر دلخواه)   |

5. Deploy را اجرا کنید (یا منتظر Deploy خودکار بمانید).
6. از تب **Logs** مطمئن شوید پیام `ArchiSMS-Bot در حال اجراست...` نمایش داده شده است.

> **نکته دیتابیس:** فضای فایل‌سیستم Railway برای سرویس‌های worker به‌صورت پیش‌فرض ephemeral است، یعنی با هر Redeploy ممکن است فایل SQLite ریست شود. برای نگهداری دائمی داده در Railway می‌توانید یک **Volume** به سرویس متصل کرده و `DB_PATH` را داخل همان Volume تنظیم کنید.

## ۶. دستورات بات

| دستور     | توضیح                                      |
|-----------|---------------------------------------------|
| `/start`  | ثبت‌نام خودکار و نمایش منوی اصلی            |
| `/admin`  | پنل مدیریت (فقط برای `ADMIN_ID`)            |

## ۷. جدول Database

جدول `users`:

| ستون          | نوع     | توضیح                        |
|----------------|---------|-------------------------------|
| `telegram_id`  | INTEGER | کلید اصلی، شناسه تلگرام کاربر |
| `username`     | TEXT    | نام کاربری تلگرام (اختیاری)  |
| `first_name`   | TEXT    | نام کوچک کاربر                |
| `created_at`   | TEXT    | زمان ثبت‌نام (ISO 8601, UTC)  |
| `trial_start`  | TEXT    | زمان شروع Trial                |
| `trial_until`  | TEXT    | زمان پایان Trial                |

## ۸. امنیت

- `BOT_TOKEN` و `ADMIN_ID` فقط از Environment Variables خوانده می‌شوند و هیچ‌جای کد hard-code نشده‌اند.
- فایل `.env` در `.gitignore` قرار دارد و نباید هرگز Commit شود.
- دسترسی به `/admin` فقط برای Telegram ID برابر با `ADMIN_ID` مجاز است؛ تلاش‌های دیگر Log می‌شوند.

## ۹. توسعه‌های آینده (خارج از محدوده فعلی)

طبق طراحی فعلی، این بات هیچ ارتباطی با پیامک یا محتوای حساس ندارد. هر توسعه‌ای در این زمینه باید جداگانه، با رعایت کامل حریم خصوصی کاربر و قوانین پلتفرم‌ها، طراحی و بررسی شود.
