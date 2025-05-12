import smtplib
import random
from email.message import EmailMessage

# === Configure with your Gmail credentials ===
SENDER_EMAIL = "your_email@gmail.com"
SENDER_PASSWORD = "your_app_password"  # Use an App Password if 2FA is enabled

# === OTP GENERATION ===
def generate_otp(length=6):
    """Generate numeric OTP"""
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

# === EMAIL SENDER ===
def send_otp_email(receiver_email, otp):
    """Send OTP to the given email"""
    msg = EmailMessage()
    msg.set_content(f"Your OTP for the College Voting System is: {otp}")
    msg['Subject'] = "OTP Verification - College Voting System"
    msg['From'] = SENDER_EMAIL
    msg['To'] = receiver_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
            smtp.send_message(msg)
        return True
    except Exception as e:
        return str(e)
