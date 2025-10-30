from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from app.services.auth.auth_service import verify_user


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = request.cookies.get("COWRITE_SESSION_ID")

        if not token:
            request.state.user = None
            response = await call_next(request)
            return response

        user_data = await verify_user(token)
        if not user_data:
            return JSONResponse(
                {"detail": "Invalid or expired session"}, status_code=401
            )

        request.state.user = user_data

        response = await call_next(request)
        return response
