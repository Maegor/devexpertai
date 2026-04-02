import uuid
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path

import bcrypt as _bcrypt
from fastapi import APIRouter, Request, Form, Depends, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
import repositories.partner as partner_repo
import repositories.invoice as invoice_repo
import repositories.reward as reward_repo
import repositories.partner_deal as deal_repo
import repositories.partner_campaign as campaign_repo
from models import InvoiceType, RewardStatus, PartnerDealStatus
from schemas.invoice import InvoiceCreate, InvoiceUpdate

INVOICES_BASE = Path("/opt/devexpertai/invoices")

router = APIRouter(prefix="/partners", tags=["partner-portal"])
templates = Jinja2Templates(directory="templates")


def _verify_password(plain: str, hashed: str) -> bool:
    return _bcrypt.checkpw(plain.encode(), hashed.encode())


def get_current_partner_id(request: Request) -> str | None:
    return request.session.get("partner_id")


# ── Auth ───────────────────────────────────────────────────────────────────────

@router.get("", response_class=HTMLResponse)
async def portal_root(request: Request):
    if get_current_partner_id(request):
        return RedirectResponse(url="/partners/dashboard", status_code=302)
    return RedirectResponse(url="/partners/login", status_code=302)


@router.get("/login", response_class=HTMLResponse)
async def login_get(request: Request):
    if get_current_partner_id(request):
        return RedirectResponse(url="/partners/dashboard", status_code=302)
    return templates.TemplateResponse(request, "partners/login.html", {"error": None})


