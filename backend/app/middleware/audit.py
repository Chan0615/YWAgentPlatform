import json
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from sqlalchemy import select

from app.core.database import async_session_maker
from app.core.security import decode_token
from app.models.audit_log import AuditLog
from app.models.user import User


class AuditMiddleware(BaseHTTPMiddleware):
    """
    Middleware that logs all non-GET API requests to the audit_log table.
    Captures: user, action (HTTP method + path), IP, user agent, result status.
    """

    # Paths to skip logging (health checks, docs, etc.)
    SKIP_PATHS = {"/docs", "/redoc", "/openapi.json", "/health"}

    async def dispatch(self, request: Request, call_next) -> Response:
        # Only log non-GET requests to API paths
        if request.method == "GET" or not request.url.path.startswith("/api/"):
            return await call_next(request)

        # Skip certain paths
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)

        # Extract user info from token
        user_id: Optional[int] = None
        username: Optional[str] = None

        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
            payload = decode_token(token)
            if payload and payload.get("type") == "access":
                user_id = int(payload.get("sub", 0)) or None

        # Get IP and user agent
        ip_address = request.headers.get("X-Forwarded-For", request.client.host if request.client else "unknown")
        # Take first IP if multiple in X-Forwarded-For
        if "," in ip_address:
            ip_address = ip_address.split(",")[0].strip()

        user_agent = request.headers.get("User-Agent", "")[:512]

        # Determine action from method + path
        method = request.method
        path = request.url.path

        # Determine resource type from path
        resource_type = self._extract_resource_type(path)
        action = self._determine_action(method, path)

        # Call the next middleware/handler
        response = await call_next(request)

        # Determine status
        log_status = "success" if response.status_code < 400 else "fail"

        # Resolve username if we have user_id
        if user_id:
            try:
                async with async_session_maker() as session:
                    result = await session.execute(select(User.username).where(User.id == user_id))
                    row = result.scalar_one_or_none()
                    if row:
                        username = row
            except Exception:
                pass

        # Write audit log
        try:
            async with async_session_maker() as session:
                log_entry = AuditLog(
                    user_id=user_id,
                    username=username,
                    action=action,
                    resource_type=resource_type,
                    resource_id=self._extract_resource_id(path),
                    detail=json.dumps({"method": method, "path": path, "status_code": response.status_code}),
                    ip_address=ip_address,
                    user_agent=user_agent,
                    status=log_status,
                )
                session.add(log_entry)
                await session.commit()
        except Exception:
            # Audit logging should never break the request
            pass

        return response

    def _extract_resource_type(self, path: str) -> str:
        """Extract resource type from URL path."""
        parts = path.replace("/api/v1/", "").replace("/api/", "").strip("/").split("/")
        if parts:
            return parts[0]
        return "unknown"

    def _determine_action(self, method: str, path: str) -> str:
        """Determine action name from HTTP method."""
        action_map = {
            "POST": "create",
            "PUT": "update",
            "PATCH": "update",
            "DELETE": "delete",
        }
        base_action = action_map.get(method, method.lower())

        # Special cases
        if "login" in path:
            return "login"
        if "logout" in path:
            return "logout"
        if "refresh" in path:
            return "refresh_token"
        if "permissions" in path and method == "POST" and "/roles/" in path:
            return "assign_permissions"

        return base_action

    def _extract_resource_id(self, path: str) -> Optional[str]:
        """Try to extract a resource ID from the URL path."""
        parts = path.strip("/").split("/")
        # Look for numeric segments
        for part in reversed(parts):
            if part.isdigit():
                return part
        return None
