# មេរៀន: បង្កើត Telegram Bot ទទួលការបង់ប្រាក់តាម KHQR (Bakong)

នៅចុងមេរៀននេះ អ្នកនឹងមាន Telegram bot មួយដែល៖

1. បង្កើតរូប **KHQR** តាមចំនួនទឹកប្រាក់ដែលអតិថិជនត្រូវបង់ (USD ឬ KHR)
2. អតិថិជន scan ជាមួយ app ធនាគារណាក៏បាន (ABA, ACLEDA, Wing, Bakong …)
3. bot **ពិនិត្យដោយស្វ័យប្រវត្តិ** ថាបានបង់ហើយឬនៅ តាមរយៈ Bakong API
4. ពេលបង់រួច bot ប្រាប់អតិថិជន ហើយផ្ញើដំណឹងទៅអ្នកលក់ (admin)

```
អតិថិជន ──/pay 5──▶ Bot ──បង្កើត KHQR──▶ ផ្ញើរូប QR
   │                                          │
   └──scan & បង់ក្នុង app ធនាគារ──▶ Bakong      │
                                     ▲        │
          Bot សួររៀងរាល់ 5 វិនាទី ("បង់ហើយឬនៅ?" តាម md5)
                                     │
                              PAID ──▶ ✅ ជូនដំណឹងអតិថិជន + admin
```

---

## មាតិកា

