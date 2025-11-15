# app/modelos/__init__.py
# Importa os modelos para garantir que o SQLAlchemy conheça as tabelas.
from app.modelos.contato import Contato  # noqa: F401
from app.modelos.negocio import Negocio  # noqa: F401
from app.modelos.funcionario import Funcionario  # noqa: F401


