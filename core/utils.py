import re
import random
from decouple import config
from eskiz_sms import EskizSMS

phone_regex = re.compile(r"^998([378]{2}|(9[013-57-9]))\d{7}$")


async def create_verification_code():
    return "".join([str(random.randint(0, 100) % 10) for _ in range(6)])


async def send_verification_code(code, phone_number):
    email = config("ESKIZ_EMAIL")
    password = config("ESKIZ_PASSWORD")
    message = f"Assalomu alaykum! Sizning tasdiqlash kodingiz: {code}\nIltimos bu tasdiqlash kodini hechkimga bermang!"
    client = EskizSMS(email=email, password=password)
    client.send_sms(mobile_phone=f"+{phone_number}", message=message)


async def check_phone(phone: str) -> bool:
    return bool(phone_regex.match(phone))
