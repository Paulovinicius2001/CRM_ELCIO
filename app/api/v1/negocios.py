# app/api/v1/negocios.py
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.banco_dados import obter_sessao
from app.modelos.negocio import Negocio
from app.esquemas.negocio import NegocioCriar, NegocioLer, NegocioAtualizar

roteador = APIRouter(
    prefix="/negocios",
    tags=["Negócios"],
)


@roteador.post(
    "/",
    response_model=NegocioLer,
    status_code=status.HTTP_201_CREATED,
    summary="Criar um novo negócio",
)
def criar_negocio(
    entrada: NegocioCriar,
    db: Session = Depends(obter_sessao),
):
    """
    Cria uma nova oportunidade no funil de vendas.
    """
    negocio = Negocio(**entrada.dict())
    db.add(negocio)
    db.commit()
    db.refresh(negocio)
    return negocio


@roteador.get(
    "/",
    response_model=List[NegocioLer],
    summary="Listar negócios",
)
def listar_negocios(
    fase: Optional[str] = Query(default=None, description="Filtrar por fase do funil."),
    origem: Optional[str] = Query(default=None, description="Filtrar por origem (whatsapp, site, etc.)."),
    contato_id: Optional[int] = Query(default=None, description="Filtrar por ID do contato."),
    pular: int = Query(0, ge=0),
    limite: int = Query(100, ge=1, le=500),
    db: Session = Depends(obter_sessao),
):
    """
    Lista negócios com filtros opcionais por fase, origem e contato.
    """
    consulta = db.query(Negocio)

    if fase:
        consulta = consulta.filter(Negocio.fase == fase)

    if origem:
        consulta = consulta.filter(Negocio.origem == origem)

    if contato_id:
        consulta = consulta.filter(Negocio.contato_id == contato_id)

    negocios = (
        consulta
        .order_by(Negocio.criado_em.desc())
        .offset(pular)
        .limit(limite)
        .all()
    )
    return negocios


@roteador.get(
    "/{negocio_id}",
    response_model=NegocioLer,
    summary="Obter um negócio pelo ID",
)
def obter_negocio(
    negocio_id: int,
    db: Session = Depends(obter_sessao),
):
    negocio = db.get(Negocio, negocio_id)
    if not negocio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Negócio não encontrado.",
        )
    return negocio


@roteador.put(
    "/{negocio_id}",
    response_model=NegocioLer,
    summary="Atualizar um negócio",
)
def atualizar_negocio(
    negocio_id: int,
    entrada: NegocioAtualizar,
    db: Session = Depends(obter_sessao),
):
    negocio = db.get(Negocio, negocio_id)
    if not negocio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Negócio não encontrado.",
        )

    dados = entrada.dict(exclude_unset=True)
    for campo, valor in dados.items():
        setattr(negocio, campo, valor)

    db.commit()
    db.refresh(negocio)
    return negocio


@roteador.delete(
    "/{negocio_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Excluir um negócio",
)
def excluir_negocio(
    negocio_id: int,
    db: Session = Depends(obter_sessao),
):
    negocio = db.get(Negocio, negocio_id)
    if not negocio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Negócio não encontrado.",
        )

    db.delete(negocio)
    db.commit()
    return None
