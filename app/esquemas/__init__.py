# app/esquemas/__init__.py
# Pacote para os esquemas (Pydantic) da API.
# app/esquemas/__init__.py
from app.esquemas.contato import (
    ContatoBase,
    ContatoCriar,
    ContatoAtualizar,
    ContatoLer,
)  # noqa: F401

from app.esquemas.negocio import (
    NegocioBase,
    NegocioCriar,
    NegocioAtualizar,
    NegocioLer,
)  # noqa: F401

from app.esquemas.funcionario import (
    FuncionarioBase,
    FuncionarioCriar,
    FuncionarioAtualizar,
    FuncionarioLer,
)  # noqa: F401
