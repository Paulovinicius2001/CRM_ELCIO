# app/api/v1/funcionarios.py
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.banco_dados import obter_sessao
from app.modelos.funcionario import Funcionario
from app.esquemas.funcionario import (
    FuncionarioCriar,
    FuncionarioLer,
    FuncionarioAtualizar,
)

roteador = APIRouter(
    prefix="/funcionarios",
    tags=["Funcionários"],
)


@roteador.post(
    "/",
    response_model=FuncionarioLer,
    status_code=status.HTTP_201_CREATED,
)
def criar_funcionario(
    dados: FuncionarioCriar,
    db: Session = Depends(obter_sessao),
):
    """
    Cria um novo funcionário.

    Use esta rota para cadastrar os usuários que serão donos dos negócios
    e aparecerão no painel de indicadores.
    """
    # Checa se já existe funcionário com mesmo e-mail (se informado)
    if dados.email:
        existente = (
            db.query(Funcionario)
            .filter(Funcionario.email == dados.email)
            .first()
        )
        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um funcionário cadastrado com esse e-mail.",
            )

    funcionario = Funcionario(
        nome=dados.nome,
        email=dados.email,
        cargo=dados.cargo,
        ativo=dados.ativo,
    )
    db.add(funcionario)
    db.commit()
    db.refresh(funcionario)
    return funcionario


@roteador.get(
    "/",
    response_model=List[FuncionarioLer],
)
def listar_funcionarios(
    somente_ativos: bool = False,
    db: Session = Depends(obter_sessao),
):
    """
    Lista todos os funcionários cadastrados.

    - Se `somente_ativos=true`, retorna apenas funcionários com `ativo = True`.
    """
    consulta = db.query(Funcionario)

    if somente_ativos:
        consulta = consulta.filter(Funcionario.ativo == True)  # noqa: E712

    funcionarios = consulta.order_by(Funcionario.nome).all()
    return funcionarios


@roteador.get(
    "/{funcionario_id}",
    response_model=FuncionarioLer,
)
def obter_funcionario(
    funcionario_id: int,
    db: Session = Depends(obter_sessao),
):
    """
    Busca um funcionário pelo ID.
    """
    funcionario = (
        db.query(Funcionario)
        .filter(Funcionario.id == funcionario_id)
        .first()
    )
    if not funcionario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Funcionário não encontrado.",
        )
    return funcionario


@roteador.put(
    "/{funcionario_id}",
    response_model=FuncionarioLer,
)
def atualizar_funcionario(
    funcionario_id: int,
    dados: FuncionarioAtualizar,
    db: Session = Depends(obter_sessao),
):
    """
    Atualiza os dados de um funcionário.
    Permite edição parcial (envie apenas o que deseja mudar).
    """
    funcionario = (
        db.query(Funcionario)
        .filter(Funcionario.id == funcionario_id)
        .first()
    )
    if not funcionario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Funcionário não encontrado.",
        )

    dados_dict = dados.model_dump(exclude_unset=True)

    # Se for alterar e-mail, verificar duplicidade
    if "email" in dados_dict and dados_dict["email"]:
        outro = (
            db.query(Funcionario)
            .filter(
                Funcionario.email == dados_dict["email"],
                Funcionario.id != funcionario_id,
            )
            .first()
        )
        if outro:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe outro funcionário com esse e-mail.",
            )

    for campo, valor in dados_dict.items():
        setattr(funcionario, campo, valor)

    db.commit()
    db.refresh(funcionario)
    return funcionario


@roteador.delete(
    "/{funcionario_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def excluir_funcionario(
    funcionario_id: int,
    db: Session = Depends(obter_sessao),
):
    """
    Remove um funcionário do sistema.

    Obs.: Em um sistema real, muitas vezes é melhor apenas marcar `ativo = False`
    para não quebrar vínculos históricos com negócios antigos.
    """
    funcionario = (
        db.query(Funcionario)
        .filter(Funcionario.id == funcionario_id)
        .first()
    )
    if not funcionario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Funcionário não encontrado.",
        )

    db.delete(funcionario)
    db.commit()
    return
