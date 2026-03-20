from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
import bcrypt as _bcrypt

from database import get_db
from models import Partner, PartnerStatus
import repositories.internal_user as user_repo
import repositories.partner as partner_repo

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="templates")


def _verify_password(plain: str, hashed: str) -> bool:
    return _bcrypt.checkpw(plain.encode(), hashed.encode())


def get_current_user_id(request: Request) -> str | None:
    return request.session.get("admin_user_id")


async def _get_partner_kpis(db: AsyncSession) -> dict:
    result = await db.execute(
        select(Partner.status, func.count(Partner.id).label("n")).group_by(Partner.status)
    )
    counts = {row.status: row.n for row in result.all()}
    total = sum(counts.values())
    return {
        "total": total,
        "active": counts.get(PartnerStatus.Active, 0),
        "inactive": counts.get(PartnerStatus.Inactive, 0),
        "pending_review": counts.get(PartnerStatus.PendingReview, 0),
        "suspended": counts.get(PartnerStatus.Suspended, 0),
        "rejected": counts.get(PartnerStatus.Rejected, 0),
    }


# ── Auth ──────────────────────────────────────────────────────────────────────

@router.get("", response_class=HTMLResponse)
async def admin_root(request: Request):
    if get_current_user_id(request):
        return RedirectResponse(url="/admin/dashboard", status_code=302)
    return RedirectResponse(url="/admin/login", status_code=302)


@router.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    if get_current_user_id(request):
        return RedirectResponse(url="/admin/dashboard", status_code=302)
    return templates.TemplateResponse(request, "admin/login.html", {"error": None})


@router.post("/login", response_class=HTMLResponse)
async def login_post(
    request: Request,
    email: str = Form(""),
    password: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    user = await user_repo.get_by_email(db, email.strip())
    if not user or not _verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            request, "admin/login.html",
            {"error": "Email o contraseña incorrectos."},
            status_code=401,
        )
    if not user.is_active:
        return templates.TemplateResponse(
            request, "admin/login.html",
            {"error": "Tu cuenta está inactiva."},
            status_code=403,
        )
    request.session["admin_user_id"] = str(user.id)
    request.session["admin_user_name"] = user.name
    return RedirectResponse(url="/admin/dashboard", status_code=302)


@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/admin/login", status_code=302)


# ── Shell ─────────────────────────────────────────────────────────────────────

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    if not get_current_user_id(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    return templates.TemplateResponse(
        request,
        "admin/dashboard.html",
        {"user_name": request.session.get("admin_user_name", "")},
    )


# ── Partners section ──────────────────────────────────────────────────────────

@router.get("/partners-section", response_class=HTMLResponse)
async def partners_section(request: Request, db: AsyncSession = Depends(get_db)):
    if not get_current_user_id(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    kpis = await _get_partner_kpis(db)
    return templates.TemplateResponse(
        request, "admin/partials/partners_section.html",
        {"kpis": kpis, "active_sub": "dashboard"},
    )


@router.get("/partners/dashboard", response_class=HTMLResponse)
async def partners_dashboard(request: Request, db: AsyncSession = Depends(get_db)):
    if not get_current_user_id(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    kpis = await _get_partner_kpis(db)
    return templates.TemplateResponse(
        request, "admin/partials/partners_dashboard.html", {"kpis": kpis}
    )


@router.get("/partners", response_class=HTMLResponse)
async def partners_list(request: Request, db: AsyncSession = Depends(get_db)):
    if not get_current_user_id(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    partners = await partner_repo.get_all(db)
    return templates.TemplateResponse(
        request, "admin/partials/partners_list.html", {"partners": partners}
    )


# ── Internal users section ────────────────────────────────────────────────────

@router.get("/internal_users", response_class=HTMLResponse)
async def internal_users_list(request: Request, db: AsyncSession = Depends(get_db)):
    if not get_current_user_id(request):
        return RedirectResponse(url="/admin/login", status_code=302)
    users = await user_repo.get_all(db)
    return templates.TemplateResponse(
        request, "admin/partials/internal_users.html", {"users": users}
    )
