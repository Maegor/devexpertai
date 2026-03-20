import asyncio
import random
import sys
import os
from datetime import date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import select
from database import SessionLocal, engine, Base
from models import Partner, BillingEntity

ENTITIES = [
    ("Acme Corporation Legal",         "US", "EIN-45-1234567",  "123 Main St, New York, NY 10001"),
    ("Blue Ocean Ltd UK",              "GB", "GB123456789",     "10 Downing Way, London EC1A 1BB"),
    ("TechNova GmbH Legal",            "DE", "DE987654321",     "Unter den Linden 5, 10117 Berlin"),
    ("SunPath Facturación SA",         "MX", "RFC-SUNP810101",  "Av. Insurgentes Sur 1234, CDMX"),
    ("Apex Solutions Canada",          "CA", "BN-123456789",    "100 King St W, Toronto, ON M5X 1B8"),
    ("Meridian Group France",          "FR", "FR12345678901",   "15 Rue de la Paix, 75001 París"),
    ("Orbit Digital SL Facturación",   "ES", "ESB12345678",     "Calle Gran Vía 28, 28013 Madrid"),
    ("Vertex Holdings Australia",      "AU", "ABN-51824753556", "Level 10, 1 Market St, Sydney NSW 2000"),
    ("Pulse Agency Brasil",            "BR", "CNPJ-12.345.678", "Av. Paulista 1000, São Paulo SP"),
    ("Nexus Partners BV",              "NL", "NL123456789B01",  "Herengracht 420, 1017 BZ Amsterdam"),
    ("CloudPeak Singapore",            "SG", "UEN-201912345K",  "1 Raffles Place, #20-01, Singapore 048616"),
    ("Redwood Ventures LLC",           "US", "EIN-46-9876543",  "500 Technology Dr, San Francisco, CA 94105"),
    ("Horizon Consulting Italy",       "IT", "IT12345678901",   "Via Roma 10, 20121 Milán"),
    ("Summit Digital Colombia",        "CO", "NIT-900.123.456", "Calle 72 #10-07, Bogotá"),
    ("Aurora Growth AB",               "SE", "SE556123456701",  "Birger Jarlsgatan 2, 111 45 Estocolmo"),
    ("IronBridge Sp. z o.o.",          "PL", "PL5261040828",    "ul. Marszałkowska 100, 00-026 Varsovia"),
    ("CrestLine Lda.",                 "PT", "PT501234567",     "Av. da Liberdade 110, 1269-046 Lisboa"),
    ("Zenith Global FZE",              "AE", "AE-TRN-123456",   "DIFC Gate Building, Dubai"),
    ("BlueSky Analytics NZ",           "NZ", "NZ-GST-123456",   "Level 5, 1 Queen St, Auckland 1010"),
    ("Atlas Commerce India",           "IN", "GSTIN-29ABCDE",   "Bandra Kurla Complex, Mumbai 400051"),
]

BANKING_TEMPLATE = "ENCRYPTED::IBAN={iban}|BIC={bic}|BANK={bank}"

IBANS = [
    ("US33XXXX", "CHASUS33", "JPMorgan Chase"),
    ("GB29NWBK", "NWBKGB2L", "NatWest Bank"),
    ("DE89370400", "COBADEFFXXX", "Commerzbank"),
    ("MX21BANO", "BANOMXMM", "BBVA México"),
    ("CA Transit", "ROYCCAT2", "Royal Bank of Canada"),
    ("FR7630006", "BNPAFRPPXXX", "BNP Paribas"),
    ("ES9121000", "CAIXESBBXXX", "CaixaBank"),
    ("AU12WPAC", "WPACAU2S", "Westpac"),
    ("BR15ITAU", "ITAUBRSP", "Itaú Unibanco"),
    ("NL91ABNA", "ABNANL2A", "ABN AMRO"),
]


async def run():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with SessionLocal() as session:
        result = await session.execute(select(Partner))
        partners = result.scalars().all()

        if not partners:
            print("ERROR: No hay partners. Ejecuta primero: .venv/bin/python seeds/partners.py")
            return

        print(f"Partners encontrados: {len(partners)}")

        # Asignar un partner distinto a cada una de las 20 entidades
        selected_partners = random.sample(partners, min(20, len(partners)))

        created = 0
        skipped = 0

        for i, (entity_name, country, tax_id, address) in enumerate(ENTITIES):
            partner = selected_partners[i]

            existing = await session.execute(
                select(BillingEntity).where(
                    BillingEntity.partner_id == partner.id,
                    BillingEntity.entity_name == entity_name,
                )
            )
            if existing.scalar_one_or_none():
                print(f"  omitido (ya existe): {entity_name}")
                skipped += 1
                continue

            iban, bic, bank = random.choice(IBANS)
            effective_from = date(random.randint(2020, 2023), random.randint(1, 12), 1)
            effective_until = None if random.random() > 0.3 else date(2024, random.randint(1, 12), 1)

            entity = BillingEntity(
                partner_id=partner.id,
                entity_name=entity_name,
                country=country,
                tax_identification_number=tax_id,
                vat_registered=random.choice([True, False]),
                address=address,
                banking_details=BANKING_TEMPLATE.format(iban=iban, bic=bic, bank=bank),
                effective_from=effective_from,
                effective_until=effective_until,
            )
            session.add(entity)
            print(f"  creado: {entity_name} → partner: {partner.name} [{partner.email}]")
            created += 1

        await session.commit()

    print(f"\nSeed completado: {created} creados, {skipped} omitidos.")


if __name__ == "__main__":
    asyncio.run(run())
