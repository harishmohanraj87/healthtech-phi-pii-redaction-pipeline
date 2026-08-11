from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.routes import router

app = FastAPI(
    title="HealthTech PHI/PII Redaction Pipeline",
    version="0.1.0"
)

# AdminLTE static files
app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)

# Jinja2 templates
templates = Jinja2Templates(directory="app/templates")

# Existing API routes
app.include_router(router)


# =========================
# FRONTEND ROUTES
# =========================

@app.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={"request": request}
    )


@app.get("/redact-ui")
async def redact_ui(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="redact.html",
        context={"request": request}
    )