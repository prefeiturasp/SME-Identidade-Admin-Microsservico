# SME-Identidade-Admin-Microsservico

O SME-Identidade-Admin-Microsservico é responsável pela administração e gestão dos recursos de identidade utilizados pelos sistemas da SME-SP.

Atuando como uma camada de gerenciamento sobre a Admin API, o serviço abstrai e centraliza operações administrativas relacionadas a clients, roles, grupos e mappers, disponibilizando APIs padronizadas para os consumidores internos da plataforma.

## Estrutura do repositório

```
.
├── apps/
│   ├── core/           # cliente HTTP
│   └── autenticacao/   # domínio autenticação: views, services, serializers
│   └── keycloak_admin/ # administração dos recursos do Keycloak
│       ├── api/        # componentes compartilhados da API
│       ├── usuarios/   # administração de usuários
│       ├── clientes/   # administração de clientes
│       ├── permissoes/ # administração de Realm e Client Roles
│       ├── grupos/     # administração de grupos
│       └── sessoes/    # administração de sessões
├── config/             # settings, urls, wsgi
├── docs/               # Documentação Sphinx
├── requirements/
│   ├── base.txt        # dependências de produção
│   └── local.txt       # base + ferramentas de desenvolvimento
├── scripts/            # Scripts auxiliares
└── manage.py
```

---

### apps/core

| Módulo | Responsabilidade |
|---|---|
| `api/views.py` | Endpoints da aplicação, incluindo o health check do serviço |
| `api/serializers.py` | Serialização e validação de dados de entrada e saída |
| `api/urls.py` | Registro e roteamento das URLs da aplicação |

### apps/autenticacao

| Módulo | Responsabilidade |
|---|---|
| `api/autenticacao.py` | Implementa a autenticação dos endpoints por **API Key**, validando a chave enviada no cabeçalho HTTP configurado pela aplicação. |

### apps/keycloak_admin

| Módulo       | Responsabilidade                               |
| ------------ | ---------------------------------------------- |
| `usuarios`   | Consulta e gerenciamento de usuários           |
| `clientes`   | Consulta, criação e atualização de clients     |
| `permissoes` | Gerenciamento de Realm Roles e Client Roles    |
| `grupos`     | Gerenciamento de grupos e associação de roles  |
| `sessoes`    | Consulta e encerramento de sessões de usuários |

---

## Requisitos

- Python 3.12+
- Docker e Docker Compose
- OpenSSL (apenas para geração das chaves em ambiente de desenvolvimento)

## Instalação para desenvolvimento

Crie um ambiente virtual e instale as dependências locais:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements/local.txt
```

Instale os hooks do `pre-commit` antes de criar o primeiro commit:

```bash
pre-commit install
pre-commit run --all-files
```

O `pre-commit install` é obrigatório no setup local. Depois de instalado, os
formatadores e validadores são executados automaticamente em cada commit,
evitando o envio de código fora do padrão do projeto.

## Configuração do ambiente

```bash
cp .env.example .env
make build
make run
```

**Geral**

| Variável | Padrão | Descrição |
|---|---|---|
| `DJANGO_SECRET_KEY` | — | Chave secreta do Django |
| `DJANGO_DEBUG` | `1` | Ativa o modo debug (`0` em produção) |
| `DJANGO_ALLOWED_HOSTS` | `*` | Hosts permitidos, separados por vírgula |
| `API_KEY` | - | Chave de autenticação utilizada para validar o acesso às APIs protegidas pela aplicação. |
| `API_KEY_HEADER` | `X-API-Key` | Nome do cabeçalho HTTP utilizado para enviar a chave de autenticação nas requisições. |
| `KEYCLOAK_URL_SERVIDOR`     | —      | URL do servidor Keycloak                              |
| `KEYCLOAK_REALM`          | —      | Realm utilizado nas operações administrativas         |
| `KEYCLOAK_USUARIO_ADMIN` | —      | Usuário administrativo utilizado pelo serviço         |
| `KEYCLOAK_SENHA_ADMIN` | —      | Senha do usuário administrativo                       |
| `KEYCLOAK_VERIFICAR_SSL`     | —      | Define se o certificado SSL do Keycloak será validado |
| `KEYCLOAK_LOGIN_CLIENT_ID` | — | Identificador do client utilizado para autenticação no Keycloak. |
| `KEYCLOAK_LOGIN_CLIENT_SECRET` | — | Credencial secreta do client utilizado para autenticação no Keycloak. |

## Atalhos Make

Use `make help` para listar todos os comandos disponíveis. Os principais:

**Ambiente**

| Comando | Descrição |
|---|---|
| `make run` | Sobe o containers em modo dev (porta 8002) |
| `make build` | Rebuild da imagem dev |
| `make stop` | Para e remove containers |

**Testes**

| Comando | Descrição |
|---|---|
| `make test` | Suite completa com cobertura ≥ 80% |
| `make test-core` | Apenas `apps.core` |

**Qualidade**

| Comando | Descrição |
|---|---|
| `make lint` | ruff + black + isort + mypy |
| `make coverage` | Relatório HTML em `docs/_cov/` |
| `make schema` | Gera schema OpenAPI em `schema.yml` |
| `make docs` | Gera documentação Sphinx em `docs/_build/html/` |

## Endpoints

Consulte o Swagger em `identidade-admin/api/v1/docs/` para a lista completa de rotas com parâmetros e exemplos de resposta.