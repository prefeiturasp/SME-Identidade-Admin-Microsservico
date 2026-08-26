"""Serviço de administração de clients no Keycloak."""

import logging
import re
import unicodedata
from typing import Any

from apps.keycloak_admin.admin_kc import KeycloakAdminService

logger = logging.getLogger(__name__)


class ClientService:
    """Centraliza as operações administrativas de clients no Keycloak.

    Este serviço encapsula as chamadas à Admin API do Keycloak,
    disponibilizando operações para criação, consulta e atualização
    de clients sem expor diretamente o cliente da biblioteca
    ``python-keycloak`` às camadas superiores da aplicação.
    """

    def __init__(
        self,
        admin: KeycloakAdminService | None = None,
    ) -> None:
        """Inicializa o serviço de administração de clients.

        Args:
            admin: Serviço responsável pela comunicação com o Keycloak.
                Quando não informado, uma nova instância é criada usando
                as configurações padrão da aplicação.
        """
        self.admin = admin or KeycloakAdminService()

    def criar(
        self,
        client_id: str,
        nome: str | None = None,
        descricao: str | None = None,
        habilitado: bool = True,
        client_publico: bool = False,
        protocolo: str = "openid-connect",
        redirect_uris: list[str] | None = None,
        web_origins: list[str] | None = None,
        atributos: dict[str, Any] | None = None,
    ) -> str:
        """Cria um client no realm configurado do Keycloak.

        O ``client_id`` recebido é normalizado antes da criação para
        garantir um identificador compatível com o padrão utilizado
        pela aplicação.

        Args:
            client_id: Identificador público do client. O valor é
                convertido para o formato slug antes da criação.
            nome: Nome de apresentação do client.
            descricao: Descrição do client.
            habilitado: Define se o client será criado habilitado.
            client_publico: Define se o client será público.
            protocolo: Protocolo utilizado pelo client.
            redirect_uris: Lista de URIs autorizadas para redirecionamento.
                Quando não informada, utiliza ``["*"]``.
            web_origins: Lista de origens web autorizadas. Quando não
                informada, utiliza ``["*"]``.
            atributos: Atributos adicionais do client.

        Returns:
            ID interno do client criado no Keycloak.
        """
        client_id = self._slugificar_client_id(client_id)

        payload = {
            "clientId": client_id,
            "name": nome,
            "description": descricao,
            "enabled": habilitado,
            "protocol": protocolo,
            "publicClient": client_publico,
            "standardFlowEnabled": True,
            "directAccessGrantsEnabled": False,
            "serviceAccountsEnabled": False,
            "redirectUris": redirect_uris or ["*"],
            "webOrigins": web_origins or ["*"],
            "attributes": atributos or {},
        }

        logger.info(
            "Criando client no Keycloak.",
            extra={"client_id": client_id},
        )

        return self.admin.executar(
            self.admin.cliente.create_client,
            payload=payload,
        )

    def consultar(
        self,
        client_uuid: str | None = None,
    ) -> list[dict[str, Any]]:
        """Consulta clients do realm configurado.

        Quando ``client_uuid`` é informado, a consulta é realizada
        diretamente pelo UUID interno do client. Caso contrário,
        todos os clients disponíveis no realm são consultados.

        Args:
            client_uuid: ID interno do client no Keycloak. Quando não
                informado, todos os clients do realm são retornados.

        Returns:
            Lista de clients com os campos normalizados para o contrato
            interno da aplicação.
        """
        logger.debug(
            "Consultando clients no Keycloak.",
            extra={
                "client_uuid": client_uuid,
            },
        )

        if client_uuid is not None:
            client = self.admin.executar(
                self.admin.cliente.get_client,
                client_id=client_uuid,
            )

            return [
                self._normalizar_client(client),
            ]

        clients = self.admin.executar(
            self.admin.cliente.get_clients,
        )

        return [self._normalizar_client(client) for client in clients]

    def atualizar(
        self,
        client_uuid: str,
        nome: str | None = None,
        descricao: str | None = None,
        habilitado: bool | None = None,
        client_publico: bool | None = None,
        protocolo: str | None = None,
        redirect_uris: list[str] | None = None,
        web_origins: list[str] | None = None,
        atributos: dict[str, Any] | None = None,
    ) -> None:
        """Atualiza parcialmente a configuração de um client.

        Somente os campos explicitamente informados são enviados ao
        Keycloak. Caso nenhum campo seja informado, nenhuma requisição
        é realizada.

        Args:
            client_uuid: ID interno do client no Keycloak.
            nome: Novo nome de apresentação do client.
            descricao: Nova descrição do client.
            habilitado: Define se o client ficará habilitado.
            client_publico: Define se o client será público.
            protocolo: Novo protocolo utilizado pelo client.
            redirect_uris: Nova lista de URIs autorizadas para
                redirecionamento.
            web_origins: Nova lista de origens web autorizadas.
            atributos: Novos atributos do client.
        """
        payload: dict[str, Any] = {}

        if nome is not None:
            payload["name"] = nome

        if descricao is not None:
            payload["description"] = descricao

        if habilitado is not None:
            payload["enabled"] = habilitado

        if client_publico is not None:
            payload["publicClient"] = client_publico

        if protocolo is not None:
            payload["protocol"] = protocolo

        if redirect_uris is not None:
            payload["redirectUris"] = redirect_uris

        if web_origins is not None:
            payload["webOrigins"] = web_origins

        if atributos is not None:
            payload["attributes"] = atributos

        if not payload:
            return

        logger.info(
            "Atualizando client no Keycloak.",
            extra={"client_uuid": client_uuid},
        )

        self.admin.executar(
            self.admin.cliente.update_client,
            client_id=client_uuid,
            payload=payload,
        )

    @staticmethod
    def _normalizar_client(
        client: dict[str, Any],
    ) -> dict[str, Any]:
        """Normaliza os dados de um client para o contrato da aplicação.

        A normalização evita que a estrutura retornada diretamente pela
        Admin API do Keycloak seja exposta às camadas superiores.

        Args:
            client: Dados do client retornados pelo Keycloak.

        Returns:
            Dicionário contendo os dados do client no formato utilizado
            internamente pela aplicação.
        """
        return {
            "id": client.get("id"),
            "client_id": client.get("clientId"),
            "nome": client.get("name"),
            "habilitado": client.get("enabled", False),
            "client_publico": client.get(
                "publicClient",
                False,
            ),
            "protocolo": client.get(
                "protocol",
                "openid-connect",
            ),
            "redirect_uris": client.get(
                "redirectUris",
                [],
            ),
            "web_origins": client.get(
                "webOrigins",
                [],
            ),
            "atributos": client.get(
                "attributes",
                {},
            ),
        }

    @staticmethod
    def _slugificar_client_id(nome: str) -> str:
        """Trata o nome informado em um ``client_id`` normalizado.

        A normalização remove acentos, substitui caracteres que não
        sejam alfanuméricos por hífens, remove hífens nas extremidades
        e converte o resultado para letras minúsculas.

        Quando o valor informado não produz um identificador válido,
        utiliza ``sistema-sem-nome`` como valor padrão.

        Args:
            nome: Nome utilizado como base para geração do ``client_id``.

        Returns:
            Identificador normalizado no formato slug.
        """
        valor = unicodedata.normalize("NFKD", nome or "")
        valor = valor.encode("ascii", "ignore").decode("ascii")
        valor = re.sub(r"[^a-zA-Z0-9]+", "-", valor)
        valor = valor.strip("-").lower()

        return valor or "sistema-sem-nome"
