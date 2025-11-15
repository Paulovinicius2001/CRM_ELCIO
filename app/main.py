# app/main.py
from datetime import datetime, date, timedelta
from typing import Optional, List, Dict

from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session
import random


from app.banco_dados import Base, engine, obter_sessao
import app.modelos  # garante o registro dos modelos
from app.modelos.contato import Contato
from app.modelos.negocio import Negocio
from app.modelos.funcionario import Funcionario
from app.api.v1.contatos import roteador as roteador_contatos
from app.api.v1.negocios import roteador as roteador_negocios
from app.api.v1.funcionarios import roteador as roteador_funcionarios


# Metadados das tags para a documentação
tags_metadata = [
    {
        "name": "Contatos",
        "description": "Operações de criação, listagem, atualização e exclusão de contatos (leads, clientes etc.).",
    },
    {
        "name": "Negócios",
        "description": "Funil de vendas: criação, acompanhamento e fechamento de oportunidades.",
    },
    {
        "name": "Funcionários",
        "description": "Cadastro e gerenciamento de funcionários (donos dos negócios).",
    },
    {
        "name": "Status",
        "description": "Rotas de status e saúde da API.",
    },
    {
        "name": "Interface",
        "description": "Interfaces web visuais do CRM (contatos, funil, indicadores).",
    },
]


# Configuração de templates (interface web)
templates = Jinja2Templates(directory="app/interface/templates")

# Criação da aplicação FastAPI
app = FastAPI(
    title="API CRM Genérico",
    description=(
        "API de CRM em português, pensada para integrar com n8n e ter painéis visuais.\n\n"
        "Use `/docs` para testar a API, `/painel` para contatos, `/funil` para negócios e `/indicadores` para indicadores por funcionário."
    ),
    version="0.6.0",
    openapi_tags=tags_metadata,
    contact={
        "name": "Meu CRM",
        "email": "contato@example.com",
    },
    license_info={
        "name": "MIT",
        "identifier": "MIT",
    },
)

# Middleware de CORS (desenvolvimento)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # depois você pode restringir
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Criação das tabelas no banco de dados (caso ainda não existam)
Base.metadata.create_all(bind=engine)


@app.get("/", tags=["Status"])
def raiz():
    """
    Endpoint raiz simples, útil para ver se a API está de pé.
    """
    return {
        "mensagem": "Bem-vindo à API do CRM 👋",
        "documentacao": "/docs",
        "painel_contatos": "/painel",
        "painel_funil": "/funil",
        "painel_indicadores": "/indicadores",
        "status": "ok",
    }


@app.get("/health", tags=["Status"])
def healthcheck():
    """
    Healthcheck simples, útil para monitoramento.
    """
    return {"status": "ok"}


@app.get("/painel", response_class=HTMLResponse, tags=["Interface"])
def painel_contatos(
    request: Request,
    db: Session = Depends(obter_sessao),
):
    """
    Painel visual de contatos, com cards de métricas e tabela.
    """

    contatos = (
        db.query(Contato)
        .order_by(Contato.criado_em.desc())
        .all()
    )

    total_contatos = db.query(func.count(Contato.id)).scalar() or 0
    total_leads = (
        db.query(func.count(Contato.id))
        .filter(Contato.situacao == "lead")
        .scalar()
        or 0
    )
    total_clientes = (
        db.query(func.count(Contato.id))
        .filter(Contato.situacao == "cliente")
        .scalar()
        or 0
    )
    total_inativos = (
        db.query(func.count(Contato.id))
        .filter(Contato.situacao == "inativo")
        .scalar()
        or 0
    )
    total_outros = max(total_contatos - (total_leads + total_clientes + total_inativos), 0)

    limite_7_dias = datetime.utcnow().date() - timedelta(days=7)
    contatos_ultimos_7 = 0
    for c in contatos:
        if c.criado_em:
            if c.criado_em.date() >= limite_7_dias:
                contatos_ultimos_7 += 1

    if total_contatos > 0:
        taxa_leads = round((total_leads / total_contatos) * 100)
        taxa_clientes = round((total_clientes / total_contatos) * 100)
        taxa_inativos = round((total_inativos / total_contatos) * 100)
        taxa_outros = max(0, 100 - (taxa_leads + taxa_clientes + taxa_inativos))
    else:
        taxa_leads = taxa_clientes = taxa_inativos = taxa_outros = 0

    if total_leads > 0:
        taxa_conversao_lead_cliente = round((total_clientes / total_leads) * 100)
    else:
        taxa_conversao_lead_cliente = 0

    contexto = {
        "request": request,
        "contatos": contatos,
        "total_contatos": total_contatos,
        "total_leads": total_leads,
        "total_clientes": total_clientes,
        "total_inativos": total_inativos,
        "total_outros": total_outros,
        "contatos_ultimos_7": contatos_ultimos_7,
        "taxa_leads": taxa_leads,
        "taxa_clientes": taxa_clientes,
        "taxa_inativos": taxa_inativos,
        "taxa_outros": taxa_outros,
        "taxa_conversao_lead_cliente": taxa_conversao_lead_cliente,
    }

    return templates.TemplateResponse("dashboard.html", contexto)


