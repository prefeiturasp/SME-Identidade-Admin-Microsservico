"""Serviço de administração de permissões no Keycloak."""

import logging
from typing import Any

from apps.keycloak_admin.admin_kc import KeycloakAdminService

logger = logging.getLogger(__name__)


class RoleService:
    """Centraliza as operações administrativas de permissões."""

    TIPOS_VALIDOS = {
        "realm",
        "client",
    }

    def __init__(
        self,
        admin: KeycloakAdminService | None = None,
    ) -> None:
        """Inicializa o serviço de administração de permissões.

        Args:
            admin: Serviço responsável pela comunicação com o Keycloak.
                Quando não informado, uma nova instância é criada.
        """
        self.admin = admin or KeycloakAdminService()

    def criar(
        self,
        nome: str,
        tipo: str = "realm",
        client_uuid: str | None = None,
        descricao: str | None = None,
        atributos: dict[str, Any] | None = None,
    ) -> None:
        """Cria uma permissão no Realm ou em um client.

        Args:
            nome: Nome da permissão.
            tipo: Tipo da permissão. Aceita ``realm`` ou ``client``.
            client_uuid: ID interno do client quando ``tipo`` for
                ``client``.
            descricao: Descrição da permissão.
            atributos: Atributos personalizados da permissão.

        Raises:
            ValueError: Se o tipo informado for inválido ou se
                ``client_uuid`` for incompatível com o tipo.
        """
        self._validar_tipo(
            tipo=tipo,
            client_uuid=client_uuid,
        )

        payload: dict[str, Any] = {
            "name": nome,
        }

        if descricao is not None:
            payload["description"] = descricao

        if atributos is not None:
            payload["attributes"] = atributos

        logger.info(
            "Criando permissão no Keycloak.",
            extra={
                "tipo": tipo,
                "nome": nome,
                "client_uuid": client_uuid,
            },
        )

        if tipo == "realm":
            self.admin.executar(
                self.admin.cliente.create_realm_role,
                payload=payload,
            )
            return

        assert client_uuid is not None

        self.admin.executar(
            self.admin.cliente.create_client_role,
            client_role_id=client_uuid,
            payload=payload,
        )

    def consultar(
        self,
        nome: str | None = None,
        tipo: str = "realm",
        client_uuid: str | None = None,
        limite: int = 100,
    ) -> list[dict[str, Any]]:
        """Consulta permissões do Realm ou de um client.

        Quando ``nome`` é informado, consulta somente a permissão
        correspondente. Caso contrário, lista as permissões disponíveis,
        respeitando o limite informado.

        Args:
            nome: Nome da permissão a ser consultada.
            tipo: Tipo da permissão. Aceita ``realm`` ou ``client``.
            client_uuid: ID interno do client quando ``tipo`` for
                ``client``.
            limite: Quantidade máxima de permissões retornadas.

        Returns:
            Lista de permissões normalizadas.

        Raises:
            ValueError: Se o tipo, os parâmetros ou o limite forem
                inválidos.
        """
        self._validar_tipo(
            tipo=tipo,
            client_uuid=client_uuid,
        )

        self._validar_limite(limite)

        logger.debug(
            "Consultando permissões no Keycloak.",
            extra={
                "tipo": tipo,
                "nome": nome,
                "client_uuid": client_uuid,
                "limite": limite,
            },
        )

        if tipo == "realm":
            permissoes = self._consultar_realm(
                nome=nome,
                limite=limite,
            )
        else:
            permissoes = self._consultar_client(
                nome=nome,
                client_uuid=client_uuid,
                limite=limite,
            )

        return [
            self._normalizar_permissao(permissao) for permissao in permissoes
        ]

    def atualizar(
        self,
        nome: str,
        tipo: str = "realm",
        client_uuid: str | None = None,
        novo_nome: str | None = None,
        descricao: str | None = None,
        atributos: dict[str, Any] | None = None,
    ) -> None:
        """Atualiza uma permissão do Realm ou de um client.

        Apenas os campos informados são alterados.

        Args:
            nome: Nome atual da permissão.
            tipo: Tipo da permissão. Aceita ``realm`` ou ``client``.
            client_uuid: ID interno do client quando ``tipo`` for
                ``client``.
            novo_nome: Novo nome da permissão.
            descricao: Nova descrição da permissão.
            atributos: Novos atributos da permissão.

        Raises:
            ValueError: Se o tipo ou os parâmetros forem inválidos ou
                se nenhum campo for informado para atualização.
        """
        self._validar_tipo(
            tipo=tipo,
            client_uuid=client_uuid,
        )

        payload: dict[str, Any] = {}

        if novo_nome is not None:
            payload["name"] = novo_nome

        if descricao is not None:
            payload["description"] = descricao

        if atributos is not None:
            payload["attributes"] = atributos

        if not payload:
            raise ValueError("Informe ao menos um campo para atualização.")

        logger.info(
            "Atualizando permissão no Keycloak.",
            extra={
                "tipo": tipo,
                "nome": nome,
                "client_uuid": client_uuid,
            },
        )

        if tipo == "realm":
            self.admin.executar(
                self.admin.cliente.update_realm_role,
                role_name=nome,
                payload=payload,
            )
            return

        assert client_uuid is not None

        self.admin.executar(
            self.admin.cliente.update_client_role,
            client_id=client_uuid,
            role_name=nome,
            payload=payload,
        )

    def _consultar_realm(
        self,
        nome: str | None,
        limite: int,
    ) -> list[dict[str, Any]]:
        """Consulta permissões diretamente no Realm.

        Args:
            nome: Nome da permissão. Quando informado, consulta
                somente essa permissão.
            limite: Quantidade máxima de permissões retornadas.

        Returns:
            Permissões retornadas pelo Keycloak.
        """
        if nome is not None:
            permissao = self.admin.executar(
                self.admin.cliente.get_realm_role,
                role_name=nome,
            )

            return [permissao]

        return self.admin.executar(
            self.admin.cliente.get_realm_roles,
            query={
                "max": limite,
            },
        )

    def _consultar_client(
        self,
        nome: str | None,
        client_uuid: str | None,
        limite: int,
    ) -> list[dict[str, Any]]:
        """Consulta permissões de um client.

        Args:
            nome: Nome da permissão. Quando informado, consulta
                somente essa permissão.
            client_uuid: ID interno do client.
            limite: Quantidade máxima de permissões retornadas.

        Returns:
            Permissões retornadas pelo Keycloak.
        """
        assert client_uuid is not None

        if nome is not None:
            permissao = self.admin.executar(
                self.admin.cliente.get_client_role,
                client_id=client_uuid,
                role_name=nome,
            )

            return [permissao]

        permissoes = self.admin.executar(
            self.admin.cliente.get_client_roles,
            client_id=client_uuid,
        )

        return permissoes[:limite]

    @classmethod
    def _validar_tipo(
        cls,
        tipo: str,
        client_uuid: str | None,
    ) -> None:
        """Valida o tipo da permissão e o client associado.

        Args:
            tipo: Tipo da permissão. Aceita ``realm`` ou ``client``.
            client_uuid: ID interno do client.

        Raises:
            ValueError: Se o tipo for inválido, se ``client_uuid`` for
                obrigatório e não for informado, ou se for informado
                indevidamente para uma permissão do Realm.
        """
        if tipo not in cls.TIPOS_VALIDOS:
            raise ValueError(
                "Tipo de permissão inválido. " "Utilize 'realm' ou 'client'."
            )

        if tipo == "client" and not client_uuid:
            raise ValueError(
                "client_uuid é obrigatório para permissões de cliente."
            )

        if tipo == "realm" and client_uuid:
            raise ValueError(
                "client_uuid não deve ser informado para "
                "permissões do Realm."
            )

    @staticmethod
    def _validar_limite(
        limite: int,
    ) -> None:
        """Valida o limite utilizado nas consultas.

        Args:
            limite: Quantidade máxima de permissões retornadas.

        Raises:
            ValueError: Se o limite for menor que 1.
        """
        if limite < 1:
            raise ValueError("limite deve ser maior ou igual a 1.")

    @staticmethod
    def _normalizar_permissao(
        permissao: dict[str, Any],
    ) -> dict[str, Any]:
        """Normaliza uma permissão para o contrato interno.

        Args:
            permissao: Dados da permissão retornados pelo Keycloak.

        Returns:
            Dados da permissão normalizados.
        """
        return {
            "id": permissao.get("id"),
            "nome": permissao.get("name"),
            "descricao": permissao.get("description"),
            "composite": permissao.get("composite", False),
            "container_id": permissao.get("containerId"),
            "atributos": permissao.get("attributes", {}),
        }
