# app/modelos/funcionario.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func

from app.banco_dados import Base


class Funcionario(Base):
    """
    Representa um funcionário/usuário do CRM.
    Usado para atribuir negócios e calcular indicadores.
    """
    __tablename__ = "funcionarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=True)
    cargo = Column(String(100), nullable=True)
    ativo = Column(Boolean, default=True)

    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<Funcionario id={self.id} nome='{self.nome}'>"
