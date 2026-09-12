import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
from database.models import Base
 
# Caminho do banco: database/app.db (fica junto dos outros arquivos do pacote)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "app.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"
 
# check_same_thread=False é necessário porque o Streamlit pode acessar
# a mesma conexão a partir de threads diferentes durante os reruns
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)
 
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
 
 
def init_db():
    """Cria todas as tabelas definidas em models.py, caso ainda não existam."""
    Base.metadata.create_all(bind=engine)
 
 
def get_session():
    """Retorna uma nova sessão do SQLAlchemy para uso em operações do app."""
    return SessionLocal()