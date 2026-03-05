import sqlite3
from collections.abc import Generator
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from config import DB_PATH, BASE_DIR
from db import get_conn

TEMPLATES_DIR = BASE_DIR / "templates"


def get_db() -> Generator[sqlite3.Connection,]:
    """Get database connection as FastAPI dependency."""
    conn = get_conn()
    try:
        yield conn
    finally:
        conn.close()


GetDb = Annotated[
    sqlite3.Connection,
    Depends(get_db),
]


app = FastAPI(
    title="App w/ SQL-Injection",
)
templates = Jinja2Templates(
    directory=TEMPLATES_DIR,
)


@app.get("/", response_class=HTMLResponse)
def articles_list_get(
    request: Request,
    db: GetDb,
    title: str = "",
    order: Literal["ASC", "DESC"] = "DESC",
):
    # VULNERABLE CODE - SQL Injection here!

    ordering = f"ORDER BY created_at {order}"
    if title:
        query = "SELECT * FROM articles WHERE title LIKE ? " + ordering
        params = (f"%{title}%",)
        articles = db.execute(query, params).fetchall()
    else:
        articles = db.execute("SELECT * FROM articles " + ordering).fetchall()

    return templates.TemplateResponse(
        "articles.html",
        {
            "request": request,
            "articles": articles,
            "search_title": title,
            "order_by": order,
        },
    )
