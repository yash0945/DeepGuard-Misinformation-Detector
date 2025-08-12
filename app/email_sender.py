import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from sqlalchemy.orm import Session
from typing import List, Optional

from . import crud

def send_email(db: Session, to_email: str, subject: str, body: str, attachments: Optional[List[str]] = None):
    smtp_settings = crud.get_smtp_settings(db)
    if not smtp_settings or not smtp_settings.server:
        print("SMTP settings are not configured. Cannot send email.")
        return False

    if not smtp_settings.sender_email:
        print("Sender email is not configured in SMTP settings. Cannot send email.")
        return False

    message = MIMEMultipart()
    message["From"] = smtp_settings.sender_email
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "html"))

    if attachments:
        for file_path in attachments:
            try:
                with open(file_path, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {os.path.basename(file_path)}",
                )
                message.attach(part)
            except Exception as e:
                print(f"Could not attach file {file_path}: {e}")

    try:
        with smtplib.SMTP(smtp_settings.server, smtp_settings.port) as server:
            server.starttls()
            if smtp_settings.username and smtp_settings.password:
                server.login(smtp_settings.username, smtp_settings.password)
            server.sendmail(smtp_settings.sender_email, to_email, message.as_string())
        print(f"Successfully sent email to {to_email}")
        return True
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")
        return False
