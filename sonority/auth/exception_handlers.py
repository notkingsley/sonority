from fastapi import status
from fastapi.responses import JSONResponse

from sonority.auth.exceptions import (
    AuthenticationError,
    PasswordChangeError,
    RegistrationError,
    UserUpdateError,
)


async def auth_exception_handler(request, exc: AuthenticationError):
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"detail": "Incorrect username or password"},
        headers={"WWW-Authenticate": "Bearer"},
    )


async def registration_exception_handler(request, exc: RegistrationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.args[0]},
    )


async def password_change_exception_handler(request, exc: PasswordChangeError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.args[0]},
    )


async def user_update_exception_handler(request, exc: UserUpdateError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": exc.args[0]},
    )


exception_handlers = {
    AuthenticationError: auth_exception_handler,
    RegistrationError: registration_exception_handler,
    PasswordChangeError: password_change_exception_handler,
    UserUpdateError: user_update_exception_handler,
}
