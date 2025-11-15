from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.banco_dados import Base


class Contato(Base):
    """
    Representa um contato no CRM (lead, cliente, etc.).
    """
    __tablename__ = "contatos"

    id = Column(Integer, primary_key=True, index=True)

    # Campos principais do contato
    nome = Column(String(150), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=True)
    telefone = Column(String(50), nullable=True)
    empresa = Column(String(150), nullable=True)

    # De onde veio o lead (whatsapp, site, instagram, indicação, ligação...)
    origem = Column(String(50), nullable=True)

    # Situação no funil de relacionamento (lead, cliente, inativo)
    situacao = Column(String(50), nullable=False, default="lead")

    # Campos de auditoria
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())

    # Relacionamento com negócios (lado "um" da relação 1:N)
    negocios = relationship("Negocio", back_populates="contato")

    def __repr__(self) -> str:
        return f"<Contato id={self.id} nome='{self.nome}'>"
