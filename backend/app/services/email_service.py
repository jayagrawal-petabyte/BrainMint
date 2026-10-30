import smtplib
import httpx
from pathlib import Path
from email.message import EmailMessage
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.enquiry import Enquiry, EmailStatus

class EmailDeliveryError(Exception):
    pass

TEMPLATE_DIR = Path(__file__).resolve().parent.parent / "templates" / "email"

def render_template(template_name: str, context: dict) -> str:
    template_path = TEMPLATE_DIR / template_name
    if not template_path.exists():
        return ""
    html_content = template_path.read_text(encoding="utf-8")
    for key, value in context.items():
        html_content = html_content.replace(f"{{{{{key}}}}}", str(value or "N/A"))
    return html_content

def send_mail(recipient: str, subject: str, html_body: str, plain_fallback: str):
    provider = getattr(settings, "EMAIL_PROVIDER", "smtp").lower()
    if provider == "sendgrid":
        headers = {
            "Authorization": f"Bearer {settings.SENDGRID_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "personalizations": [{"to": [{"email": recipient}]}],
            "from": {"email": settings.EMAILS_FROM_EMAIL or settings.SMTP_USER},
            "subject": subject,
            "content": [{"type": "text/html", "value": html_body or plain_fallback}]
        }
        response = httpx.post("https://api.sendgrid.com/v3/mail/send", json=payload, headers=headers, timeout=10.0)
        response.raise_for_status()

    elif provider == "mailgun":
        auth = ("api", settings.MAILGUN_API_KEY)
        data = {
            "from": f"Support <{settings.EMAILS_FROM_EMAIL or settings.SMTP_USER}>",
            "to": [recipient],
            "subject": subject,
            "html": html_body or plain_fallback
        }
        response = httpx.post(f"https://api.mailgun.net/v3/{settings.MAILGUN_DOMAIN}/messages", data=data, auth=auth, timeout=10.0)
        response.raise_for_status()

    else:
        use_ssl = getattr(settings, "SMTP_SSL", False)
        smtp_cls = smtplib.SMTP_SSL if use_ssl else smtplib.SMTP

        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = settings.EMAILS_FROM_EMAIL or settings.SMTP_USER
        msg["To"] = recipient
        msg.set_content(plain_fallback)
        if html_body:
            msg.add_alternative(html_body, subtype="html")

        with smtp_cls(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if not use_ssl and getattr(settings, "SMTP_TLS", True):
                server.starttls()
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)

def send_enquiry_notification(enquiry_id: int):
    db: Session = SessionLocal()
    enquiry = None
    try:
        enquiry = db.query(Enquiry).filter(Enquiry.id == enquiry_id).first()
        if not enquiry:
            return

        context = {
            "enquiry_id": enquiry.id,
            "name": enquiry.name,
            "email": enquiry.email,
            "phone": enquiry.phone,
            "service": enquiry.service,
            "message": enquiry.message,
            "source": enquiry.source,
        }

        company_html = render_template("enquiry_notification.html", context)
        company_plain = f"New enquiry received via {enquiry.source}:\n\nName: {enquiry.name}\nEmail: {enquiry.email}"
        send_mail(settings.EMAILS_TO_EMAIL, f"New Enquiry from {enquiry.name}", company_html, company_plain)

        enquiry.email_status = EmailStatus.sent
        enquiry.email_error = None
        db.commit()

    except Exception as e:
        db.rollback()
        if not enquiry:
            enquiry = db.query(Enquiry).filter(Enquiry.id == enquiry_id).first()
        if enquiry:
            enquiry.email_status = EmailStatus.failed
            enquiry.email_error = str(e)
            db.commit()
        raise EmailDeliveryError(str(e)) from e
    finally:
        db.close()

def send_enquiry_acknowledgement(enquiry_id: int):
    db: Session = SessionLocal()
    try:
        enquiry = db.query(Enquiry).filter(Enquiry.id == enquiry_id).first()
        if not enquiry or not enquiry.email:
            return

        context = {
            "enquiry_id": enquiry.id,
            "name": enquiry.name,
            "email": enquiry.email,
            "phone": enquiry.phone,
            "service": enquiry.service,
            "message": enquiry.message,
            "source": enquiry.source,
        }

        client_html = render_template("enquiry_acknowledgement.html", context)
        client_plain = f"Hi {enquiry.name}, we received your enquiry."
        send_mail(enquiry.email, "We've received your message – BrainMint Software", client_html, client_plain)

    except Exception as e:
        pass
    finally:
        db.close()

def send_password_reset_email(email: str, reset_token: str):
    reset_link = f"https://your-frontend-domain.com/admin/reset-password?token={reset_token}"
    subject = "Password Reset Request - BrainMint Admin"
    html_body = f"""
    <p>Hello,</p>
    <p>You requested a password reset for your admin account. Click the link below to reset your password:</p>
    <p><a href="{reset_link}" target="_blank">Reset Password</a></p>
    <p>If you didn't request this, please ignore this email. This link expires in 15 minutes.</p>
    """
    plain_fallback = f"Reset your password by visiting this link: {reset_link}"
    
    try:
        send_mail(email, subject, html_body, plain_fallback)
    except Exception as e:
        pass

class EmailService:
    def send_enquiry_notification(self, enquiry_id: int):
        return send_enquiry_notification(enquiry_id)

    def send_enquiry_acknowledgement(self, enquiry_id: int):
        return send_enquiry_acknowledgement(enquiry_id)

    def send_password_reset_email(self, email: str, reset_token: str):
        return send_password_reset_email(email, reset_token)
    
    def __call__(self, enquiry_id: int):
        email_error = None
        try:
            self.send_enquiry_notification(enquiry_id)
            self.send_enquiry_acknowledgement(enquiry_id)
        except Exception as e:
            email_error = str(e)

        db = SessionLocal()
        try:
            enquiry = db.query(Enquiry).filter(Enquiry.id == enquiry_id).first()
            if enquiry:
                if email_error:
                    enquiry.email_status = EmailStatus.failed
                    enquiry.email_error = email_error
                else:
                    enquiry.email_status = EmailStatus.sent
                    enquiry.email_error = None
                db.commit()
        except Exception:
            db.rollback()
        finally:
            db.close()

email_service = EmailService()