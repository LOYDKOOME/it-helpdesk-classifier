# email_utils.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_confirmation_email(to_email, user_name, issue_summary, category):
    sender_email = ("loydkooome@gmail.com")
    sender_password = ("loyd")  # Use an App Password for Gmail

    subject = "IT Helpdesk Ticket Confirmation"
    body = f"""
    Hello {user_name},

    Your IT helpdesk ticket has been successfully submitted.

    Issue Summary: {issue_summary}
    Predicted Category: {category}

    We'll get back to you as soon as possible.

    Regards,  
    IT Helpdesk Team
    """

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        print(f"Email sent to {to_email}")
    except Exception as e:
        print("Error sending email:", e)
