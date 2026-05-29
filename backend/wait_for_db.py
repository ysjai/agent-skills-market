import asyncio
import os
import sys

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


RETRIES = int(os.getenv("DB_READY_RETRIES", "30"))
DELAY_SECONDS = float(os.getenv("DB_READY_DELAY", "2"))


async def main() -> None:
    database_url = os.environ["DATABASE_URL"]
    engine = create_async_engine(database_url, pool_pre_ping=True)

    try:
        for attempt in range(1, RETRIES + 1):
            try:
                async with engine.connect() as connection:
                    await connection.execute(text("SELECT 1"))
                print("Database is ready.")
                return
            except Exception as exc:
                if attempt == RETRIES:
                    print(f"Database is not ready after {RETRIES} attempts: {exc}", file=sys.stderr)
                    raise
                print(f"Waiting for database ({attempt}/{RETRIES}): {exc}")
                await asyncio.sleep(DELAY_SECONDS)
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
