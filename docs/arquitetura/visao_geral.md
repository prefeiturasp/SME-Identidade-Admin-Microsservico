# Visão geral da arquitetura

## Objetivo

O **SME-Identidade-Admin-Microsserviço** é responsável por centralizar e
disponibilizar operações administrativas relacionadas à gestão de identidade
do ecossistema SME.

O microsserviço atua como uma camada intermediária entre os consumidores
internos da plataforma e o provedor de identidade **Keycloak**, evitando que
os consumidores precisem realizar diretamente operações administrativas
contra a Admin API do Keycloak.

Através dessa camada, as operações administrativas são padronizadas,
controladas e expostas por meio de APIs próprias do microsserviço.

Atualmente, o serviço disponibiliza operações administrativas para:

- usuários;
- clientes;
- permissões;
- grupos;
- sessões.

---

## Responsabilidades

O Admin-MS possui como principais responsabilidades:

- disponibilizar APIs administrativas para os recursos de identidade;
- validar os dados recebidos pelos consumidores;
- centralizar as regras de negócio relacionadas às operações administrativas;
- encapsular a comunicação com o Keycloak;
- controlar o acesso às APIs administrativas;
- padronizar as respostas da aplicação;
- tratar e propagar erros provenientes da integração com o Keycloak;
- evitar que consumidores dependam diretamente da estrutura da Admin API.

O microsserviço **não substitui o Keycloak**.

Sua responsabilidade é fornecer uma camada controlada e padronizada para
acesso às funcionalidades administrativas disponibilizadas pelo provedor
de identidade.

---

## Visão arquitetural

O fluxo principal da aplicação pode ser representado da seguinte forma:

```text
┌──────────────────────┐
│     Consumidor       │
│      interno         │
└──────────┬───────────┘
           │
           │ HTTP
           ▼
┌──────────────────────┐
│       Admin-MS       │
│                      │
│  API / Views         │
│       │              │
│       ▼              │
│  Serializers         │
│       │              │
│       ▼              │
│  Services            │
│       │              │
│       ▼              │
│  keycloak_admin      │
└──────────┬───────────┘
           │
           │ python-keycloak
           ▼
┌──────────────────────┐
│   Keycloak Admin API │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│       Keycloak       │
└──────────────────────┘
````

O consumidor não precisa conhecer os detalhes da comunicação com o
Keycloak. A requisição é recebida pelo Admin-MS, validada, processada pela
camada de serviço e encaminhada ao Keycloak através da integração
administrativa.

---

## Organização da aplicação

A aplicação utiliza Django como framework principal e organiza suas
funcionalidades em módulos dentro do diretório `apps`.

A estrutura relacionada à administração do Keycloak é organizada da seguinte
forma:

```text
apps/
└── keycloak_admin/
    │
    ├── api/
    │   ├── base.py
    │   ├── serializers.py
    │   └── ...
    │
    ├── usuarios/
    │   ├── api/
    │   │   ├── serializers.py
    │   │   ├── urls.py
    │   │   └── views.py
    │   ├── services.py
    │   └── testes/
    │
    ├── clientes/
    │   ├── api/
    │   ├── services.py
    │   └── testes/
    │
    ├── permissoes/
    │   ├── api/
    │   ├── services.py
    │   └── testes/
    │
    ├── grupos/
    │   ├── api/
    │   ├── services.py
    │   └── testes/
    │
    └── sessoes/
        ├── api/
        ├── services.py
        └── testes/
```

Cada recurso administrativo possui sua própria organização interna,
mantendo separadas as responsabilidades de API, regras de negócio e testes.

---

## Módulo `keycloak_admin`

O módulo `keycloak_admin` é o núcleo responsável pelas operações
administrativas relacionadas ao Keycloak.

Sua principal finalidade é centralizar a integração administrativa e evitar
que diferentes partes da aplicação precisem implementar diretamente a
comunicação com o provedor de identidade.

Os recursos administrativos são separados por domínio:

| Módulo       | Responsabilidade                                     |
| ------------ | ---------------------------------------------------- |
| `usuarios`   | Consulta e gerenciamento de usuários                 |
| `clientes`   | Consulta, criação e atualização de clients           |
| `permissoes` | Gerenciamento de Realm Roles e Client Roles          |
| `grupos`     | Consulta, criação, atualização e associação de roles |
| `sessoes`    | Consulta e encerramento de sessões de usuários       |

Essa divisão permite que cada domínio possua suas próprias APIs,
serializers, serviços e testes.

---

## Camadas da aplicação

A comunicação interna do Admin-MS segue uma separação por responsabilidades.

### Views

As views são responsáveis pela camada HTTP da aplicação.

Suas responsabilidades incluem:

* receber a requisição;
* obter parâmetros de rota;
* validar os dados através dos serializers;
* chamar o serviço responsável pela operação;
* serializar os dados de resposta;
* retornar a resposta HTTP adequada.

As views não devem conter regras de negócio relacionadas diretamente ao
Keycloak.

Exemplo:

```text
GET /clientes/
       │
       ▼
ClientListCreateView
       │
       ▼
ClientConsultaSerializer
       │
       ▼
ClientService.consultar()
```

---

### Serializers

Os serializers são responsáveis pela validação e representação dos dados
da API.

Eles definem:

* campos obrigatórios;
* campos opcionais;
* tipos de dados;
* limites;
* valores padrão;
* regras de validação da entrada;
* estrutura das respostas.

A validação dos dados recebidos deve ocorrer antes da chamada ao serviço.

Exemplo:

```text
Requisição HTTP
      │
      ▼
