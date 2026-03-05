import re

from fastapi.templating import Jinja2Templates
from markupsafe import escape, Markup

from config import BASE_DIR

templates = Jinja2Templates(directory=BASE_DIR / "templates")


REPLACE_GUESTBOOK = re.compile("(guestbook)", re.IGNORECASE)


def highlight_guestbook(text: str) -> Markup:
    if not text:
        return Markup("")

    safe_text = escape(text)
    safe_text = REPLACE_GUESTBOOK.sub(r"<b>\1</b>", safe_text)
    return Markup(safe_text)


templates.env.filters["highlight_guestbook"] = highlight_guestbook
