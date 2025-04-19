import smtplib
from email.message import EmailMessage

smtp_host = "smtp.gmail.com"
smtp_port = 587
smtp_user = "aigor9534@gmail.com"
smtp_password = "wgriazacuqserclv"

msg = EmailMessage()
msg.set_content("Test email")
msg["Subject"] = "Test"
msg["From"] = smtp_user
msg["To"] = smtp_user

with smtplib.SMTP(smtp_host, smtp_port) as server:
    server.starttls()
    server.login(smtp_user, smtp_password)
    server.send_message(msg)
print("Email sent successfully!")