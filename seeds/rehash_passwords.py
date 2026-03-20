"""
Migra los password_hash de sha256 a bcrypt para todos los internal_users.
Asume que la contraseña original es "Password1234!" (seed por defecto).
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import bcrypt
from sqlalchemy import select
from database import SessionLocal

from models import InternalUser

DEFAULT_PASSWORD = "Password1234!"


def _hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


async def run():
    async with SessionLocal() as session:
        result = await session.execute(select(InternalUser))
        users = result.scalars().all()

        count = 0
        for user in users:
            # Solo migrar hashes que no sean bcrypt (bcrypt empieza con $2b$ o $2a$)
            if not user.password_hash.startswith("$2"):
                user.password_hash = _hash(DEFAULT_PASSWORD)
                count += 1
                print(f"  rehashed: {user.email}")
            else:
                print(f"  omitido (ya es bcrypt): {user.email}")

        await session.commit()
        print(f"\nMigración completada: {count} usuarios actualizados.")


if __name__ == "__main__":
    asyncio.run(run())
