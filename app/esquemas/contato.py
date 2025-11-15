# app/esquemas/contato.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict


class ContatoBase(BaseModel):
    """
    Campos básicos compartilhados entre criação, leitura e atualização.
    """
    primeiro_nome: str
    sobrenome: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    situacao: str = "lead"


class ContatoCriar(ContatoBase):
    """
    Esquema usado ao criar um novo contato.
    """
    # Exemplo que aparece direto na documentação do FastAPI (/docs)
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "primeiro_nome": "João",
                "sobrenome": "Silva",
                "email": "joao.silva@empresa.com",
                "telefone": "5592999999999",
                "situacao": "lead"
            }
        }
    )


class ContatoAtualizar(BaseModel):
    """
    Esquema para atualização parcial de contato.
    Todos os campos são opcionais.
    """
    primeiro_nome: Optional[str] = None
    sobrenome: Optional[str] = None
    email: Optional[EmailStr] = None
    telefone: Optional[str] = None
    situacao: Optional[str] = None


class ContatoLer(ContatoBase):
    """
    Esquema de resposta (leitura) de contato.
    Inclui campos somente leitura como id e datas.
    """
    id: int
    criado_em: datetime
    atualizado_em: Optional[datetime] = None

    # Pydantic v2: substitui o antigo `orm_mode = True`
    model_config = ConfigDict(from_attributes=True)