@app.get("/funil", response_class=HTMLResponse, tags=["Interface"])
def painel_funil(
    request: Request,
    db: Session = Depends(obter_sessao),
):
    """
    Painel visual do funil de vendas (negócios por fase).
    """
    # Carrega negócios por fase
    novos = (
        db.query(Negocio)
        .filter(Negocio.fase == "novo")
        .order_by(Negocio.criado_em.desc())
        .all()
    )
    em_proposta = (
        db.query(Negocio)
        .filter(Negocio.fase == "em_proposta")
        .order_by(Negocio.criado_em.desc())
        .all()
    )
    fechados_ganhos = (
        db.query(Negocio)
        .filter(Negocio.fase == "fechado_ganho")
        .order_by(Negocio.criado_em.desc())
        .all()
    )
    fechados_perdidos = (
        db.query(Negocio)
        .filter(Negocio.fase == "fechado_perdido")
        .order_by(Negocio.criado_em.desc())
        .all()
    )

    def soma_valor(lista: List[Negocio]) -> float:
        return round(sum(n.valor_previsto or 0 for n in lista), 2)

    total_novos = len(novos)
    total_em_proposta = len(em_proposta)
    total_ganhos = len(fechados_ganhos)
    total_perdidos = len(fechados_perdidos)

    valor_novos = soma_valor(novos)
    valor_em_proposta = soma_valor(em_proposta)
    valor_ganhos = soma_valor(fechados_ganhos)
    valor_perdidos = soma_valor(fechados_perdidos)

    total_negocios = total_novos + total_em_proposta + total_ganhos + total_perdidos
    valor_total = valor_novos + valor_em_proposta + valor_ganhos + valor_perdidos

    if (total_novos + total_em_proposta + total_ganhos) > 0:
        taxa_fechamento = round(
            (total_ganhos / (total_novos + total_em_proposta + total_ganhos)) * 100
        )
    else:
        taxa_fechamento = 0

    contexto = {
        "request": request,
        "novos": novos,
        "em_proposta": em_proposta,
        "fechados_ganhos": fechados_ganhos,
        "fechados_perdidos": fechados_perdidos,
        "total_novos": total_novos,
        "total_em_proposta": total_em_proposta,
        "total_ganhos": total_ganhos,
        "total_perdidos": total_perdidos,
        "valor_novos": valor_novos,
        "valor_em_proposta": valor_em_proposta,
        "valor_ganhos": valor_ganhos,
        "valor_perdidos": valor_perdidos,
        "total_negocios": total_negocios,
        "valor_total": valor_total,
        "taxa_fechamento": taxa_fechamento,
    }

    return templates.TemplateResponse("funil.html", contexto)


