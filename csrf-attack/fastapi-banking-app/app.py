"""
FastAPI CSRF Vulnerability Example

This example demonstrates a CSRF vulnerability in a FastAPI application.
The /send endpoint does not have CSRF protection, making it vulnerable to CSRF attacks.
"""

import secrets
from datetime import datetime
from pathlib import Path
from typing import Annotated, Literal

from fastapi import FastAPI, Request, Form, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from fastapi_csrf_protect import CsrfProtect
from fastapi_csrf_protect.exceptions import CsrfProtectError
from pydantic_settings import BaseSettings
from starlette.responses import JSONResponse

from models import User, PaymentForm, LoginForm, Payment, UserInfo
from db import get_db


class CsrfSettings(BaseSettings):
    secret_key: str = "Jij30i4qmWhOGnSxNvbKb4cPFpsDsIOKk8bKt_oHXgo"
    cookie_secure: bool = True
    # cookie_samesite: str = "none"
    cookie_samesite: str = "lax"
    token_location: Literal["body", "header"] = "body"
    token_key: str = "csrf_secret_token"


@CsrfProtect.load_config
def get_csrf_config():
    return CsrfSettings()


# FastAPI app
app = FastAPI(title="CSRF Vulnerable Payment System")

# Templates
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


# Session management (simple cookie-based for demo purposes)
SESSIONS = {}


@app.exception_handler(CsrfProtectError)
def csrf_protect_exception_handler(request: Request, exc: CsrfProtectError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


def get_current_user(request: Request) -> User | None:
    """Get current user from session cookie"""
    session_id = request.cookies.get("session_id")
    if not session_id or session_id not in SESSIONS:
        return None

    user_id = SESSIONS[session_id]
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user_row = cursor.fetchone()
    conn.close()

    if user_row:
        return User(
            id=user_row["id"],
            username=user_row["username"],
            password=user_row["password"],
            balance=user_row["balance"],
        )
    return None


class LoginRequiredError(Exception):
    pass


def require_login(user: User | None = Depends(get_current_user)) -> User:
    """Dependency that requires user to be logged in"""
    if user is None:
        raise LoginRequiredError
    return user


UserRequired = Annotated[
    User,
    Depends(require_login),
]


@app.exception_handler(LoginRequiredError)
def login_exception_handler(
    request: Request, exc: LoginRequiredError
) -> RedirectResponse:
    response = RedirectResponse(
        url=request.url_for("login"),
        status_code=status.HTTP_302_FOUND,
    )
    response.delete_cookie("session_id")
    return response


@app.get("/", response_class=HTMLResponse)
def home(request: Request, user: UserRequired):
    """Homepage showing user payments"""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT p.id
             , p.amount
             , p.created_at
             , u_from.username as from_username
             , u_to.username as to_username
        FROM payments as p
        JOIN users as u_from ON p.from_user_id = u_from.id
        JOIN users as u_to ON p.to_user_id = u_to.id
        WHERE p.from_user_id = ? OR p.to_user_id = ?
        ORDER BY p.created_at DESC
    """,
        (user.id, user.id),
    )

    payments = [
        Payment(
            id=row["id"],
            amount=row["amount"],
            created_at=row["created_at"],
            from_username=row["from_username"],
            to_username=row["to_username"],
        )
        for row in cursor.fetchall()
    ]
    conn.close()

    return templates.TemplateResponse(
        request=request,
        name="payments_list.html",
        context={
            "request": request,
            "user": user,
            "payments": payments,
        },
    )


def render_send_money_view(
    request: Request,
    user: User,
    message: str = "",
    message_class: str = "",
) -> HTMLResponse:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username FROM users WHERE id != ?",
        (user.id,),
    )
    users = [
        UserInfo(
            id=row["id"],
            username=row["username"],
        )
        for row in cursor.fetchall()
    ]
    conn.close()

    return templates.TemplateResponse(
        request=request,
        name="send_money.html",
        context={
            "request": request,
            "user": user,
            "users": users,
            "message": message,
            "message_class": message_class,
        },
    )


@app.get("/send", response_class=HTMLResponse)
def send_money_get(
    request: Request,
    user: UserRequired,
):
    return render_send_money_view(
        request=request,
        user=user,
    )


@app.post("/send")
def send_money_post(
    request: Request,
    user: UserRequired,
    payment_data: PaymentForm = Form(),
):
    """
    VULNERABLE ENDPOINT - No CSRF protection!
    This endpoint accepts POST requests without any CSRF token validation.
    """
    # Validate business rules
    if user.balance < payment_data.amount:
        message = "Not enough money on balance"
        message_class = "error"
    elif payment_data.to_user_id == user.id:
        message = "You cannot send payment to yourself"
        message_class = "error"
    else:
        # Perform the transaction
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE users SET balance = balance - ? WHERE id = ?",
            (payment_data.amount, user.id),
        )
        cursor.execute(
            "UPDATE users SET balance = balance + ? WHERE id = ?",
            (payment_data.amount, payment_data.to_user_id),
        )
        cursor.execute(
            "INSERT INTO payments (from_user_id, to_user_id, amount, created_at) VALUES (?, ?, ?, ?)",
            (
                user.id,
                payment_data.to_user_id,
                payment_data.amount,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )

        conn.commit()
        conn.close()

        message = "Successfully sent payment!"
        message_class = "success"

    # Show error message on form
    return render_send_money_view(
        request=request,
        user=user,
        message=message,
        message_class=message_class,
    )


@app.get(
    "/login",
    response_class=HTMLResponse,
    name="login",
)
def login_get(request: Request):
    """Login page"""
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={
            "request": request,
        },
    )


@app.post("/login")
def login_post(request: Request, login_data: LoginForm = Form()):
    """Login handler"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id FROM users WHERE username = ? AND password = ?",
        (login_data.username, login_data.password),
    )
    user = cursor.fetchone()
    conn.close()

    if user:
        # Create session
        session_id = secrets.token_urlsafe(32)
        SESSIONS[session_id] = user["id"]

        # Redirect to home with session cookie
        response = RedirectResponse(
            url="/",
            status_code=status.HTTP_303_SEE_OTHER,
        )
        response.set_cookie(
            key="session_id",
            value=session_id,
            httponly=True,
            # secure=False,
            secure=True,
            samesite="none",
        )
        return response
    else:
        message = "Invalid username or password"
        message_class = "error"
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "request": request,
                "message": message,
                "message_class": message_class,
            },
        )


@app.get("/logout")
def logout(request: Request):
    """Logout handler"""
    session_id = request.cookies.get("session_id")
    if session_id:
        SESSIONS.pop(session_id, None)

    response = RedirectResponse(
        url="/login",
        status_code=status.HTTP_303_SEE_OTHER,
    )
    response.delete_cookie(key="session_id")
    return response
