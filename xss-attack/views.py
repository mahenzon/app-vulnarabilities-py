import re
from typing import Annotated

from fastapi import APIRouter, Request, Form, status
from fastapi.responses import RedirectResponse

from templating import templates
from db import GetDB

router = APIRouter(
    prefix="/guestbook",
    tags=["guestbook"],
)


REPLACE_GUESTBOOK = re.compile("(guestbook)", re.IGNORECASE)


@router.get("/", name="guestbook.index")
def index(
    request: Request,
    db: GetDB,
):
    rows = db.execute(
        "SELECT message, created_at FROM messages ORDER BY created_at DESC"
    ).fetchall()
    messages_for_render = []
    current_number = len(rows)
    for row in rows:
        text = REPLACE_GUESTBOOK.sub(r"<b>\1</b>", row["message"])
        messages_for_render.append(
            {
                "number": current_number,
                "text": text,
                "created_at": row["created_at"],
            }
        )
        current_number -= 1
    return templates.TemplateResponse(
        request=request,
        name="guestbook/index.html",
        context={
            "messages_for_render": messages_for_render,
        },
    )


@router.get("/add/", name="guestbook.add_form")
def add_message_form(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="guestbook/add.html",
    )


@router.post("/add/", name="guestbook.add_message")
def add_message(
    request: Request,
    message: Annotated[str, Form(...)],
    db: GetDB,
):
    db.execute(
        "INSERT INTO messages (message, created_at) VALUES (?, datetime('now'))",
        (message,),
    )
    db.commit()
    return RedirectResponse(
        url=request.url_for("guestbook.index"),
        status_code=status.HTTP_303_SEE_OTHER,
    )
