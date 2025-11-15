# app/esquemas/negocio.py
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, conint


class NegocioBase(BaseModel):
    """
    Campos básicos de um negócio (oportunidade).
    """
    titulo: str
    descricao: Optional[str] = None
    valor_previsto: Optional[float] = None
    fase: str = "novo"
    origem: Optional[str] = None
    probabilidade: Optional[conint(ge=0, le=100)] = None
    contato_id: Optional[int] = None
    responsavel_id: Optional[int] = None
    data_prevista_fechamento: Optional[date] = None
    data_fechamento: Optional[date] = None


class NegocioCriar(NegocioBase):
    """
    Esquema para criação de negócio.
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "titulo": "Projeto CRM para Empresa X",
                "descricao": "Implantação do CRM e integração com n8n.",
                "valor_previsto": 15000.0,
                "fase": "novo",
                "origem": "whatsapp",
                "probabilidade": 40,
                "contato_id": 1,
                "responsavel_id": 1,
                "data_prevista_fechamento": "2025-12-31",
                "data_fechamento": None
            }
        }
    )


class NegocioAtualizar(BaseModel):
    """
    Atualização parcial de negócio.
    """
    titulo: Optional[str] = None
    descricao: Optional[str] = None
    valor_previsto: Optional[float] = None
    fase: Optional[str] = None
    origem: Optional[str] = None
    probabilidade: Optional[conint(ge=0, le=100)] = None
    contato_id: Optional[int] = None
    responsavel_id: Optional[int] = None
    data_prevista_fechamento: Optional[date] = None
    data_fechamento: Optional[date] = None


class NegocioLer(NegocioBase):
    """
    Esquema de leitura (retorno) de negócio.
    """
    id: int
    criado_em: datetime
    atualizado_em: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
