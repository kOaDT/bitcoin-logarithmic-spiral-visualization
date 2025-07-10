from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.datastructures import MutableHeaders

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        headers = MutableHeaders(response.headers)
        headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
            "font-src 'self' https://fonts.gstatic.com; "
            "script-src 'self' 'unsafe-inline'; " # 'unsafe-inline' is required for Plotly charts
            "img-src 'self' data:; "
            "object-src 'none'; "
            "frame-ancestors 'none'; "
            "base-uri 'self';"
        )
        headers["X-Content-Type-Options"] = "nosniff"
        headers["X-Frame-Options"] = "DENY"
        headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers.update(headers)
        return response 