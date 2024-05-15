import re
from eskiz_sms import EskizSMS
from pydantic import ValidationError

phone_regex = re.compile(r"^998([378]{2}|(9[013-57-9]))\d{7}$")


async def send_verification_code(code, phone_number):
    email = "eskiz_email"
    password = "eskiz_password"
    message = f"Assalomu alaykum! Sizning tasdiqlash kodingiz: {code}\nIltimos bu tasdiqlash kodini hechkimga bermang!"
    client = EskizSMS(email=email, password=password)
    client.send_sms(mobile_phone=f"+{phone_number}", message=message)


async def check_phone(phone):
    if re.fullmatch(phone_regex, phone):
        phone = "phone"
    else:
        data = {
            "success": False,
            'message': "Your phone number is incorrect"
        }
        raise ValidationError(data)
    return phone
