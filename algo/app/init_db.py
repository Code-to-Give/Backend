import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from db.database import Base, engine
from db.models import AgencyModel, DonationModel, DonorModel

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSession(engine) as session:
        async with session.begin():
            # Use text() to create a SQL expression
            result = await session.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'"))
            existing_tables = [row[0] for row in result]
            
            print(f"Existing tables after creation: {existing_tables}")

            # Check if all model tables exist in the database
            model_tables = set(Base.metadata.tables.keys())
            missing_tables = model_tables - set(existing_tables)
            if missing_tables:
                print(f"Warning: Some tables are still missing: {missing_tables}")
            else:
                print("All expected tables have been created successfully.")

if __name__ == "__main__":
    asyncio.run(init_db())