from sqlalchemy import inspect
from database import Base, engine
from models import AgencyModel, DonationModel, DonorModel 

def init_db():
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    print(f"Existing tables before creation: {existing_tables}")

    # Check Base.metadata
    print("Tables in Base.metadata:")
    for table_name, table in Base.metadata.tables.items():
        print(f"- {table_name}")
        
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Table creation completed.")

    # Check tables after creation
    existing_tables = inspector.get_table_names()
    print(f"Existing tables after creation: {existing_tables}")

    # Check if all model tables exist in the database
    model_tables = set(Base.metadata.tables.keys())
    missing_tables = model_tables - set(existing_tables)
    if missing_tables:
        print(f"Warning: Some tables are still missing: {missing_tables}")
    else:
        print("All expected tables have been created successfully.")

if __name__ == "__main__":
    init_db()