@router.post("/login", response_class=HTMLResponse)
async def login_post(
    request: Request,
    email: str = Form(""),
    password: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    partner = await partner_repo.get_by_email(db, email.strip())
    if not partner or not partner.password_hash:
        return templates.TemplateResponse(
            request, "partners/login.html",
            {"error": "Email o contraseña incorrectos."},
            status_code=401,
        )
    if not _verify_password(password, partner.password_hash):
        return templates.TemplateResponse(
            request, "partners/login.html",
            {"error": "Email o contraseña incorrectos."},
            status_code=401,
        )
    request.session["partner_id"] = str(partner.id)
    request.session["partner_name"] = partner.name
    return RedirectResponse(url="/partners/dashboard", status_code=302)


@router.get("/logout")
async def logout(request: Request):
    request.session.pop("partner_id", None)
    request.session.pop("partner_name", None)
    return RedirectResponse(url="/partners/login", status_code=302)


# ── Dashboard shell ────────────────────────────────────────────────────────────

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    if not get_current_partner_id(request):
        return RedirectResponse(url="/partners/login", status_code=302)
    return templates.TemplateResponse(
        request,
        "partners/dashboard.html",
        {"partner_name": request.session.get("partner_name", "")},
    )


# ── Partials ───────────────────────────────────────────────────────────────────

@router.get("/dashboard/profile", response_class=HTMLResponse)
async def profile_partial(request: Request, db: AsyncSession = Depends(get_db)):
    partner_id = get_current_partner_id(request)
    if not partner_id:
        return RedirectResponse(url="/partners/login", status_code=302)
    partner = await partner_repo.get_by_id(db, uuid.UUID(partner_id))
    return templates.TemplateResponse(
        request, "partners/partials/profile.html", {"partner": partner}
    )


@router.get("/dashboard/invoices", response_class=HTMLResponse)
async def invoices_partial(request: Request, db: AsyncSession = Depends(get_db)):
    partner_id = get_current_partner_id(request)
    if not partner_id:
        return RedirectResponse(url="/partners/login", status_code=302)
    invoices = await invoice_repo.get_by_partner(db, uuid.UUID(partner_id))
    invoices_sorted = sorted(invoices, key=lambda i: i.created_at, reverse=True)
    return templates.TemplateResponse(
        request, "partners/partials/invoices.html", {"invoices": invoices_sorted}
    )


@router.get("/dashboard/rewards", response_class=HTMLResponse)
async def rewards_partial(request: Request, db: AsyncSession = Depends(get_db)):
    partner_id = get_current_partner_id(request)
    if not partner_id:
        return RedirectResponse(url="/partners/login", status_code=302)
    rewards = await reward_repo.get_by_partner(db, uuid.UUID(partner_id))
    rewards_sorted = sorted(rewards, key=lambda r: r.transaction_date, reverse=True)

    def _kpi(status):
        items = [r for r in rewards if r.status == status]
        return {
            "count": len(items),
            "total": sum((r.amount for r in items), Decimal("0")),
        }

    kpis = {
        "paid":     _kpi(RewardStatus.Paid),
        "pending":  _kpi(RewardStatus.Pending),
        "rejected": _kpi(RewardStatus.Rejected),
    }

    return templates.TemplateResponse(
        request, "partners/partials/rewards.html",
        {"rewards": rewards_sorted, "kpis": kpis},
    )


@router.get("/dashboard/invoices/new", response_class=HTMLResponse)
async def invoice_form_get(request: Request):
    partner_id = get_current_partner_id(request)
    if not partner_id:
        return RedirectResponse(url="/partners/login", status_code=302)
    return templates.TemplateResponse(
        request, "partners/partials/invoice_form.html", {"error": None}
    )


@router.post("/dashboard/invoices/new", response_class=HTMLResponse)
async def invoice_form_post(
    request: Request,
    invoice_type: str = Form(...),
    invoice_reference: str = Form(...),
    period_from: str = Form(...),
    period_to: str = Form(...),
    currency: str = Form(...),
    net_amount: str = Form(...),
    vat_amount: str = Form(""),
    pdf_file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    partner_id = get_current_partner_id(request)
    if not partner_id:
        return RedirectResponse(url="/partners/login", status_code=302)

    def _render_form(error: str):
        return templates.TemplateResponse(
            request, "partners/partials/invoice_form.html", {"error": error}
        )

    if not pdf_file.filename or not pdf_file.filename.lower().endswith(".pdf"):
        return _render_form("Only PDF files are accepted.")

    try:
        p_from = date.fromisoformat(period_from)
        p_to   = date.fromisoformat(period_to)
    except ValueError:
        return _render_form("Invalid period dates.")
    if p_from > p_to:
        return _render_form("Period start must be before or equal to end date.")

    try:
        net = Decimal(net_amount)
    except InvalidOperation:
        return _render_form("Invalid net amount.")

    vat: Decimal | None = None
    if vat_amount.strip():
        try:
            vat = Decimal(vat_amount)
        except InvalidOperation:
            return _render_form("Invalid VAT amount.")

    gross = net + (vat or Decimal("0"))

    try:
        inv_type = InvoiceType(invoice_type)
    except ValueError:
        return _render_form("Invalid invoice type.")

    # Create invoice first to get the DB-generated ID
    data = InvoiceCreate(
        partner_id=uuid.UUID(partner_id),
        invoice_type=inv_type,
        invoice_reference=invoice_reference.strip(),
        period_from=p_from,
        period_to=p_to,
        currency=currency.strip(),
        net_amount=net,
        vat_amount=vat,
        gross_total=gross,
        pdf_path="",
    )
    invoice = await invoice_repo.create(db, data)

    # Save PDF: /opt/devexpertai/invoices/<partner_id>/<invoice_id><filename>
    dest_dir = INVOICES_BASE / partner_id
    dest_dir.mkdir(parents=True, exist_ok=True)
    safe_name = Path(pdf_file.filename).name
    dest_path = dest_dir / f"{invoice.id}{safe_name}"
    contents = await pdf_file.read()
    dest_path.write_bytes(contents)

    # Update pdf_path on the invoice record
    await invoice_repo.update(db, invoice, InvoiceUpdate(pdf_path=str(dest_path)))

    invoices = await invoice_repo.get_by_partner(db, uuid.UUID(partner_id))
    invoices_sorted = sorted(invoices, key=lambda i: i.created_at, reverse=True)
    return templates.TemplateResponse(
        request,
        "partners/partials/invoices.html",
        {"invoices": invoices_sorted, "success": "Invoice submitted successfully."},
    )


@router.get("/dashboard/invoices/{invoice_id}/pdf")
async def invoice_pdf_download(
    request: Request,
    invoice_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    partner_id = get_current_partner_id(request)
    if not partner_id:
        return RedirectResponse(url="/partners/login", status_code=302)
    invoice = await invoice_repo.get_by_id(db, invoice_id)
    if not invoice or str(invoice.partner_id) != partner_id:
        return HTMLResponse("Not found.", status_code=404)
    if not invoice.pdf_path:
        return HTMLResponse("No PDF available.", status_code=404)
    pdf_path = Path(invoice.pdf_path)
    if not pdf_path.is_file():
        return HTMLResponse("File not found on server.", status_code=404)
    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=pdf_path.name,
    )


@router.get("/dashboard/invoices/{invoice_id}", response_class=HTMLResponse)
async def invoice_detail_partial(
    request: Request,
    invoice_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    partner_id = get_current_partner_id(request)
    if not partner_id:
        return RedirectResponse(url="/partners/login", status_code=302)
    invoice = await invoice_repo.get_by_id(db, invoice_id)
    if not invoice or str(invoice.partner_id) != partner_id:
        return HTMLResponse("<p class='text-danger'>Factura no encontrada.</p>", status_code=404)
    rewards = await reward_repo.get_by_invoice(db, invoice_id)
    rewards_sorted = sorted(rewards, key=lambda r: r.transaction_date, reverse=True)
    return templates.TemplateResponse(
        request, "partners/partials/invoice_detail.html",
        {"invoice": invoice, "rewards": rewards_sorted}
    )


# ── Deals ─────────────────────────────────────────────────────────────────────

@router.get("/dashboard/deals", response_class=HTMLResponse)
async def deals_partial(request: Request, db: AsyncSession = Depends(get_db)):
    partner_id = get_current_partner_id(request)
    if not partner_id:
        return RedirectResponse(url="/partners/login", status_code=302)
    deals = await deal_repo.get_by_partner(db, uuid.UUID(partner_id))
    deals_sorted = sorted(deals, key=lambda d: d.created_at, reverse=True)

    def _kpi(status):
        items = [d for d in deals if d.status == status]
        return {
            "count": len(items),
            "total": sum((d.total_cost for d in items), Decimal("0")),
        }

    kpis = {
        "proposal":        _kpi(PartnerDealStatus.Proposal),
        "pending_closure": _kpi(PartnerDealStatus.PendingClosure),
        "closed":          _kpi(PartnerDealStatus.Closed),
        "active":          _kpi(PartnerDealStatus.Active),
        "completed":       _kpi(PartnerDealStatus.Completed),
    }

    return templates.TemplateResponse(
        request, "partners/partials/deals.html",
        {"deals": deals_sorted, "kpis": kpis},
    )


@router.get("/dashboard/deals/{deal_id}", response_class=HTMLResponse)
async def deal_detail_partial(
    request: Request,
    deal_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    partner_id = get_current_partner_id(request)
    if not partner_id:
        return RedirectResponse(url="/partners/login", status_code=302)
    deal = await deal_repo.get_by_id(db, deal_id)
    if not deal or str(deal.partner_id) != partner_id:
        return HTMLResponse("<p class='text-danger'>Deal not found.</p>", status_code=404)
    return templates.TemplateResponse(
        request, "partners/partials/deal_detail.html", {"deal": deal}
    )


# ── Campaigns ─────────────────────────────────────────────────────────────────

@router.get("/dashboard/campaigns", response_class=HTMLResponse)
async def campaigns_partial(request: Request, db: AsyncSession = Depends(get_db)):
    partner_id = get_current_partner_id(request)
    if not partner_id:
        return RedirectResponse(url="/partners/login", status_code=302)
    pcs = await campaign_repo.get_by_partner(db, uuid.UUID(partner_id))
    pcs_sorted = sorted(pcs, key=lambda pc: pc.created_at, reverse=True)
    return templates.TemplateResponse(
        request, "partners/partials/campaigns.html", {"pcs": pcs_sorted}
    )


@router.get("/dashboard/campaigns/{pc_id}", response_class=HTMLResponse)
async def campaign_detail_partial(
    request: Request,
    pc_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    partner_id = get_current_partner_id(request)
    if not partner_id:
        return RedirectResponse(url="/partners/login", status_code=302)
    pc = await campaign_repo.get_by_id(db, pc_id)
    if not pc or str(pc.partner_id) != partner_id:
        return HTMLResponse("<p class='text-danger'>Campaign not found.</p>", status_code=404)
    return templates.TemplateResponse(
        request, "partners/partials/campaign_detail.html", {"pc": pc}
    )
