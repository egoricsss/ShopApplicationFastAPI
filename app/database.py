import asyncio
from typing import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.schemas import get_config

config = get_config()


_engine = create_async_engine(url=config.db_url.get_secret_value(), echo=True)
_async_session_factory = async_sessionmaker(bind=_engine, expire_on_commit=False)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with _async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


if __name__ == "__main__":

    async def main():
        print("--- Testing Engine ---")
        try:
            async with _engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            print("✅ Connection success")
        except OperationalError:
            print("❌ Connection failed")
        except Exception as e:
            print(f"❌ Error: {e}")

        print("\n--- Testing Session ---")
        async with _async_session_factory() as session:
            try:
                result = await session.execute(text("SELECT current_timestamp"))
                print(f"🕒 DB Time: {result.scalar()}")
                await session.commit()
                print("✅ Session test success")
            except Exception as e:
                await session.rollback()
                print(f"❌ Session test failed: {e}")
                raise

        await _engine.dispose()

    asyncio.run(main())
