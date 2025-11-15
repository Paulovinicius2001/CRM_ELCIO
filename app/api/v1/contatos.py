# app/api/v1/contatos.py
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.banco_dados import obter_sessao
from app.modelos.contato import Contato
from app.esquemas.contato import ContatoCriar, ContatoLer, ContatoAtualizar

roteador = APIRouter(
    prefix="/contatos",
    tags=["Contatos"],
)


@roteador.post(
    "/",
    response_model=ContatoLer,
    status_code=status.HTTP_201_CREATED,
    summary="Criar um novo contato",
    response_description="Dados completos do contato criado.",
)
def criar_contato(
    contato_entrada: ContatoCriar,
    db: Session = Depends(obter_sessao),
):
    """
    Cria um novo contato na base de dados.

    - Garante que não exista outro contato com o mesmo e-mail.
    """
    if contato_entrada.email:
        existente = (
            db.query(Contato)
            .filter(Contato.email == contato_entrada.email)
            .first()
        )
        if existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um contato cadastrado com esse e-mail.",
            )

    contato = Contato(**contato_entrada.dict())
    db.add(contato)
    db.commit()
    db.refresh(contato)
    return contato


@roteador.get(
    "/",
    response_model=List[ContatoLer],
    summary="Listar contatos",
    response_description="Lista paginada de contatos.",
)
def listar_contatos(
    pular: int = Query(0, ge=0, description="Quantidade de registros a pular (offset)."),
    limite: int = Query(100, ge=1, le=500, description="Quantidade máxima de registros a retornar."),
    situacao: Optional[str] = Query(
        default=None,
        description="Filtrar por situação (ex.: lead, cliente, inativo).",
    ),
    db: Session = Depends(obter_sessao),
):
    """
    Lista contatos com paginação simples e filtro opcional por situação.
    """
    consulta = db.query(Contato)

    if situacao:
        consulta = consulta.filter(Contato.situacao == situacao)

    contatos = consulta.offset(pular).limit(limite).all()
    return contatos


@roteador.get(
    "/{contato_id}",
    response_model=ContatoLer,
    summary="Obter um contato pelo ID",
    response_description="Dados completos do contato solicitado.",
)
def obter_contato(
    contato_id: int,
    db: Session = Depends(obter_sessao),
):
    """
    Retorna um contato específico pelo ID.
    """
    contato = db.get(Contato, contato_id)
    if not contato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contato não encontrado.",
        )
    return contato


@roteador.put(
    "/{contato_id}",
    response_model=ContatoLer,
    summary="Atualizar um contato",
    response_description="Dados completos do contato após atualização.",
)
def atualizar_contato(
    contato_id: int,
    contato_entrada: ContatoAtualizar,
    db: Session = Depends(obter_sessao),
):
    """
    Atualiza os dados de um contato existente.
    Permite atualização parcial (apenas campos enviados).
    """
    contato = db.get(Contato, contato_id)
    if not contato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contato não encontrado.",
        )

    dados_atualizados = contato_entrada.dict(exclude_unset=True)
    for campo, valor in dados_atualizados.items():
        setattr(contato, campo, valor)

    db.commit()
    db.refresh(contato)
    return contato


@roteador.delete(
    "/{contato_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir um contato",
)
def excluir_contato(
    contato_id: int,
    db: Session = Depends(obter_sessao),
):
    """
    Exclui um contato da base de dados.
    """
    contato = db.get(Contato, contato_id)
    if not contato:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contato não encontrado.",
        )

    db.delete(contato)
    db.commit()
    return None
