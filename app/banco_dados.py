# app/banco_dados.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# URL do banco de dados (por enquanto SQLite em arquivo local)
DATABASE_URL = "sqlite:///./crm.db"

# Criação do engine do SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Necessário para SQLite com múltiplas threads
)

# Fábrica de sessões (cada request terá sua própria sessão)
SessaoLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe base para os modelos
Base = declarative_base()


def obter_sessao():
    """
    Dependência do FastAPI para obter uma sessão de banco de dados.
    Fecha a sessão automaticamente ao final da requisição.
    """
    sessao = SessaoLocal()
    try:
        yield sessao
    finally:
        sessao.close()
