import smtplib
from pathlib import Path
from email.message import EmailMessage
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.enquiry import Enquiry, EmailStatus

class EmailDeliveryError(Exception):
    """Custom exception raised when email delivery fails."""
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

        use_ssl = getattr(settings, "SMTP_SSL", False)
        smtp_cls = smtplib.SMTP_SSL if use_ssl else smtplib.SMTP

        def send_mail(recipient: str, subject: str, html_body: str, plain_fallback: str):
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

        company_html = render_template("enquiry_notification.html", context)
        company_plain = f"New enquiry received via {enquiry.source}:\n\nName: {enquiry.name}\nEmail: {enquiry.email}"
        send_mail(settings.EMAILS_TO_EMAIL, f"New Enquiry from {enquiry.name}", company_html, company_plain)

        if enquiry.email:
            client_html = render_template("enquiry_acknowledge.html", context)
            client_plain = f"Hi {enquiry.name}, we received your enquiry."
            send_mail(enquiry.email, "We've received your message – BrainMint Software", client_html, client_plain)

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

class EmailService:
    def send_enquiry_notification(self, enquiry_id: int):
        return send_enquiry_notification(enquiry_id)

    def send_enquiry_acknowledgement(self, enquiry_id: int):
        pass
    
    def __call__(self, enquiry_id: int):
        return send_enquiry_notification(enquiry_id)

email_service = EmailService()