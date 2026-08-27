# Fluxo de integração com o Keycloak

## Fluxo geral

```text
Cliente
   │
   ▼
Admin-MS
   │
   ├── View
   ├── Serializer
   └── Service
        │
        ▼
   python-keycloak
        │
        ▼
   Keycloak Admin API
        │
        ▼
     Keycloak
````

## Processamento da requisição

1. O consumidor envia uma requisição para uma API administrativa.
2. O Admin-MS valida a autenticação e os dados recebidos.
3. A View encaminha a operação para o Service correspondente.
4. O Service utiliza o `python-keycloak` para executar a operação.
5. O Keycloak processa a solicitação através da Admin API.
6. O resultado retorna pelo mesmo fluxo até o consumidor.

## Exemplo

Uma consulta de usuários segue o fluxo:

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
python-keycloak
      │
      ▼
Keycloak Admin API
      │
      ▼
Keycloak
```

O Service é responsável por encapsular os detalhes da integração,
mantendo a API do Admin-MS independente da implementação interna do
`python-keycloak` e da Admin API do Keycloak.