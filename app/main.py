from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.routes import router


app = FastAPI(
    title="HealthTech PHI/PII Redaction Pipeline",
    version="0.1.0"
)


# =========================================================
# STATIC FILES
# =========================================================

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)


# =========================================================
# TEMPLATES
# =========================================================

templates = Jinja2Templates(
    directory="app/templates"
)


# =========================================================
# API ROUTES
# =========================================================

app.include_router(router)


# =========================================================
# FRONTEND ROUTES
# =========================================================

@app.get("/dashboard")
async def dashboard(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "request": request,
            "active_page": "dashboard"
        }
    )


@app.get("/redact-ui")
async def redact_ui(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="redact.html",
        context={
            "request": request,
            "active_page": "redact"
        }
    )


@app.get("/restore-ui")
async def restore_ui(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="restore.html",
        context={
            "request": request,
            "active_page": "restore"
        }
    )