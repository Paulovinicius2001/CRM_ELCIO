# app/esquemas/funcionario.py
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict


class FuncionarioBase(BaseModel):
    """
    Campos básicos de um funcionário.
    """
    nome: str
    email: Optional[EmailStr] = None
    cargo: Optional[str] = None
    ativo: bool = True


class FuncionarioCriar(FuncionarioBase):
    """
    Esquema para criação de funcionário.
    """
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "nome": "João Silva",
                "email": "joao.silva@empresa.com",
                "cargo": "Vendedor",
                "ativo": True,
            }
        }
    )


class FuncionarioAtualizar(BaseModel):
    """
    Atualização parcial de funcionário.
    Todos os campos são opcionais.
    """
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    cargo: Optional[str] = None
    ativo: Optional[bool] = None


class FuncionarioLer(FuncionarioBase):
    """
    Esquema de leitura/retorno de funcionário.
    """
    id: int
    criado_em: datetime
    atualizado_em: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
