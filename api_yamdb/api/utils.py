import secrets
import string
from django.core.mail import send_mail


def generate_confirmation_code(length=10):
    characters = string.ascii_letters + string.digits
    confirmation_code = ''.join(
        secrets.choice(characters) for _ in range(length))
    return confirmation_code


def send_confirmation_email(email, confirmation_code):
    subject = 'Confirmation Code'
    message = f'Your confirmation code is {confirmation_code}'
    from_email = 'your-email@example.com'
    recipient_list = [email]

    send_mail(subject, message, from_email, recipient_list)
