"""
Telegram Bot ទទួលការបង់ប្រាក់តាម KHQR (Bakong)

ដំណើរការ:
  1. អតិថិជនវាយ /pay 5        -> bot បង្កើត KHQR $5 ហើយផ្ញើរូប QR
  2. អតិថិជន scan ជាមួយ app ធនាគារណាមួយ (ABA, ACLEDA, Wing, Bakong ...)
  3. bot ពិនិត្យស្ថានភាពជាមួយ Bakong API រៀងរាល់ 5 វិនាទី
  4. ពេលបង់រួច bot ប្រាប់អតិថិជន (និង admin) ថា "បង់ប្រាក់ជោគជ័យ"
"""

import asyncio
import logging
import os
import time
import uuid

from bakong_khqr import KHQR
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

# ---------------------------------------------------------------------------
# ការកំណត់ (អានពីឯកសារ .env)
# ---------------------------------------------------------------------------
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
BAKONG_TOKEN = os.getenv("BAKONG_TOKEN", "")
BAKONG_ACCOUNT_ID = os.getenv("BAKONG_ACCOUNT_ID", "")      # ឧ. yourname@aclb
MERCHANT_NAME = os.getenv("MERCHANT_NAME", "My Shop")
MERCHANT_CITY = os.getenv("MERCHANT_CITY", "Phnom Penh")
MERCHANT_PHONE = os.getenv("MERCHANT_PHONE") or None
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID") or None          # chat id អ្នកលក់ (ជម្រើស)

PAYMENT_TIMEOUT_SECONDS = 10 * 60   # រង់ចាំការបង់ប្រាក់អតិបរមា 10 នាទី
POLL_INTERVAL_SECONDS = 5           # ពិនិត្យរៀងរាល់ 5 វិនាទី

logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)
log = logging.getLogger("khqr-bot")

khqr = KHQR(BAKONG_TOKEN)

# ការបញ្ជាទិញដែលកំពុងរង់ចាំ: md5 -> ព័ត៌មាន
# (សម្រាប់មេរៀន យើងទុកក្នុង memory។ ពេលប្រើពិត គួរប្រើ database ដូចជា SQLite)
pending_orders: dict[str, dict] = {}


# ---------------------------------------------------------------------------
# មុខងារជំនួយ
# ---------------------------------------------------------------------------
def parse_amount(args: list[str]) -> tuple[float, str]:
    """បំប្លែង '/pay 5' ឬ '/pay 20000 KHR' ទៅជា (amount, currency)"""
    if not args:
        raise ValueError("សូមបញ្ចូលចំនួនទឹកប្រាក់។ ឧ. /pay 5 ឬ /pay 20000 KHR")

    try:
        amount = float(args[0])
    except ValueError:
        raise ValueError("ចំនួនទឹកប្រាក់មិនត្រឹមត្រូវទេ។ ឧ. /pay 2.50")

    currency = args[1].upper() if len(args) > 1 else "USD"
    if currency not in ("USD", "KHR"):
        raise ValueError("រូបិយប័ណ្ណត្រូវតែ USD ឬ KHR")
    if currency == "USD" and amount < 0.01:
        raise ValueError("ចំនួនអប្បបរមាគឺ 0.01 USD")
    if currency == "KHR":
        if amount < 100:
            raise ValueError("ចំនួនអប្បបរមាគឺ 100 KHR")
        amount = int(amount)  # ប្រាក់រៀលមិនមានខ្ទង់ទសភាគ
    return amount, currency


def format_money(amount: float, currency: str) -> str:
    return f"${amount:,.2f}" if currency == "USD" else f"{amount:,.0f}៛"


async def check_paid(md5: str) -> bool:
    """សួរ Bakong API ថា QR នេះបានបង់ហើយឬនៅ"""
    # check_payment ជាកូដ blocking ដូច្នេះដំណើរការវាក្នុង thread ផ្សេង
    status = await asyncio.to_thread(khqr.check_payment, md5)
    return status == "PAID"


