from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Garantiza que checkout_software.db siempre se cree dentro de la carpeta /backend
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "checkout_software.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH.as_posix()}"

# check_same_thread=False es necesario en SQLite para permitir múltiples hilos en FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

