import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)

_CODES = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
    422: "VALIDATION_ERROR",
    429: "RATE_LIMITED",
}


def error_response(status_code: int, code: str, message: str, details=None, headers=None):
    return JSONResponse(
        status_code=status_code,
        content={"success": False, "error": {"code": code, "message": message, "details": details}},
        headers=headers,
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        # Endpoints that already built the envelope (e.g. the rate limiter) pass through.
        if isinstance(exc.detail, dict) and ("error" in exc.detail or "success" in exc.detail):
            return JSONResponse(status_code=exc.status_code, content=exc.detail, headers=exc.headers)
        if exc.status_code == 404 and exc.detail == "Not Found":
            message = f"The requested resource '{request.url.path}' does not exist on this server."
        else:
            message = str(exc.detail)
        code = _CODES.get(exc.status_code, "HTTP_ERROR")
        return error_response(exc.status_code, code, message, headers=exc.headers)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        details = [
            {
                "field": ".".join(str(p) for p in err["loc"] if p != "body") or "body",
                "message": err["msg"],
            }
            for err in exc.errors()
        ]
        return error_response(422, "VALIDATION_ERROR", "One or more fields failed validation.", details)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return error_response(500, "INTERNAL_ERROR", "Something went wrong. Please try again later.")