async def mark_paid(md5: str, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ពេលបង់រួច: ជូនដំណឹងអតិថិជន និង admin"""
    order = pending_orders.pop(md5, None)
    if order is None:   # បានដោះស្រាយរួចហើយ
        return

    money = format_money(order["amount"], order["currency"])
    await context.bot.send_message(
        chat_id=order["chat_id"],
        text=f"✅ បង់ប្រាក់ជោគជ័យ!\n\nលេខវិក្កយបត្រ: {order['bill']}\nចំនួន: {money}\nអរគុណច្រើន 🙏",
    )
    if ADMIN_CHAT_ID:
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"💰 ទទួលបានប្រាក់ {money}\nវិក្កយបត្រ: {order['bill']}\nពី: {order['user']}",
        )
    log.info("PAID %s %s", order["bill"], money)


async def watch_payment(md5: str, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ពិនិត្យស្ថានភាពការបង់ប្រាក់ម្តងហើយម្តងទៀត រហូតបង់រួច ឬអស់ពេល"""
    deadline = time.time() + PAYMENT_TIMEOUT_SECONDS
    while time.time() < deadline:
        if md5 not in pending_orders:       # អ្នកប្រើបានចុច "ពិនិត្យ" ហើយបង់រួចហើយ
            return
        try:
            if await check_paid(md5):
                await mark_paid(md5, context)
                return
        except ValueError as e:             # ឧ. Token ខុស ឬផុតកំណត់
            log.warning("Bakong API error: %s", e)
        await asyncio.sleep(POLL_INTERVAL_SECONDS)

    order = pending_orders.pop(md5, None)
    if order:
        await context.bot.send_message(
            chat_id=order["chat_id"],
            text=f"⌛ QR សម្រាប់វិក្កយបត្រ {order['bill']} អស់ពេលហើយ។ សូមវាយ /pay ម្តងទៀត។",
        )


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "សួស្តី! 👋 ខ្ញុំជា bot ទទួលការបង់ប្រាក់តាម KHQR។\n\n"
        "📌 របៀបប្រើ:\n"
        "/pay 5 — បង់ $5\n"
        "/pay 20000 KHR — បង់ 20,000៛\n"
        "/myid — មើល chat id របស់អ្នក"
    )


async def my_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f"Chat ID របស់អ្នក: {update.effective_chat.id}")


async def pay(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        amount, currency = parse_amount(context.args)
    except ValueError as e:
        await update.message.reply_text(f"⚠️ {e}")
        return

    bill = "INV" + uuid.uuid4().hex[:8].upper()   # លេខវិក្កយបត្រមិនស្ទួន

    # 1) បង្កើត KHQR string (ដំណើរការក្នុងម៉ាស៊ីន មិនចាំបាច់ internet)
    qr = khqr.create_qr(
        amount=amount,
        currency=currency,
        account_id=BAKONG_ACCOUNT_ID,
        merchant_name=MERCHANT_NAME,
        merchant_city=MERCHANT_CITY,
        phone_number=MERCHANT_PHONE,
        bill_number=bill,
        store_label=MERCHANT_NAME[:25],
        terminal_label="TelegramBot",
    )
    md5 = qr.md5   # លេខសម្គាល់សម្រាប់ពិនិត្យការបង់ប្រាក់

    # 2) បំប្លែងទៅជារូបភាព KHQR
    image = khqr.qr_image(qr, format="bytes")

    pending_orders[md5] = {
        "chat_id": update.effective_chat.id,
        "user": update.effective_user.full_name,
        "bill": bill,
        "amount": amount,
        "currency": currency,
    }

    # 3) ផ្ញើរូប QR + ប៊ូតុង "ពិនិត្យការបង់ប្រាក់"
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🔄 ពិនិត្យការបង់ប្រាក់", callback_data=f"check:{md5}")]]
    )
    await update.message.reply_photo(
        photo=image,
        caption=(
            f"🧾 វិក្កយបត្រ: {bill}\n"
            f"💵 ចំនួន: {format_money(amount, currency)}\n\n"
            "សូម scan QR នេះជាមួយ app ធនាគាររបស់អ្នក។\n"
            f"QR មានសុពលភាព {PAYMENT_TIMEOUT_SECONDS // 60} នាទី។"
        ),
        reply_markup=keyboard,
    )

    # 4) ចាប់ផ្តើមតាមដានការបង់ប្រាក់នៅខាងក្រោយ
    context.application.create_task(watch_payment(md5, context))


async def check_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    md5 = query.data.split(":", 1)[1]

    if md5 not in pending_orders:
        await query.answer("វិក្កយបត្រនេះបានបញ្ចប់រួចហើយ (បង់រួច ឬអស់ពេល)។", show_alert=True)
        return

    try:
        paid = await check_paid(md5)
    except ValueError as e:
        await query.answer(f"មានបញ្ហា: {e}", show_alert=True)
        return

    if paid:
        await query.answer("✅ បង់រួចហើយ!")
        await mark_paid(md5, context)
    else:
        await query.answer("⏳ មិនទាន់ទទួលបានការបង់ប្រាក់ទេ។ សូមរង់ចាំបន្តិច។", show_alert=True)


# ---------------------------------------------------------------------------
def main() -> None:
    missing = [n for n in ("TELEGRAM_BOT_TOKEN", "BAKONG_TOKEN", "BAKONG_ACCOUNT_ID") if not os.getenv(n)]
    if missing:
        raise SystemExit(f"❌ ខ្វះការកំណត់ក្នុង .env: {', '.join(missing)}")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("myid", my_id))
    app.add_handler(CommandHandler("pay", pay))
    app.add_handler(CallbackQueryHandler(check_button, pattern=r"^check:"))

    log.info("🤖 Bot កំពុងដំណើរការ... (ចុច Ctrl+C ដើម្បីបញ្ឈប់)")
    app.run_polling()


if __name__ == "__main__":
    main()
