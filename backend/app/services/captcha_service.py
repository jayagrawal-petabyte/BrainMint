"""
CAPTCHA verification service.

Supports hCaptcha (default) and Google reCAPTCHA v2/v3.
Set CAPTCHA_PROVIDER in .env to "recaptcha" to switch providers.
Set CAPTCHA_ENABLED=false to bypass verification in local dev / tests.
"""

import logging
from typing import Literal

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

HCAPTCHA_VERIFY_URL = "https://hcaptcha.com/siteverify"
RECAPTCHA_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"


class CaptchaVerificationError(Exception):
    """Raised when a CAPTCHA token fails server-side verification."""


class CaptchaService:
    def __init__(self):
        self.enabled: bool = getattr(settings, "CAPTCHA_ENABLED", True)
        self.provider: Literal["hcaptcha", "recaptcha"] = getattr(
            settings, "CAPTCHA_PROVIDER", "hcaptcha"
        )
        self.secret: str = getattr(settings, "CAPTCHA_SECRET_KEY", "")
        self.min_score: float = float(getattr(settings, "RECAPTCHA_MIN_SCORE", 0.5))

    def verify(self, token: str, ip: str | None = None) -> None:
        """
        Verify a CAPTCHA token with the provider's siteverify endpoint.

        Raises
        ------
        CaptchaVerificationError
            If the token is invalid, expired, or scores below threshold.
        """
        if not self.enabled:
            logger.debug("CAPTCHA verification disabled – skipping.")
            return

        if not self.secret:
            logger.warning(
                "CAPTCHA_SECRET_KEY not set; skipping verification. "
                "Set CAPTCHA_ENABLED=false to silence this warning."
            )
            return

        if self.provider == "recaptcha":
            self._verify_recaptcha(token, ip)
        else:
            self._verify_hcaptcha(token, ip)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _verify_hcaptcha(self, token: str, ip: str | None) -> None:
        payload: dict = {"secret": self.secret, "response": token}
        if ip:
            payload["remoteip"] = ip
        try:
            resp = httpx.post(HCAPTCHA_VERIFY_URL, data=payload, timeout=5.0)
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            logger.error("hCaptcha network error: %s", exc)
            # Fail open so a network blip doesn't block real users.
            return

        if not data.get("success"):
            error_codes = data.get("error-codes", [])
            logger.warning("hCaptcha failed: %s", error_codes)
            raise CaptchaVerificationError(
                f"CAPTCHA verification failed: {', '.join(error_codes)}"
            )

    def _verify_recaptcha(self, token: str, ip: str | None) -> None:
        payload: dict = {"secret": self.secret, "response": token}
        if ip:
            payload["remoteip"] = ip
        try:
            resp = httpx.post(RECAPTCHA_VERIFY_URL, data=payload, timeout=5.0)
            resp.raise_for_status()
            data = resp.json()
        except Exception as exc:
            logger.error("reCAPTCHA network error: %s", exc)
            return

        if not data.get("success"):
            error_codes = data.get("error-codes", [])
            logger.warning("reCAPTCHA failed: %s", error_codes)
            raise CaptchaVerificationError(
                f"CAPTCHA verification failed: {', '.join(error_codes)}"
            )

        # v3 score check
        score = data.get("score")
        if score is not None and score < self.min_score:
            logger.warning("reCAPTCHA score too low: %.2f", score)
            raise CaptchaVerificationError(
                f"CAPTCHA score {score:.2f} is below the minimum threshold {self.min_score}."
            )


captcha_service = CaptchaService()
