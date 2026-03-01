from fastapi import FastAPI, status, Request
from fastapi.responses import RedirectResponse

from views import router as guestbook_router

app = FastAPI(title="XSS Attack demo")
app.include_router(guestbook_router)


@app.get(
    "/",
    status_code=status.HTTP_303_SEE_OTHER,
)
def index(request: Request):
    return RedirectResponse(
        url=request.url_for("guestbook.index"),
    )
