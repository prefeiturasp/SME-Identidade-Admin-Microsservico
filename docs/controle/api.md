# API

Esta seção apresenta uma visão geral dos recursos disponibilizados pelo
**SME-Identidade-Admin-Microsserviço**.

## Autenticação

Todos os endpoints administrativos utilizam autenticação por **API Key**.

A chave deve ser enviada no cabeçalho HTTP configurado pela variável de
ambiente `API_KEY_HEADER`.

Exemplo:

```text
X-API-Key: <API_KEY>
````

Caso a chave seja inválida ou esteja ausente, a requisição será rejeitada
com **HTTP 401 (Unauthorized)**.

---

## Recursos disponíveis

### Health Check

Endpoint utilizado para verificar a disponibilidade da aplicação.

| Método | Endpoint                           | Descrição                              |
| ------ | ---------------------------------- | -------------------------------------- |
| GET    | `/identidade-admin/api/v1/health/` | Verifica se o serviço está disponível. |

---

### Usuários

Conjunto de endpoints responsáveis pelo gerenciamento administrativo
dos usuários no Keycloak.

| Método | Endpoint                                                | Descrição                         |
| ------ | ------------------------------------------------------- | --------------------------------- |
| GET    | `/identidade-admin/api/v1/usuarios/`                    | Consulta usuários.                |
| POST   | `/identidade-admin/api/v1/usuarios/`                    | Cria um usuário.                  |
| PATCH  | `/identidade-admin/api/v1/usuarios/{usuario_id}/`       | Atualiza um usuário.              |
| PATCH  | `/identidade-admin/api/v1/usuarios/{usuario_id}/senha/` | Altera a senha de um usuário.     |
| PATCH  | `/identidade-admin/api/v1/usuarios/{usuario_id}/email/` | Altera o e-mail de um usuário.    |
| POST   | `/identidade-admin/api/v1/usuarios/{usuario_id}/grupos/`| Associa usuário ao um grupo.   |
| PATCH  | `/identidade-admin/api/v1/usuarios/{usuario_id}/grupos/`| Desassocia usuário ao um grupo.|
| POST   | `/identidade-admin/api/v1/usuarios/{usuario_id}/permissoes/cliente/`| Associa usuário ao client-role.|
| PATCH  | `/identidade-admin/api/v1/usuarios/{usuario_id}/permissoes/cliente/`| Desassocia usuário ao client-role.|
| POST   | `/identidade-admin/api/v1/usuarios/{usuario_id}/permissoes/realm/`| Associa usuário ao realm-role.|
| PATCH  | `/identidade-admin/api/v1/usuarios/{usuario_id}/permissoes/realm/`| Desassocia usuário ao realm-role.|

---

### Clientes

Conjunto de endpoints responsáveis pelo gerenciamento dos clients
registrados no Keycloak.

| Método | Endpoint                                           | Descrição           |
| ------ | -------------------------------------------------- | ------------------- |
| GET    | `/identidade-admin/api/v1/clientes/`               | Consulta clients.   |
| POST   | `/identidade-admin/api/v1/clientes/`               | Cria um client.     |
| PATCH  | `/identidade-admin/api/v1/clientes/{client_uuid}/` | Atualiza um client. |

---

### Permissões

Conjunto de endpoints responsáveis pelo gerenciamento de **Realm Roles**
e **Client Roles**.

#### Realm Roles

| Método | Endpoint                                            | Descrição                |
| ------ | --------------------------------------------------- | ------------------------ |
| GET    | `/identidade-admin/api/v1/permissoes/realm/`        | Consulta Realm Roles.    |
| POST   | `/identidade-admin/api/v1/permissoes/realm/`        | Cria uma Realm Role.     |
| PATCH  | `/identidade-admin/api/v1/permissoes/realm/{nome}/` | Atualiza uma Realm Role. |

#### Client Roles

| Método | Endpoint                                                             | Descrição                 |
| ------ | -------------------------------------------------------------------- | ------------------------- |
| GET    | `/identidade-admin/api/v1/permissoes/clientes/{client_uuid}/`        | Consulta Client Roles.    |
| POST   | `/identidade-admin/api/v1/permissoes/clientes/{client_uuid}/`        | Cria uma Client Role.     |
| PATCH  | `/identidade-admin/api/v1/permissoes/clientes/{client_uuid}/{nome}/` | Atualiza uma Client Role. |

---

### Grupos

Conjunto de endpoints responsáveis pelo gerenciamento de grupos e suas
associações de permissões.

| Método | Endpoint                                      | Descrição          |
| ------ | --------------------------------------------- | ------------------ |
| GET    | `/identidade-admin/api/v1/grupos/`            | Consulta grupos.   |
| POST   | `/identidade-admin/api/v1/grupos/`            | Cria um grupo.     |
| PATCH  | `/identidade-admin/api/v1/grupos/{grupo_id}/` | Atualiza um grupo. |

#### Roles de Realm

| Método | Endpoint                                                  | Descrição                           |
| ------ | --------------------------------------------------------- | ----------------------------------- |
| POST   | `/identidade-admin/api/v1/grupos/{grupo_id}/roles/realm/` | Associa uma Realm Role ao grupo.    |
| PATCH  | `/identidade-admin/api/v1/grupos/{grupo_id}/roles/realm/` | Desassocia uma Realm Role do grupo. |

#### Roles de Client

| Método | Endpoint                                                                  | Descrição                            |
| ------ | ------------------------------------------------------------------------- | ------------------------------------ |
| POST   | `/identidade-admin/api/v1/grupos/{grupo_id}/roles/cliente/{client_uuid}/` | Associa uma Client Role ao grupo.    |
| PATCH  | `/identidade-admin/api/v1/grupos/{grupo_id}/roles/cliente/{client_uuid}/` | Desassocia uma Client Role do grupo. |

---

### Sessões

Conjunto de endpoints responsáveis pela administração das sessões de
usuários.

| Método | Endpoint                                                         | Descrição                                 |
| ------ | ---------------------------------------------------------------- | ----------------------------------------- |
| GET    | `/identidade-admin/api/v1/usuarios/{usuario_id}/sessoes/`        | Consulta as sessões ativas de um usuário. |
| POST   | `/identidade-admin/api/v1/usuarios/{usuario_id}/sessoes/encerrar/` | Encerra as sessões ativas de um usuário.  |

---

# OpenAPI

A documentação completa da API pode ser consultada através do Swagger da
aplicação.

Ela inclui:

* contratos de requisição e resposta;
* parâmetros;
* payloads;
* schemas;
* códigos de resposta;
* exemplos de utilização.

A documentação completa da API está disponível em:

* `/identidade-admin/api/v1/docs/`