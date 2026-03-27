import uuid

import bcrypt as _bcrypt
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models import InternalRole
import repositories.internal_user as user_repo
import repositories.partner as partner_repo
import repositories.invoice as invoice_repo
import repositories.reward as reward_repo

router = APIRouter(prefix="/sales", tags=["sales-portal"])
templates = Jinja2Templates(directory="templates")


def _verify_password(plain: str, hashed: str) -> bool:
    return _bcrypt.checkpw(plain.encode(), hashed.encode())


def get_current_sales_user_id(request: Request) -> str | None:
    return request.session.get("sales_user_id")


# ── Auth ───────────────────────────────────────────────────────────────────────

@router.get("", response_class=HTMLResponse)
async def sales_root(request: Request):
    if get_current_sales_user_id(request):
        return RedirectResponse(url="/sales/dashboard", status_code=302)
    return RedirectResponse(url="/sales/login", status_code=302)


@router.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    if get_current_sales_user_id(request):
        return RedirectResponse(url="/sales/dashboard", status_code=302)
    return templates.TemplateResponse(request, "sales/login.html", {"error": None})


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
            request, "sales/login.html",
            {"error": "Email o contraseña incorrectos."},
            status_code=401,
        )
    if not user.is_active:
        return templates.TemplateResponse(
            request, "sales/login.html",
            {"error": "Tu cuenta está inactiva."},
            status_code=403,
        )
    if user.role != InternalRole.Sales:
        return templates.TemplateResponse(
            request, "sales/login.html",
            {"error": "Acceso restringido al equipo de ventas."},
            status_code=403,
        )
    request.session["sales_user_id"] = str(user.id)
    request.session["sales_user_name"] = user.name
    return RedirectResponse(url="/sales/dashboard", status_code=302)


@router.get("/logout")
async def logout(request: Request):
    request.session.pop("sales_user_id", None)
    request.session.pop("sales_user_name", None)
    return RedirectResponse(url="/sales/login", status_code=302)


# ── Shell ──────────────────────────────────────────────────────────────────────

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: AsyncSession = Depends(get_db)):
    sales_user_id = get_current_sales_user_id(request)
    if not sales_user_id:
        return RedirectResponse(url="/sales/login", status_code=302)
    partners = await partner_repo.get_by_sales_rep(db, uuid.UUID(sales_user_id))
    partners_sorted = sorted(partners, key=lambda p: p.name)
    return templates.TemplateResponse(
        request,
        "sales/dashboard.html",
        {
            "user_name": request.session.get("sales_user_name", ""),
            "partners": partners_sorted,
        },
    )


# ── Partials ───────────────────────────────────────────────────────────────────

@router.get("/section", response_class=HTMLResponse)
async def sales_section(request: Request, db: AsyncSession = Depends(get_db)):
    sales_user_id = get_current_sales_user_id(request)
    if not sales_user_id:
        return RedirectResponse(url="/sales/login", status_code=302)
    partners = await partner_repo.get_by_sales_rep(db, uuid.UUID(sales_user_id))
    partners_sorted = sorted(partners, key=lambda p: p.name)
    return templates.TemplateResponse(
        request, "sales/partials/sales_section.html",
        {"partners": partners_sorted},
    )


@router.get("/partners", response_class=HTMLResponse)
async def partners_list(request: Request, db: AsyncSession = Depends(get_db)):
    sales_user_id = get_current_sales_user_id(request)
    if not sales_user_id:
        return RedirectResponse(url="/sales/login", status_code=302)
    partners = await partner_repo.get_by_sales_rep(db, uuid.UUID(sales_user_id))
    partners_sorted = sorted(partners, key=lambda p: p.name)
    return templates.TemplateResponse(
        request, "sales/partials/partners.html",
        {"partners": partners_sorted},
    )


@router.get("/invoices", response_class=HTMLResponse)
async def invoices_list(request: Request, db: AsyncSession = Depends(get_db)):
    sales_user_id = get_current_sales_user_id(request)
    if not sales_user_id:
        return RedirectResponse(url="/sales/login", status_code=302)
    partners = await partner_repo.get_by_sales_rep(db, uuid.UUID(sales_user_id))
    partner_map = {str(p.id): p.name for p in partners}
    partner_ids = [p.id for p in partners]
    invoices = await invoice_repo.get_by_partners(db, partner_ids)
    invoices_sorted = sorted(invoices, key=lambda i: i.created_at, reverse=True)
    return templates.TemplateResponse(
        request, "sales/partials/invoices.html",
        {"invoices": invoices_sorted, "partner_map": partner_map},
    )


@router.get("/invoices/{invoice_id}", response_class=HTMLResponse)
async def invoice_detail(
    request: Request,
    invoice_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    sales_user_id = get_current_sales_user_id(request)
    if not sales_user_id:
        return RedirectResponse(url="/sales/login", status_code=302)
    invoice = await invoice_repo.get_by_id(db, invoice_id)
    if not invoice:
        return HTMLResponse("<p style='color:#e85454;padding:2rem;'>Factura no encontrada.</p>", status_code=404)
    # Verificar que la factura pertenece a un partner del sales rep
    partners = await partner_repo.get_by_sales_rep(db, uuid.UUID(sales_user_id))
    partner_ids = {str(p.id) for p in partners}
    if str(invoice.partner_id) not in partner_ids:
        return HTMLResponse("<p style='color:#e85454;padding:2rem;'>Sin acceso a esta factura.</p>", status_code=403)
    rewards = await reward_repo.get_by_invoice(db, invoice_id)
    rewards_sorted = sorted(rewards, key=lambda r: r.transaction_date, reverse=True)
    return templates.TemplateResponse(
        request, "partners/partials/invoice_detail.html",
        {
            "invoice": invoice,
            "rewards": rewards_sorted,
            "back_url": "/sales/invoices",
            "back_target": "#sales-main",
        },
    )


@router.get("/partners/{partner_id}/detail", response_class=HTMLResponse)
async def partner_detail(
    request: Request,
    partner_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    sales_user_id = get_current_sales_user_id(request)
    if not sales_user_id:
        return RedirectResponse(url="/sales/login", status_code=302)

    partner = await partner_repo.get_by_id(db, partner_id)
    if not partner or str(partner.assigned_sales_rep_id) != sales_user_id:
        return HTMLResponse(
            "<p style='color:#e85454;padding:2rem;'>Partner no encontrado o sin acceso.</p>",
            status_code=404,
        )
    invoices = await invoice_repo.get_by_partner(db, partner_id)
    invoices_sorted = sorted(invoices, key=lambda i: i.created_at, reverse=True)
    rewards = await reward_repo.get_by_partner(db, partner_id)
    rewards_sorted = sorted(rewards, key=lambda r: r.transaction_date, reverse=True)
    return templates.TemplateResponse(
        request, "sales/partials/partner_detail.html",
        {"partner": partner, "invoices": invoices_sorted, "rewards": rewards_sorted},
    )