@app.get("/indicadores", response_class=HTMLResponse, tags=["Interface"])
def painel_indicadores(
    request: Request,
    inicio: Optional[str] = None,
    fim: Optional[str] = None,
    db: Session = Depends(obter_sessao),
):
    """
    Painel de indicadores por funcionário.
    Permite filtrar por janela de datas (criação/atualização/fechamento).
    """
    # 1) Definir intervalo de datas (padrão: últimos 30 dias)
    if not inicio or not fim:
        fim_data = date.today()
        inicio_data = fim_data - timedelta(days=29)
    else:
        try:
            inicio_data = datetime.strptime(inicio, "%Y-%m-%d").date()
            fim_data = datetime.strptime(fim, "%Y-%m-%d").date()
        except ValueError:
            fim_data = date.today()
            inicio_data = fim_data - timedelta(days=29)

    if inicio_data > fim_data:
        inicio_data, fim_data = fim_data, inicio_data

    inicio_str = inicio_data.isoformat()
    fim_str = fim_data.isoformat()

    # 2) Carregar negócios e funcionários
    negocios: List[Negocio] = db.query(Negocio).all()
    funcionarios: List[Funcionario] = (
        db.query(Funcionario)
        .filter(Funcionario.ativo == True)  # noqa: E712
        .order_by(Funcionario.nome)
        .all()
    )

    # 3) Global: negócios recebidos e ganhos no período
    negocios_recebidos_global: List[Negocio] = []
    ganhos_global: List[Negocio] = []

    for n in negocios:
        if n.criado_em:
            dc = n.criado_em.date()
            if inicio_data <= dc <= fim_data:
                negocios_recebidos_global.append(n)

        if n.fase == "fechado_ganho" and n.data_fechamento:
            if inicio_data <= n.data_fechamento <= fim_data:
                ganhos_global.append(n)

    ciclos_global: List[int] = []
    for n in ganhos_global:
        if n.criado_em:
            ciclos_global.append(
                (n.data_fechamento - n.criado_em.date()).days  # type: ignore[arg-type]
            )

    if ciclos_global:
        ciclo_medio_global = round(sum(ciclos_global) / len(ciclos_global), 1)
    else:
        ciclo_medio_global = 0.0

    total_negocios_recebidos_global = len(negocios_recebidos_global)
    total_negocios_ganhos_global = len(ganhos_global)

    if total_negocios_recebidos_global > 0:
        taxa_conversao_global = round(
            (total_negocios_ganhos_global / total_negocios_recebidos_global) * 100
        )
    else:
        taxa_conversao_global = 0

    # 4) Métricas por funcionário
    metricas_funcionarios: List[Dict] = []
    valor_max_vendedor = 0.0

    for f in funcionarios:
        negocios_f = [n for n in negocios if n.responsavel_id == f.id]

        recebidos_f: List[Negocio] = []
        trabalhados_ids = set()
        ganhos_f: List[Negocio] = []

        for n in negocios_f:
            if n.criado_em:
                dc = n.criado_em.date()
                if inicio_data <= dc <= fim_data:
                    recebidos_f.append(n)
                    trabalhados_ids.add(n.id)

            if n.atualizado_em:
                da = n.atualizado_em.date()
                if inicio_data <= da <= fim_data:
                    trabalhados_ids.add(n.id)

            if n.fase == "fechado_ganho" and n.data_fechamento:
                if inicio_data <= n.data_fechamento <= fim_data:
                    ganhos_f.append(n)

        negocios_recebidos_f = len(recebidos_f)
        negocios_trabalhados_f = len(trabalhados_ids)
        negocios_ganhos_f = len(ganhos_f)

        ciclos_f: List[int] = []
        for n in ganhos_f:
            if n.criado_em:
                ciclos_f.append(
                    (n.data_fechamento - n.criado_em.date()).days  # type: ignore[arg-type]
                )

        if ciclos_f:
            ciclo_medio_f = round(sum(ciclos_f) / len(ciclos_f), 1)
        else:
            ciclo_medio_f = 0.0

        if negocios_recebidos_f > 0:
            taxa_conversao_f = round(
                (negocios_ganhos_f / negocios_recebidos_f) * 100
            )
        else:
            taxa_conversao_f = 0

        valor_ganho_f = sum(n.valor_previsto or 0 for n in ganhos_f)
        valor_max_vendedor = max(valor_max_vendedor, valor_ganho_f)

        metricas_funcionarios.append(
            {
                "funcionario": f,
                "negocios_recebidos": negocios_recebidos_f,
                "negocios_trabalhados": negocios_trabalhados_f,
                "negocios_ganhos": negocios_ganhos_f,
                "ciclo_medio": ciclo_medio_f,
                "taxa_conversao": taxa_conversao_f,
                "valor_ganho": valor_ganho_f,
            }
        )

    # Normalizar largura da barra de vendas por funcionário
    for m in metricas_funcionarios:
        if valor_max_vendedor > 0:
            m["largura_barra"] = round(
                (m["valor_ganho"] * 100) / valor_max_vendedor
            )
        else:
            m["largura_barra"] = 0

    # 5) Vendas por origem (somente negócios ganhos no período)
    vendas_origem_dict: Dict[str, Dict[str, float]] = {}
    valor_max_origem = 0.0

    for n in ganhos_global:
        origem = n.origem or "Não informada"
        if origem not in vendas_origem_dict:
            vendas_origem_dict[origem] = {"quantidade": 0, "valor": 0.0}
        vendas_origem_dict[origem]["quantidade"] += 1
        valor = float(n.valor_previsto) if n.valor_previsto is not None else 0.0
        vendas_origem_dict[origem]["valor"] += valor

        valor_max_origem = max(valor_max_origem, vendas_origem_dict[origem]["valor"])

    vendas_por_origem: List[Dict] = []
    for origem, dados in vendas_origem_dict.items():
        if valor_max_origem > 0:
            largura = round((dados["valor"] * 100) / valor_max_origem)
        else:
            largura = 0
        vendas_por_origem.append(
            {
                "origem": origem,
                "quantidade": dados["quantidade"],
                "valor": dados["valor"],
                "largura_barra": largura,
            }
        )

    # 6) Produtividade por dia (negócios ganhos por dia de fechamento)
    produtividade_dict: Dict[date, int] = {}
    for n in ganhos_global:
        if n.data_fechamento:
            d = n.data_fechamento
            produtividade_dict[d] = produtividade_dict.get(d, 0) + 1

    produtividade_por_dia: List[Dict] = []
    for d, qtd in sorted(produtividade_dict.items(), key=lambda item: item[0]):
        produtividade_por_dia.append({"data": d, "quantidade": qtd})

    max_produtividade = (
        max((p["quantidade"] for p in produtividade_por_dia), default=0)
    )

    for p in produtividade_por_dia:
        if max_produtividade > 0:
            p["largura_barra"] = round(
                (p["quantidade"] * 100) / max_produtividade
            )
        else:
            p["largura_barra"] = 0

    contexto = {
        "request": request,
        "inicio": inicio_str,
        "fim": fim_str,
        "total_negocios_recebidos_global": total_negocios_recebidos_global,
        "total_negocios_ganhos_global": total_negocios_ganhos_global,
        "ciclo_medio_global": ciclo_medio_global,
        "taxa_conversao_global": taxa_conversao_global,
        "metricas_funcionarios": metricas_funcionarios,
        "vendas_por_origem": vendas_por_origem,
        "produtividade_por_dia": produtividade_por_dia,
    }

    return templates.TemplateResponse("indicadores.html", contexto)
