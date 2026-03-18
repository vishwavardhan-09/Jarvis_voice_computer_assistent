import smtplib
import os
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

def send_email(to_email, subject, body):
    """
    Sends an email using Gmail SMTP.
    Requires EMAIL_ADDRESS and EMAIL_PASSWORD (App Password) in .env.
    """
    email_address = os.getenv("EMAIL_ADDRESS")
    email_password = os.getenv("EMAIL_PASSWORD")

    if not email_address or not email_password or "your-email" in email_address:
        print("❌ Email credentials not configured in .env")
        return False, "Email credentials not configured."

    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = email_address
        msg['To'] = to_email
        msg.set_content(body)

        # Connect to Gmail SMTP
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(email_address, email_password)
            smtp.send_message(msg)
        
        print(f"📧 Email sent successfully to {to_email}")
        return True, "Email sent successfully."
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False, str(e)

if __name__ == "__main__":
    # Test
    # success, msg = send_email("test@example.com", "Test Subject", "Test Body")
    # print(msg)
    pass
