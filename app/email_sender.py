import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy.orm import Session
from . import crud

def send_email(db: Session, to_email: str, subject: str, body: str):
    smtp_settings = crud.get_smtp_settings(db)
    if not smtp_settings or not smtp_settings.server:
        # In a real app, you'd have a more robust error handling system
        # or a default mailer. For now, we just block sending.
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

    try:
        # Use a with statement for cleaner connection handling
        with smtplib.SMTP(smtp_settings.server, smtp_settings.port) as server:
            server.starttls()
            # The password stored in the DB is what we use.
            # The API doesn't return it, but the CRUD layer can access it.
            if smtp_settings.username and smtp_settings.password:
                server.login(smtp_settings.username, smtp_settings.password)

            server.sendmail(smtp_settings.sender_email, to_email, message.as_string())

        print(f"Successfully sent email to {to_email}")
        return True
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")
        return False