@app.post("/dev/seed", tags=["Dev"])
def seed_dados_dev(
    limpar: bool = True,
    dias_passado: int = 60,
    qtd_funcionarios: int = 5,
    qtd_contatos: int = 40,
    qtd_negocios: int = 120,
    db: Session = Depends(obter_sessao),
):
    """
    Popula o banco com dados de exemplo para desenvolvimento.

    Parâmetros:
    - limpar: se True, apaga todos os Funcionários, Contatos e Negócios antes de criar os dados.
    - dias_passado: intervalo (em dias) para jogar as datas no passado.
    - qtd_funcionarios: quantos funcionários criar.
    - qtd_contatos: quantos contatos criar.
    - qtd_negocios: quantos negócios criar.
    """
    # 1) Limpar dados existentes (opcional)
    if limpar:
        db.query(Negocio).delete(synchronize_session=False)
        db.query(Contato).delete(synchronize_session=False)
        db.query(Funcionario).delete(synchronize_session=False)
        db.commit()

    # 2) Criar funcionários fake
    primeiros_nomes = [
        "Ana", "Bruno", "Carla", "Daniel", "Eduarda",
        "Felipe", "Gabriela", "Henrique", "Isabela", "João",
        "Larissa", "Marcos", "Natalia", "Otávio", "Paula",
    ]
    sobrenomes = [
        "Silva", "Souza", "Oliveira", "Pereira", "Costa",
        "Almeida", "Gomes", "Ribeiro", "Carvalho", "Santos",
    ]
    cargos = ["Vendedor", "Closer", "SDR", "Gestor Comercial", "Pré-vendas"]

    funcionarios = []
    for i in range(qtd_funcionarios):
        nome = f"{random.choice(primeiros_nomes)} {random.choice(sobrenomes)}"
        email = f"vendedor{i+1}@empresa.com".lower()
        cargo = random.choice(cargos)

        func = Funcionario(
            nome=nome,
            email=email,
            cargo=cargo,
            ativo=True,
        )
        db.add(func)
        funcionarios.append(func)

    db.commit()
    for f in funcionarios:
        db.refresh(f)

    # 3) Criar contatos fake
    nomes_contato = [
        "Carlos", "Fernanda", "Rodrigo", "Juliana", "Thiago",
        "Patrícia", "André", "Luciana", "Vinícius", "Marta",
        "Rafael", "Camila", "Diego", "Bianca", "Gustavo",
    ]
    empresas = [
        "Tech Manaus", "Inova Digital", "Amazon Solutions",
        "Comercial Rio Negro", "Studio Criar", "Global Contábil",
        "Impacto Vendas", "Norte Serviços", "Amazônia Solar",
    ]
    telefones_base = ["9299990000", "9298880000", "9299770000"]

    situacoes = ["lead", "cliente", "inativo"]

    contatos = []
    for i in range(qtd_contatos):
        nome = random.choice(nomes_contato) + f" {random.choice(sobrenomes)}"
        empresa = random.choice(empresas)
        email = f"{nome.split()[0].lower()}{i+1}@{empresa.split()[0].lower()}.com"
        telefone = random.choice(telefones_base)[:-1] + str(i % 10)

        situacao = random.choices(
            population=situacoes,
            weights=[0.6, 0.3, 0.1],
            k=1,
        )[0]

        c = Contato(
            nome=nome,
            email=email,
            telefone=telefone,
            empresa=empresa,
            origem=random.choice(["whatsapp", "site", "instagram", "indicação", "ligação"]),
            situacao=situacao,
        )
        db.add(c)
        contatos.append(c)

    db.commit()
    for c in contatos:
        db.refresh(c)

    # 4) Criar negócios fake
    hoje = date.today()
    fases = ["novo", "em_proposta", "fechado_ganho", "fechado_perdido"]
    origens_negocio = ["whatsapp", "site", "instagram", "indicação", "ligação"]

    negocios_criados = 0
    ganhos = 0
    perdidos = 0

    for i in range(qtd_negocios):
        if not contatos or not funcionarios:
            break

        contato = random.choice(contatos)
        responsavel = random.choice(funcionarios)

        dias_atras = random.randint(0, max(dias_passado, 1))
        data_criacao = hoje - timedelta(days=dias_atras)

        fase = random.choices(
            population=fases,
            weights=[0.35, 0.30, 0.25, 0.10],
            k=1,
        )[0]

        valor = round(random.uniform(500, 20000), 2)

        probabilidade = None
        if fase == "novo":
            probabilidade = random.choice([10, 20, 30, 40])
        elif fase == "em_proposta":
            probabilidade = random.choice([40, 50, 60, 70])
        elif fase == "fechado_ganho":
            probabilidade = random.choice([80, 90, 100])
        elif fase == "fechado_perdido":
            probabilidade = random.choice([5, 10, 15])

        data_prevista = data_criacao + timedelta(days=random.randint(5, 30))
        data_fechamento = None

        if fase in ["fechado_ganho", "fechado_perdido"]:
            dias_para_fechar = random.randint(1, 45)
            data_fechamento = data_criacao + timedelta(days=dias_para_fechar)
            if data_fechamento > hoje:
                data_fechamento = hoje

        n = Negocio(
            titulo=f"Projeto #{i+1} - {contato.empresa}",
            descricao=f"Negócio gerado automaticamente para testes (contato: {contato.nome}).",
            valor_previsto=valor,
            fase=fase,
            origem=random.choice(origens_negocio),
            probabilidade=probabilidade,
            contato_id=contato.id,
            responsavel_id=responsavel.id,
            data_prevista_fechamento=data_prevista,
            data_fechamento=data_fechamento,
        )

        # Força a data de criação manualmente para simular histórico
        n.criado_em = datetime.combine(data_criacao, datetime.min.time())

        db.add(n)
        negocios_criados += 1

        if fase == "fechado_ganho":
            ganhos += 1
        if fase == "fechado_perdido":
            perdidos += 1

    db.commit()

    return {
        "mensagem": "Seed de desenvolvimento executada com sucesso.",
        "parametros": {
            "limpar": limpar,
            "dias_passado": dias_passado,
            "qtd_funcionarios": qtd_funcionarios,
            "qtd_contatos": qtd_contatos,
            "qtd_negocios": qtd_negocios,
        },
        "resumo": {
            "funcionarios_criados": len(funcionarios),
            "contatos_criados": len(contatos),
            "negocios_criados": negocios_criados,
            "negocios_ganhos": ganhos,
            "negocios_perdidos": perdidos,
        },
    }


# Inclui as rotas de contatos, negócios e funcionários sob /api/v1
app.include_router(roteador_contatos, prefix="/api/v1")
app.include_router(roteador_negocios, prefix="/api/v1")
app.include_router(roteador_funcionarios, prefix="/api/v1")

