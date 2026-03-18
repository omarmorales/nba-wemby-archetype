from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

engine = create_engine(
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'advanced'
        ORDER BY ordinal_position;
    """))
    print("=== advanced columns ===")
    for row in result:
        print(row[0])

    result2 = conn.execute(text("""
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'totals'
        ORDER BY ordinal_position;
    """))
    print("\n=== totals columns ===")
    for row in result2:
        print(row[0])