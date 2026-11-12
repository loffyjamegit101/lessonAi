"""
សាកល្បងបង្កើត KHQR ដោយមិនចាំបាច់មាន Telegram bot ឬ Bakong token។

ដំណើរការ:  python test_khqr.py
លទ្ធផល:    បង្កើតឯកសារ test_qr.png ដែលអ្នកអាចបើកមើល ហើយ scan សាកល្បងបាន
"""

import os

from bakong_khqr import KHQR
from dotenv import load_dotenv

load_dotenv()

khqr = KHQR()  # ការបង្កើត QR មិនត្រូវការ token ទេ (token ត្រូវការតែពេលពិនិត្យការបង់ប្រាក់)

qr = khqr.create_qr(
    amount=0.01,
    currency="USD",
    account_id=os.getenv("BAKONG_ACCOUNT_ID") or "test_user@aclb",
    merchant_name=os.getenv("MERCHANT_NAME") or "My Shop",
    merchant_city=os.getenv("MERCHANT_CITY") or "Phnom Penh",
    bill_number="TEST001",
)

print("KHQR string :", qr)
print("MD5         :", qr.md5)

khqr.qr_image(qr, format="png", output_path="test_qr.png")
print("✅ បានរក្សាទុករូប QR ក្នុង test_qr.png")
