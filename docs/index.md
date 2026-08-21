# SME Identidade Admin Microsserviço

Documentação técnica do serviço responsável pela administração e gestão dos recursos de identidade do ecossistema SME por meio da integração com a Admin API.

O microsserviço atua como uma camada de gerenciamento, abstraindo as operações administrativas relacionadas a clients, roles, grupos e mappers. Sua função é centralizar e padronizar os fluxos de administração da identidade, disponibilizando APIs específicas para os consumidores internos da plataforma.

Além das operações administrativas, o serviço disponibiliza um portal de autosserviço por meio de uma camada bridge, permitindo que operações de gestão de identidade sejam realizadas de forma controlada e desacoplada da interface administrativa nativa do provedor de autenticação.

```{toctree}
:maxdepth: 2
:caption: Conteúdo

api
```