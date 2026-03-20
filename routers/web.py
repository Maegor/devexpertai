from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from schemas.partner import PartnerCreate
import repositories.partner as repo

router = APIRouter(tags=["web"])

templates = Jinja2Templates(directory="templates")

COUNTRIES = [
    ("AR", "Argentina"), ("AU", "Australia"), ("AT", "Austria"), ("BE", "Belgium"),
    ("BR", "Brazil"), ("CA", "Canada"), ("CL", "Chile"), ("CN", "China"),
    ("CO", "Colombia"), ("HR", "Croatia"), ("CZ", "Czech Republic"), ("DK", "Denmark"),
    ("EG", "Egypt"), ("FI", "Finland"), ("FR", "France"), ("DE", "Germany"),
    ("GR", "Greece"), ("HK", "Hong Kong"), ("HU", "Hungary"), ("IN", "India"),
    ("ID", "Indonesia"), ("IE", "Ireland"), ("IL", "Israel"), ("IT", "Italy"),
    ("JP", "Japan"), ("MY", "Malaysia"), ("MX", "Mexico"), ("NL", "Netherlands"),
    ("NZ", "New Zealand"), ("NG", "Nigeria"), ("NO", "Norway"), ("PK", "Pakistan"),
    ("PL", "Poland"), ("PT", "Portugal"), ("RO", "Romania"), ("SA", "Saudi Arabia"),
    ("SG", "Singapore"), ("ZA", "South Africa"), ("KR", "South Korea"), ("ES", "Spain"),
    ("SE", "Sweden"), ("CH", "Switzerland"), ("TW", "Taiwan"), ("TH", "Thailand"),
    ("TR", "Turkey"), ("UA", "Ukraine"), ("AE", "United Arab Emirates"),
    ("GB", "United Kingdom"), ("US", "United States"), ("VN", "Vietnam"),
]

LANGUAGES = [
    ("en", "English"),
    ("es", "Spanish"),
    ("fr", "French"),
    ("de", "German"),
    ("pt", "Portuguese"),
    ("it", "Italian"),
    ("nl", "Dutch"),
    ("zh", "Chinese"),
    ("ja", "Japanese"),
    ("ar", "Arabic"),
]


@router.get("/register", response_class=HTMLResponse)
async def register_get(request: Request):
    return templates.TemplateResponse(
        request,
        "register.html",
        {"form": {}, "errors": {}, "countries": COUNTRIES, "languages": LANGUAGES},
    )


@router.post("/register", response_class=HTMLResponse)
async def register_post(
    request: Request,
    name: str = Form(""),
    email: str = Form(""),
    company_name: str = Form(""),
    country: str = Form(""),
    language_preference: str = Form("en"),
    collaboration_reason: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    form_data = {
        "name": name,
        "email": email,
        "company_name": company_name,
        "country": country,
        "language_preference": language_preference,
        "collaboration_reason": collaboration_reason,
    }
    errors = {}

    if not name.strip():
        errors["name"] = "Full name is required."
    if not email.strip():
        errors["email"] = "Email address is required."
    if not company_name.strip():
        errors["company_name"] = "Company name is required."
    if not country.strip():
        errors["country"] = "Please select a country."

    if errors:
        return templates.TemplateResponse(
            request,
            "register.html",
            {"form": form_data, "errors": errors, "countries": COUNTRIES, "languages": LANGUAGES},
            status_code=422,
        )

    existing = await repo.get_by_email(db, email)
    if existing:
        errors["email"] = "This email address is already registered."
        return templates.TemplateResponse(
            request,
            "register.html",
            {"form": form_data, "errors": errors, "countries": COUNTRIES, "languages": LANGUAGES},
            status_code=409,
        )

    data = PartnerCreate(
        name=name.strip(),
        email=email.strip(),
        company_name=company_name.strip() or None,
        country=country or None,
        language_preference=language_preference or "en",
        collaboration_reason=collaboration_reason.strip() or None,
    )
    partner = await repo.create(db, data)

    return templates.TemplateResponse(
        request,
        "register_success.html",
        {"name": partner.name, "email": partner.email},
    )
