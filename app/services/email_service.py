import logging
import smtplib
from email.message import EmailMessage
from email.utils import parseaddr
from pathlib import Path

import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.enquiry import Enquiry, EmailStatus

logger = logging.getLogger(__name__)

# Network calls must never hang a worker thread for long.
HTTP_TIMEOUT = 10.0
SMTP_TIMEOUT = 10


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


def _sender() -> tuple[str, str]:
    """Return (display_name, address). EMAIL_FROM may be 'Name <addr>' or just 'addr'."""
    raw = settings.EMAILS_FROM_EMAIL or settings.SMTP_USER
    name, addr = parseaddr(raw)
    return name, addr or raw


def send_mail(recipient: str, subject: str, html_body: str, plain_fallback: str):
    """Send one email through the configured provider. Raises on failure."""
    if not getattr(settings, "EMAIL_ENABLED", True):
        logger.info("EMAIL_ENABLED is false; skipping email to %s", recipient)
        return
    if not recipient:
        raise EmailDeliveryError("No recipient address configured (check EMAIL_TEAM_TO).")

    provider = getattr(settings, "EMAIL_PROVIDER", "smtp").lower()
    from_name, from_addr = _sender()

    if provider == "sendgrid":
        headers = {
            "Authorization": f"Bearer {settings.SENDGRID_API_KEY}",
            "Content-Type": "application/json",
        }
        sender = {"email": from_addr}
        if from_name:
            sender["name"] = from_name
        payload = {
            "personalizations": [{"to": [{"email": recipient}]}],
            "from": sender,
            "subject": subject,
            "content": [{"type": "text/html", "value": html_body or plain_fallback}],
        }
        response = httpx.post(
            "https://api.sendgrid.com/v3/mail/send",
            json=payload,
            headers=headers,
            timeout=HTTP_TIMEOUT,
        )
        response.raise_for_status()

    elif provider == "mailgun":
        auth = ("api", settings.MAILGUN_API_KEY)
        data = {
            "from": f"{from_name or 'BrainMint'} <{from_addr}>",
            "to": [recipient],
            "subject": subject,
            "html": html_body or plain_fallback,
        }
        response = httpx.post(
            f"https://api.mailgun.net/v3/{settings.MAILGUN_DOMAIN}/messages",
            data=data,
            auth=auth,
            timeout=HTTP_TIMEOUT,
        )
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

        with smtp_cls(settings.SMTP_HOST, settings.SMTP_PORT, timeout=SMTP_TIMEOUT) as server:
            if not use_ssl and getattr(settings, "SMTP_USE_TLS", True):
                server.starttls()
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)


def _load_enquiry_data(enquiry_id: int) -> dict | None:
    """Read what we need from the DB and release the connection immediately."""
    db: Session = SessionLocal()
    try:
        enquiry = db.query(Enquiry).filter(Enquiry.id == enquiry_id).first()
        if not enquiry:
            return None
        source = getattr(enquiry.source, "value", enquiry.source)
        return {
            "enquiry_id": enquiry.id,
            "name": enquiry.name,
            "email": enquiry.email,
            "phone": enquiry.phone,
            "service": enquiry.service,
            "message": enquiry.message,
            "source": source,
        }
    finally:
        db.close()


def _set_email_status(enquiry_id: int, status: EmailStatus, error: str | None = None):
    """Short-lived session used only to save the delivery result."""
    db: Session = SessionLocal()
    try:
        enquiry = db.query(Enquiry).filter(Enquiry.id == enquiry_id).first()
        if enquiry:
            enquiry.email_status = status
            enquiry.email_error = error[:1000] if error else None
            db.commit()
    except Exception:
        db.rollback()
        logger.exception("Could not save email status for enquiry #%s", enquiry_id)
    finally:
        db.close()


def send_enquiry_notification(enquiry_id: int):
    """Email the enquiry to the company inbox and record sent/failed on the enquiry."""
    if not getattr(settings, "EMAIL_ENABLED", True):
        logger.info("EMAIL_ENABLED is false; not emailing enquiry #%s", enquiry_id)
        return

    # 1. Read data, release the DB connection BEFORE any network call.
    ctx = _load_enquiry_data(enquiry_id)
    if ctx is None:
        return

    # 2. Network call with no DB connection held.
    try:
        company_html = render_template("enquiry_notification.html", ctx)
        company_plain = (
            f"New enquiry received via {ctx['source']}:\n\n"
            f"Name: {ctx['name']}\nEmail: {ctx['email']}\n"
            f"Phone: {ctx['phone'] or 'N/A'}\nService: {ctx['service'] or 'N/A'}\n\n"
            f"{ctx['message']}"
        )
        send_mail(
            settings.EMAILS_TO_EMAIL,
            f"New Enquiry from {ctx['name']}",
            company_html,
            company_plain,
        )
    except Exception as e:
        logger.error("Email delivery failed for enquiry #%s: %s", enquiry_id, e)
        _set_email_status(enquiry_id, EmailStatus.failed, str(e))
        raise EmailDeliveryError(str(e)) from e

    # 3. Short session just to save the result.
    _set_email_status(enquiry_id, EmailStatus.sent)


def send_enquiry_acknowledgement(enquiry_id: int):
    """Email a confirmation to the client. A failure here is logged but never fails the enquiry."""
    if not getattr(settings, "EMAIL_ENABLED", True):
        return
    ctx = _load_enquiry_data(enquiry_id)
    if ctx is None or not ctx["email"]:
        return
    try:
        client_html = render_template("enquiry_acknowledgement.html", ctx)
        client_plain = f"Hi {ctx['name']}, we received your enquiry and will get back to you shortly."
        send_mail(
            ctx["email"],
            "We've received your message – BrainMint Software",
            client_html,
            client_plain,
        )
    except Exception:
        logger.exception("Acknowledgement email failed for enquiry #%s", enquiry_id)


def send_password_reset_email(email: str, reset_token: str):
    frontend = getattr(settings, "FRONTEND_URL", None) or settings.SITE_URL
    reset_link = f"{frontend.rstrip('/')}/admin/reset-password?token={reset_token}"
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
    except Exception:
        logger.exception("Password reset email failed")


class EmailService:
    def send_enquiry_notification(self, enquiry_id: int):
        return send_enquiry_notification(enquiry_id)

    def send_enquiry_acknowledgement(self, enquiry_id: int):
        return send_enquiry_acknowledgement(enquiry_id)

    def send_password_reset_email(self, email: str, reset_token: str):
        return send_password_reset_email(email, reset_token)

    def __call__(self, enquiry_id: int):
        """Background task entry point: notify the company, then acknowledge the client."""
        email_error = None
        try:
            self.send_enquiry_notification(enquiry_id)
        except Exception as e:
            email_error = str(e)
            logger.exception("Notification email failed for enquiry #%s", enquiry_id)

        # The acknowledgement is best-effort and never changes the enquiry's email status.
        try:
            self.send_enquiry_acknowledgement(enquiry_id)
        except Exception:
            logger.exception("Acknowledgement email failed for enquiry #%s", enquiry_id)

        if getattr(settings, "EMAIL_ENABLED", True):
            if email_error:
                _set_email_status(enquiry_id, EmailStatus.failed, email_error)
            else:
                _set_email_status(enquiry_id, EmailStatus.sent)


email_service = EmailService()
