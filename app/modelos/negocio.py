from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    Date,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.banco_dados import Base


class Negocio(Base):
    """
    Representa um negócio/oportunidade no funil de vendas.
    """
    __tablename__ = "negocios"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(200), nullable=False)
    descricao = Column(String(500), nullable=True)
    valor_previsto = Column(Numeric(12, 2), nullable=True)

    # Fase do funil: novo, em_proposta, fechado_ganho, fechado_perdido
    fase = Column(String(50), nullable=False, default="novo")

    # Origem do negócio: whatsapp, site, instagram, indicação, ligação etc.
    origem = Column(String(50), nullable=True)

    # Probabilidade de fechamento (0–100)
    probabilidade = Column(Integer, nullable=True)

    # Relacionamentos
    contato_id = Column(Integer, ForeignKey("contatos.id"), nullable=False)
    responsavel_id = Column(Integer, ForeignKey("funcionarios.id"), nullable=True)

    data_prevista_fechamento = Column(Date, nullable=True)
    data_fechamento = Column(Date, nullable=True)

    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())

    # Lados do relacionamento:
    # aqui usamos back_populates, combinando com Contato.negocios
    contato = relationship("Contato", back_populates="negocios")
    responsavel = relationship("Funcionario")

    def __repr__(self) -> str:
        return f"<Negocio id={self.id} titulo='{self.titulo}'>"
