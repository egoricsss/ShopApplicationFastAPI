from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy import text
from app.schemas import get_config
import asyncio

import sys
import os


sys.path.append(os.path.join(os.getcwd(), '../../'))

config = get_config()


engine = create_async_engine(url=config.db_url.get_secret_value(), echo=True)


async def check_db_connection():
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
    except OperationalError:
        print("connection failed")
    except Exception as e:
        print(f"Error: {e}")
    else:
        print("Connection success")


if __name__ == "__main__":
    asyncio.run(check_db_connection())