- [ជំហាន 0: អ្វីដែលត្រូវរៀបចំ](#ជំហាន-0-អ្វីដែលត្រូវរៀបចំ)
- [ជំហាន 1: បង្កើត Telegram Bot ជាមួយ BotFather](#ជំហាន-1-បង្កើត-telegram-bot-ជាមួយ-botfather)
- [ជំហាន 2: យក Bakong Developer Token](#ជំហាន-2-យក-bakong-developer-token)
- [ជំហាន 3: រកមើល Bakong Account ID របស់អ្នក](#ជំហាន-3-រកមើល-bakong-account-id-របស់អ្នក)
- [ជំហាន 4: ដំឡើង Project](#ជំហាន-4-ដំឡើង-project)
- [ជំហាន 5: កំណត់ឯកសារ .env](#ជំហាន-5-កំណត់ឯកសារ-env)
- [ជំហាន 6: សាកល្បងបង្កើត KHQR](#ជំហាន-6-សាកល្បងបង្កើត-khqr)
- [ជំហាន 7: ដំណើរការ Bot](#ជំហាន-7-ដំណើរការ-bot)
- [ជំហាន 8: ស្វែងយល់ពីកូដ](#ជំហាន-8-ស្វែងយល់ពីកូដ)
- [ជំហាន 9: សុវត្ថិភាព និងការប្រើពិតប្រាកដ](#ជំហាន-9-សុវត្ថិភាព-និងការប្រើពិតប្រាកដ)
- [បញ្ហាដែលជួបញឹកញាប់](#បញ្ហាដែលជួបញឹកញាប់)

---

## ជំហាន 0: អ្វីដែលត្រូវរៀបចំ

| ត្រូវការ | ពិនិត្យ |
|---|---|
| Python 3.10 ឡើងទៅ | `python3 --version` |
| គណនី Telegram | — |
| គណនីធនាគារដែលភ្ជាប់ Bakong (ABA, ACLEDA, Wing, app Bakong …) | — |
| អ៊ីមែល សម្រាប់ចុះឈ្មោះ Bakong Developer | — |

---

## ជំហាន 1: បង្កើត Telegram Bot ជាមួយ BotFather

1. បើក Telegram ហើយស្វែងរក **@BotFather** (មានសញ្ញាធីកពណ៌ខៀវ)
2. វាយ `/newbot`
3. ដាក់ **ឈ្មោះ** bot ឧ. `My Shop Payment`
4. ដាក់ **username** ដែលបញ្ចប់ដោយ `bot` ឧ. `myshop_pay_bot`
5. BotFather នឹងផ្ញើ **token** មកឲ្យ មានទម្រង់ដូចនេះ៖
   ```
   123456789:AAHdqTcvCH1vGWJxfSeofSAs0K5PALDsaw
   ```
   👉 រក្សាទុក token នេះ ព្រោះវាជា **TELEGRAM_BOT_TOKEN**

> ⚠️ token នេះដូចជាលេខសម្ងាត់។ អ្នកណាមាន token គឺអាចបញ្ជា bot របស់អ្នកបាន។
> បើបែកធ្លាយ សូមវាយ `/revoke` ទៅ BotFather ដើម្បីប្តូរ token ថ្មី។

**ជម្រើស:** វាយ `/setcommands` ទៅ BotFather ហើយដាក់៖
```
start - ចាប់ផ្តើម
pay - បង់ប្រាក់ ឧ. /pay 5
myid - មើល chat id
```

---

## ជំហាន 2: យក Bakong Developer Token

Bakong Open API ជាសេវារបស់ **ធនាគារជាតិនៃកម្ពុជា (NBC)** ដែលអនុញ្ញាតឲ្យយើងពិនិត្យថា KHQR មួយត្រូវបានបង់ហើយឬនៅ។

1. ចូលទៅកាន់ **https://api-bakong.nbc.gov.kh/register**
2. បំពេញព័ត៌មាន ហើយបញ្ជាក់អ៊ីមែល
3. អ្នកនឹងទទួលបាន **Developer Token** (ខ្សែអក្សរវែង ចាប់ផ្តើមដោយ `eyJ...`)
   👉 នេះជា **BAKONG_TOKEN**

> 📌 **ចំណាំ:**
> - Token មាន **សុពលភាពប្រហែល 90 ថ្ងៃ** ហើយត្រូវ renew ជាមុនពេលផុតកំណត់ (នៅលើគេហទំព័រដដែល)
> - ការ **បង្កើត** KHQR មិនត្រូវការ token ទេ។ token ត្រូវការតែពេល **ពិនិត្យ** ការបង់ប្រាក់ប៉ុណ្ណោះ

---

## ជំហាន 3: រកមើល Bakong Account ID របស់អ្នក

**Bakong Account ID** ជាអាសយដ្ឋានគណនីទទួលប្រាក់ មានទម្រង់ `ឈ្មោះ@ធនាគារ` ឧ. `sokdara@aclb`

របៀបរក៖
- បើក app ធនាគាររបស់អ្នក ហើយរកផ្នែក **KHQR / Bakong / Receive money**។ ឧទាហរណ៍ app Bakong បង្ហាញ ID នៅលើ profile
- ឬ scan KHQR ផ្ទាល់ខ្លួនរបស់អ្នកជាមួយ app ផ្សេង ដើម្បីមើល ID
- បើរកមិនឃើញ សូមសួរធនាគាររបស់អ្នក

👉 នេះជា **BAKONG_ACCOUNT_ID**

---

## ជំហាន 4: ដំឡើង Project

```bash
# 1. ទាញយកមេរៀន
git clone https://github.com/loffyjamegit101/lessonAi.git
cd lessonAi

# 2. បង្កើត virtual environment (បន្ទប់ដាច់ដោយឡែកសម្រាប់ library)
python3 -m venv venv

# 3. បើកដំណើរការ venv
source venv/bin/activate          # macOS / Linux
# venv\Scripts\activate           # Windows

# 4. ដំឡើង library
pip install -r requirements.txt
```

Library ដែលយើងប្រើ៖

| Library | ប្រើសម្រាប់ |
|---|---|
| `python-telegram-bot` | ទំនាក់ទំនងជាមួយ Telegram |
| `bakong-khqr` | បង្កើត KHQR, រូប QR និងពិនិត្យការបង់ប្រាក់ |
| `python-dotenv` | អានការកំណត់ពីឯកសារ `.env` |

---

## ជំហាន 5: កំណត់ឯកសារ .env

```bash
cp .env.example .env
```

បើក `.env` ហើយបំពេញ៖

```env
TELEGRAM_BOT_TOKEN=123456789:AAH...     # ពីជំហាន 1
BAKONG_TOKEN=eyJhbGciOi...              # ពីជំហាន 2
BAKONG_ACCOUNT_ID=yourname@aclb         # ពីជំហាន 3
MERCHANT_NAME=My Shop
MERCHANT_CITY=Phnom Penh
ADMIN_CHAT_ID=                          # បំពេញនៅជំហាន 7
```

> 🔒 ឯកសារ `.env` ត្រូវបានដាក់ក្នុង `.gitignore` រួចហើយ ដូច្នេះវានឹងមិនត្រូវ push ចូល GitHub ទេ។

---

## ជំហាន 6: សាកល្បងបង្កើត KHQR

មុនដំណើរការ bot សូមសាកល្បងថាការបង្កើត QR ដំណើរការ៖

```bash
python test_khqr.py
```

លទ្ធផល៖
```
KHQR string : 00020101021229180014test_user@aclb52045999530384054040.015802KH5907My Shop6010Phnom Penh62110107TEST0019934...6304EA74
MD5         : 2abffe602f83aabc9e209fdcd4c9e1a8
✅ បានរក្សាទុករូប QR ក្នុង test_qr.png
```

បើក `test_qr.png` ហើយ scan ជាមួយ app ធនាគារ។ app គួរតែបង្ហាញ **ឈ្មោះអ្នកលក់** និង **$0.01** (មិនចាំបាច់បង់ទេ)។

### តើ KHQR string មានអ្វីខ្លះ?

KHQR ធ្វើតាមស្តង់ដារ **EMVCo** ដែលទិន្នន័យនីមួយៗមានទម្រង់ `ID(2) + ប្រវែង(2) + តម្លៃ`៖

| Tag | អត្ថន័យ | ឧទាហរណ៍ |
|---|---|---|
| `00` | Payload format | `01` |
| `01` | `11` = QR ឋិតិវន្ត (static), `12` = QR ថាមវន្ត (dynamic, មានចំនួនប្រាក់) | `12` |
| `29` | Bakong Account ID | `yourname@aclb` |
| `52` | Merchant category code | `5999` |
| `53` | រូបិយប័ណ្ណ `840` = USD, `116` = KHR | `840` |
| `54` | ចំនួនទឹកប្រាក់ | `0.01` |
| `58` | ប្រទេស | `KH` |
| `59` | ឈ្មោះអ្នកលក់ | `My Shop` |
| `60` | ទីក្រុង | `Phnom Penh` |
| `62` | ព័ត៌មានបន្ថែម (លេខវិក្កយបត្រ, ទូរស័ព្ទ …) | `TEST001` |
| `99` | ពេលបង្កើត និងពេលផុតកំណត់ | timestamp |
| `63` | CRC (checksum សម្រាប់ផ្ទៀងផ្ទាត់) | `EA74` |

👉 **MD5** គឺជា hash នៃ KHQR string ទាំងមូល។ យើងប្រើវាជា "លេខសម្គាល់" ដើម្បីសួរ Bakong ថាបានបង់ហើយឬនៅ។

---

## ជំហាន 7: ដំណើរការ Bot

```bash
python bot.py
```

បើឃើញ `🤖 Bot កំពុងដំណើរការ...` មានន័យថាជោគជ័យ។

សាកល្បងនៅលើ Telegram៖

1. ស្វែងរក bot របស់អ្នក (`@myshop_pay_bot`) ហើយចុច **Start**
2. វាយ `/myid` ហើយចម្លងលេខ ID ទៅដាក់ក្នុង `ADMIN_CHAT_ID` នៃ `.env` (ជម្រើស)។ រួច restart bot (`Ctrl+C` ហើយ `python bot.py` ម្តងទៀត)
3. វាយ `/pay 0.01` ដើម្បីទទួលរូប KHQR
4. scan ហើយបង់ $0.01 ជាមួយ app ធនាគារ
5. ក្នុងរយៈពេលប្រហែល 5 វិនាទី bot នឹងឆ្លើយថា **✅ បង់ប្រាក់ជោគជ័យ!**

| Command | មុខងារ |
|---|---|
| `/start` | សារស្វាគមន៍ |
| `/pay 5` | បង្កើត KHQR $5 |
| `/pay 20000 KHR` | បង្កើត KHQR 20,000៛ |
| `/myid` | បង្ហាញ chat id |
| ប៊ូតុង 🔄 | ពិនិត្យការបង់ប្រាក់ភ្លាមៗ |

---

## ជំហាន 8: ស្វែងយល់ពីកូដ

កូដទាំងអស់នៅក្នុង [`bot.py`](bot.py)។ ផ្នែកសំខាន់ៗមានដូចខាងក្រោម។

### 8.1 បង្កើត KHQR

```python
from bakong_khqr import KHQR
khqr = KHQR(BAKONG_TOKEN)

qr = khqr.create_qr(
    amount=5,
    currency="USD",                  # ឬ "KHR"
    account_id="yourname@aclb",
    merchant_name="My Shop",
    merchant_city="Phnom Penh",
    bill_number="INV1A2B3C4D",       # លេខវិក្កយបត្រមិនស្ទួន
)
md5 = qr.md5                         # លេខសម្គាល់សម្រាប់ពិនិត្យ
```

### 8.2 បំប្លែងទៅជារូបភាព ហើយផ្ញើទៅ Telegram

```python
image = khqr.qr_image(qr, format="bytes")    # រូប KHQR ដែលមានស៊ុម និងរចនាប័ទ្ម
await update.message.reply_photo(photo=image, caption="សូម scan ...")
```

### 8.3 ពិនិត្យការបង់ប្រាក់

```python
status = khqr.check_payment(md5)   # "PAID" ឬ "UNPAID"
```

នៅខាងក្រោយ មុខងារនេះហៅ Bakong API៖

```
POST https://api-bakong.nbc.gov.kh/v1/check_transaction_by_md5
Authorization: Bearer <BAKONG_TOKEN>
{"md5": "44c5673a19bbfea7150393542205b881"}
```

- `responseCode: 0` មានន័យថា **បានបង់**
- `responseCode: 1` មានន័យថា **មិនទាន់បង់** (ឬរកមិនឃើញ)

### 8.4 តាមដានដោយស្វ័យប្រវត្តិ (polling)

`watch_payment()` សួរ Bakong រៀងរាល់ **5 វិនាទី** រហូតដល់បង់រួច ឬអស់ពេល **10 នាទី**។
ដោយសារ `check_payment` ជាកូដ blocking យើងដំណើរការវាតាម `asyncio.to_thread()` ដើម្បីកុំឲ្យ bot គាំង ពេលមានអតិថិជនច្រើននាក់ក្នុងពេលតែមួយ។

អ្នកអាចកែតម្លៃទាំងនេះនៅខាងលើ `bot.py`៖

```python
PAYMENT_TIMEOUT_SECONDS = 10 * 60
POLL_INTERVAL_SECONDS = 5
```

---

## ជំហាន 9: សុវត្ថិភាព និងការប្រើពិតប្រាកដ

### ✅ ត្រូវធ្វើ
- **កុំ** push `.env` ឬ token ចូល GitHub ឬផ្ញើក្នុង chat
- **ផ្ទៀងផ្ទាត់ចំនួនប្រាក់នៅ server**: កុំទុកចិត្តតម្លៃដែលអតិថិជនវាយ។ ពេលលក់ទំនិញពិត ត្រូវគណនាតម្លៃពីតារាងទំនិញក្នុងកូដ ឬ database
- **ប្រើ database** (ឧ. SQLite) ជំនួស `pending_orders` ក្នុង memory។ បើ bot restart ការបញ្ជាទិញក្នុង memory នឹងបាត់
- **Renew Bakong token** មុនផុតកំណត់ 90 ថ្ងៃ (ដាក់ reminder ក្នុងប្រតិទិន)
- **កុំ poll លឿនពេក**: 5 វិនាទីគឺសមរម្យ។ បើលឿនជាងនេះ API អាចបដិសេធ (rate limit)

### 🚀 ដាក់ bot ឲ្យដំណើរការ 24/7
ពេលកុំព្យូទ័របិទ bot ក៏ឈប់ដែរ។ ដើម្បីឲ្យវាដំណើរការជាប់ជានិច្ច អាចដាក់លើ VPS (ឧ. DigitalOcean, Vultr, ឬ server នៅកម្ពុជា) ហើយប្រើ `systemd`, `pm2` ឬ `docker`។

> 📌 មានអ្នកប្រើខ្លះរាយការណ៍ថា Bakong API អាចបដិសេធសំណើពី IP នៅក្រៅប្រទេសកម្ពុជា។
> បើអ្នកជួប error timeout ឬ 403 ពេលដាក់លើ server បរទេស សូមសាកល្បងជាមួយ server ឬ VPN នៅកម្ពុជា។

### 💡 គំនិតពង្រីក
- បង្កើតម៉ឺនុយទំនិញជាមួយ Inline keyboard (`/shop`)
- រក្សាទុកប្រវត្តិការបង់ប្រាក់ក្នុង SQLite ហើយបន្ថែម command `/history` សម្រាប់ admin
- ប្រើ `khqr.get_payment(md5)` ដើម្បីយកព័ត៌មានលម្អិត (ឈ្មោះអ្នកបង់, hash ប្រតិបត្តិការ …)
- ប្រើ `khqr.check_bulk_payments([md5, ...])` ដើម្បីពិនិត្យរហូតដល់ 50 វិក្កយបត្រក្នុងពេលតែមួយ

---

## បញ្ហាដែលជួបញឹកញាប់

| បញ្ហា | មូលហេតុ / ដំណោះស្រាយ |
|---|---|
| `❌ ខ្វះការកំណត់ក្នុង .env` | មិនទាន់បង្កើត `.env` ឬភ្លេចបំពេញ token |
| `telegram.error.InvalidToken` | `TELEGRAM_BOT_TOKEN` ខុស។ សូមចម្លងពី BotFather ម្តងទៀត |
| `Unauthorized` / `Developer Token ... incorrect or expired` | `BAKONG_TOKEN` ខុស ឬផុតកំណត់។ សូម renew នៅ api-bakong.nbc.gov.kh |
| បង់រួចហើយ ប៉ុន្តែ bot នៅតែថា "មិនទាន់" | ពិនិត្យថា `BAKONG_ACCOUNT_ID` ត្រឹមត្រូវ, token នៅមានសុពលភាព ហើយរង់ចាំ 5–10 វិនាទី |
| app ធនាគារថា QR មិនត្រឹមត្រូវ | Account ID ខុសទម្រង់ ឬ QR ផុតកំណត់។ សូមបង្កើតថ្មី |
| `ModuleNotFoundError` | ភ្លេចបើក venv (`source venv/bin/activate`) ឬភ្លេច `pip install -r requirements.txt` |

---

## រចនាសម្ព័ន្ធ Project

```
lessonAi/
├── README.md          ← មេរៀននេះ
├── bot.py             ← កូដ Telegram bot
├── test_khqr.py       ← សាកល្បងបង្កើត KHQR
├── requirements.txt   ← បញ្ជី library
├── .env.example       ← គំរូការកំណត់ (ចម្លងទៅ .env)
└── .gitignore         ← ការពារកុំឲ្យ .env ត្រូវ push
```

## ឯកសារយោង
- Telegram Bot API: https://core.telegram.org/bots
- python-telegram-bot: https://docs.python-telegram-bot.org
- Bakong Open API: https://api-bakong.nbc.gov.kh
- bakong-khqr (Python): https://github.com/bsthen/bakong-khqr
- Bakong (NBC): https://bakong.nbc.gov.kh
