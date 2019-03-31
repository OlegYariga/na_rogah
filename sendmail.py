from app import mail
from flask_mail import Message


# Function to send email
def send_mail(mail_to, subject, text):
    try:
        # Try to send message to user
        msg = Message()
        msg.subject = subject
        msg.recipients = [mail_to]
        msg.html = text
        mail.send(msg)
        return True
    # If in email was detected not-ascii symbols
    except UnicodeEncodeError:
        return False
    except Exception:
        return False
