from app.services.email_service import (
    send_verification_email_service,
)


def send_verification_email(email, verification_code, subject):
    return send_verification_email_service(email, verification_code, subject)
