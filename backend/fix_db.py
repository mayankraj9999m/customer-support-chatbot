import asyncio
from sqlalchemy import text
from database import engine

async def main():
    async with engine.begin() as conn:
        try:
            await conn.execute(text("ALTER TABLE users ADD COLUMN name VARCHAR;"))
            print("Successfully added 'name' column to 'users' table.")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
