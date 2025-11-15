# CRM em Construção 🧱

Sistema de **CRM genérico e extensível** desenvolvido em **Python + FastAPI**, pensado para:

- organizar **contatos** e **negócios** (funil de vendas),
- acompanhar **desempenho por funcionário**,
- gerar **indicadores de vendas**,
- e futuramente ser integrado com **n8n** para automações (WhatsApp, e-mail, tarefas etc.).

> ⚠️ Projeto em desenvolvimento ativo. A ideia é ser um CRM base, simples de entender, mas pronto para crescer.

---

## 🧰 Stack utilizada

- **Python** (3.11+ – testado com 3.13)
- **FastAPI** (API + rotas web)
- **Uvicorn** (servidor ASGI)
- **SQLAlchemy** (ORM / acesso ao banco)
- **Pydantic v2** (validação de dados)
- **Jinja2** (templates HTML)
- **Tailwind CSS via CDN** (estilo dos painéis e cards)
- **SQLite** (banco de dados local para desenvolvimento)

---

## 📂 Estrutura resumida do projeto

```text
crm/
  app/
    __init__.py
    main.py                 # ponto de entrada da aplicação FastAPI
    banco_dados.py          # conexão com o banco + sessão SQLAlchemy
    modelos/                # modelos ORM (tabelas)
      __init__.py
      contato.py
      negocio.py
      funcionario.py
    esquemas/               # esquemas Pydantic (entrada/saída da API)
      __init__.py
      contato.py
    api/                    # rotas de API REST
      __init__.py
      v1/
        __init__.py
        contatos.py
    interface/              # camada de interface web
      templates/
        base.html
        negocios.html
        contatos.html
        indicadores.html
      static/
        css/...
🚀 Como rodar localmente (Windows)
1. Clonar o repositório
powershell
Copiar código
git clone https://github.com/SEU-USUARIO/CRM-EM-CONSTRUCAO.git
cd CRM-EM-CONSTRUCAO  # ou o nome que você usou
Se o projeto já estiver na sua máquina (pasta crm), é só entrar na pasta:

powershell
Copiar código
cd C:\Users\paulo\crm
2. Criar e ativar o ambiente virtual
powershell
Copiar código
python -m venv .venv
.\.venv\Scripts\Activate.ps1
Você deve ver algo como:

text
Copiar código
(.venv) PS C:\Users\paulo\crm>
3. Instalar as dependências
powershell
Copiar código
pip install -r requirements.txt
4. Rodar o servidor
powershell
Copiar código
uvicorn app.main:app --reload
A aplicação ficará disponível em:

http://127.0.0.1:8000 → painel web

http://127.0.0.1:8000/docs → documentação interativa da API (Swagger)

🗄️ Banco de dados
Por padrão o projeto usa SQLite em arquivo (ideal para desenvolvimento).

A configuração da URL do banco está centralizada em app/banco_dados.py.
Se quiser usar outro banco (PostgreSQL, MySQL etc.), basta ajustar a DATABASE_URL ali.

Exemplo de URL para PostgreSQL:

python
Copiar código
DATABASE_URL = "postgresql+psycopg2://usuario:senha@localhost:5432/crm"
🌱 Seed de dados de desenvolvimento
O projeto tem uma rota para popular o banco com dados falsos (funcionários, contatos e negócios), útil para testar o painel de indicadores.

Rota
http
Copiar código
POST /dev/seed
Parâmetros de query
limpar (bool) – se true, apaga os dados atuais antes de inserir.

dias_passado (int) – quantos dias para trás distribuir as datas dos negócios.

qtd_funcionarios (int) – quantos funcionários criar.

qtd_contatos (int) – quantos contatos criar.

qtd_negocios (int) – quantos negócios criar.

Exemplo (via navegador / Swagger)
Acessar:

text
Copiar código
http://127.0.0.1:8000/docs
Chamar o endpoint:

text
Copiar código
POST /dev/seed?limpar=true&dias_passado=60&qtd_funcionarios=5&qtd_contatos=40&qtd_negocios=120
Depois disso o painel /indicadores já terá dados para exibir.

🖥️ Rotas principais (Web)
GET /
Painel geral / funil de negócios (kanban + cards avançados).

GET /negocios
Listagem de negócios cadastrados.

GET /contatos
Listagem de contatos.

GET /indicadores
Painel de indicadores por funcionário, com:

negócios recebidos / trabalhados / ganhos por funcionário,

ciclo médio de vendas (dias),

taxa de conversão,

valor ganho por funcionário,

vendas por origem (tráfego pago, indicação, instagram etc.),

produtividade por dia (gráfico de barras).

As telas usam Tailwind CSS via CDN, com layout escuro e cards bem visuais.

📡 Rotas principais (API REST)
Atualmente a API expõe principalmente o módulo de contatos.

GET /api/v1/contatos
Lista contatos.

POST /api/v1/contatos
Cria um novo contato.

GET /api/v1/contatos/{id}
Detalhe de um contato.

PUT /api/v1/contatos/{id}
Atualiza um contato.

DELETE /api/v1/contatos/{id}
Remove um contato.

Outros módulos (Negócios, Funcionários, Atividades etc.) podem seguir o mesmo padrão de separação em app/esquemas, app/modelos e app/api/v1.

🤖 Integração com n8n (ideia base)
Este CRM foi pensado para ser facilmente integrado com n8n usando o nó HTTP Request.

Alguns exemplos de fluxos possíveis:

Quando chegar um lead pelo WhatsApp
→ n8n chama POST /api/v1/contatos e cria o contato automaticamente.

Relatório diário de indicadores
→ n8n chama GET /indicadores ou um endpoint JSON específico
→ gera um resumo e envia no WhatsApp do gestor.

Atualização de negócio via formulário externo
→ n8n recebe os dados
→ chama rotas de negócios (quando criadas) para movimentar o funil.

🧭 Próximos passos (roadmap)
 Entidade Atividade (tarefas, ligações, reuniões, follow-ups).

 Módulo de Campanhas (origem dos negócios: tráfego pago, orgânico, indicação).

 Tela de Atendimento com linha do tempo por contato.

 API JSON específica para indicadores (/api/v1/indicadores) focada em integrações com n8n.

 Autenticação e multiusuário (login, permissões).

 Deploy em servidor (Docker, Railway, Fly.io, VPS etc.).

📜 Licença
Licença ainda não definida.
Você pode utilizar este projeto como base para estudos e personalização do seu próprio CRM.
Quando decidir abrir o código, basta adicionar um arquivo LICENSE (por exemplo, MIT).