Serializer
      │
      ├── inválido ──► HTTP 400
      │
      ▼
Dados validados
      │
      ▼
Service
```

---

### Services

Os services concentram as operações administrativas e a integração com o
Keycloak.

Essa camada é responsável por:

* executar as operações administrativas;
* obter a conexão administrativa com o Keycloak;
* utilizar os métodos disponibilizados pelo `python-keycloak`;
* transformar dados quando necessário;
* tratar particularidades da Admin API;
* manter as views independentes da implementação do cliente Keycloak.

Exemplo:

```text
ClientService
      │
      ▼
KeycloakAdmin
      │
      ▼
python-keycloak
      │
      ▼
Keycloak Admin API
```

Essa separação permite substituir ou alterar a implementação da integração
com o Keycloak sem precisar modificar diretamente os endpoints da API.

---

## Integração com o Keycloak

A comunicação administrativa com o Keycloak é realizada utilizando a
biblioteca `python-keycloak`.

O Admin-MS não implementa diretamente as requisições HTTP da Admin API.
Em vez disso, utiliza a abstração fornecida pelo cliente Python.

O fluxo de integração é:

```text
Admin-MS
   │
   ▼
Service
   │
   ▼
KeycloakAdmin
   │
   ▼
python-keycloak
   │
   ▼
Keycloak Admin API
```

Por exemplo, uma operação de consulta de usuários segue conceitualmente o
fluxo:

```text
GET /usuarios/
      │
      ▼
UsuarioListView
      │
      ▼
UsuarioService.consultar()
      │
      ▼
KeycloakAdmin.get_users()
      │
      ▼
Keycloak Admin API
      │
      ▼
Keycloak
```

O mesmo princípio é utilizado pelos demais recursos administrativos.

---

## Recursos administrados

### Usuários

O módulo de usuários disponibiliza operações relacionadas ao gerenciamento
dos usuários existentes no Keycloak.

Entre as operações estão:

* consulta de usuários;
* consulta por identificadores ou atributos suportados;
* criação de usuários;
* atualização de usuários;
* alteração de senha.
* alteração do e-mail.
* associação de Realm Roles/ Clients Roles/ Grupos;
* desassociação de Realm Roles/ Clients Roles/ Grupos;

As operações são encapsuladas pelo `UsuarioService`.

---

### Clientes

O módulo de clientes permite administrar as aplicações registradas no
Keycloak.

Entre as operações estão:

* consulta de clientes;
* consulta de um cliente específico;
* criação de clientes;
* atualização de clientes.

As operações são encapsuladas pelo `ClientService`.

---

### Permissões

O módulo de permissões administra roles do Keycloak.

São tratados dois tipos de roles:

* **Realm Roles**;
* **Client Roles**.

A separação é importante porque as Client Roles pertencem a um client
específico, enquanto as Realm Roles pertencem diretamente ao Realm.

O `RoleService` encapsula as operações de consulta, criação e atualização
dessas permissões.

---

### Grupos

O módulo de grupos permite administrar grupos do Realm.

Entre as operações estão:

* consulta de grupos;
* criação de grupos;
* atualização de grupos;
* associação de Realm Roles;
* desassociação de Realm Roles;
* associação de Client Roles;
* desassociação de Client Roles.

As operações são encapsuladas pelo `GrupoService`.

---

### Sessões

O módulo de sessões possui como objetivo administrar sessões de um usuário
específico.

São disponibilizadas operações para:

* consultar as sessões ativas de um usuário;
* encerrar as sessões ativas de um usuário.

A operação de encerramento é direcionada exclusivamente ao usuário informado,
não realizando logout global de todo o Realm ou de todos os usuários.

As operações são encapsuladas pelo `SessaoService`.

---

## Autenticação da API

O acesso às APIs administrativas é protegido através de `API Key`.

O mecanismo de autenticação é aplicado antes da execução das operações
administrativas.

O fluxo pode ser representado da seguinte forma:

```text
Consumidor
    │
    │ X-API-Key
    ▼
Admin-MS
    │
    ▼
Autenticação
    │
    ├── inválida ──► HTTP 401
    │
    ▼
API administrativa
    │
    ▼
Service
    │
    ▼
Keycloak
```

A autenticação da API do Admin-MS é independente das credenciais utilizadas
internamente para comunicação administrativa com o Keycloak.

Isso significa que existem dois contextos distintos:

1. autenticação do consumidor perante o Admin-MS;
2. autenticação administrativa do Admin-MS perante o Keycloak.

---

## Separação entre consumidor e Keycloak

Um dos principais objetivos arquiteturais do Admin-MS é evitar o acoplamento
direto dos consumidores com a Admin API do Keycloak.

Sem o Admin-MS, um consumidor precisaria conhecer detalhes como:

```text
Consumidor
   │
   ├── autenticação administrativa
   ├── endpoints do Keycloak
   ├── formatos da Admin API
   ├── regras específicas
   └── tratamento de erros
```

Com o Admin-MS:

```text
Consumidor
   │
   ▼
Admin-MS
   │
   ├── autenticação
   ├── validação
   ├── regras administrativas
   ├── transformação
   └── integração
   │
   ▼
Keycloak
```

Dessa forma, alterações na implementação da integração podem ser
concentradas no Admin-MS, reduzindo o acoplamento dos consumidores ao
provedor de identidade.