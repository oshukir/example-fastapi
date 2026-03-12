from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
from .config import settings

# while True:
#     try:
#         conn = psycopg2.connect(
#             host = 'localhost',
#             user = 'postgres',
#             password = 'osser2005',
#             port = '5433',
#             database = 'fastapi',
#             cursor_factory = RealDictCursor
#         )
#         cursor = conn.cursor()
#         print("Database connection is successful")
#         break
#     except Exception as error:
#         print("db connection is failed")
#         print(f"The error is - {error}")

SQLALCHEMY_DB_URL = f"postgresql://{settings.DB_USERNAME}:{settings.DB_PASSWORD}@{settings.DB_HOSTNAME}:{settings.DB_PORT}/{settings.DB_NAME}"

engine = create_engine(SQLALCHEMY_DB_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()