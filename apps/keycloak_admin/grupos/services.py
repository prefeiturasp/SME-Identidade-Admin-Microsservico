"""Serviço de administração de grupos no Keycloak."""

import logging
from typing import Any

from apps.keycloak_admin.admin_kc import KeycloakAdminService

logger = logging.getLogger(__name__)


class GrupoService:
    """Centraliza as operações administrativas de grupos no Keycloak."""

    def __init__(
        self,
        admin: KeycloakAdminService | None = None,
    ) -> None:
        """Inicializa o serviço de administração de grupos.

        Args:
            admin: Serviço responsável pela comunicação com o Keycloak.
                Quando não informado, uma nova instância é criada.
        """
        self.admin = admin or KeycloakAdminService()

    def criar(
        self,
        nome: str,
        caminho: str | None = None,
        atributos: dict[str, Any] | None = None,
    ) -> str:
        """Cria um grupo no Keycloak.

        Args:
            nome: Nome do grupo.
            caminho: Caminho hierárquico do grupo.
            atributos: Atributos personalizados do grupo.

        Returns:
            ID interno do grupo criado no Keycloak.

        Raises:
            ValueError: Se o Keycloak não retornar o ID do grupo criado.
        """
        payload: dict[str, Any] = {
            "name": nome,
        }

        if caminho is not None:
            payload["path"] = caminho

        if atributos is not None:
            payload["attributes"] = atributos

        logger.info(
            "Criando grupo no Keycloak.",
            extra={"nome": nome},
        )

        resultado = self.admin.executar(
            self.admin.cliente.create_group,
            payload=payload,
        )

        if resultado is None:
            raise ValueError("O Keycloak não retornou o ID do grupo criado.")

        return resultado

    def consultar(
        self,
        grupo_id: str | None = None,
        nome: str | None = None,
        limite: int = 100,
    ) -> list[dict[str, Any]]:
        """Consulta grupos do Realm.

        Quando ``grupo_id`` é informado, consulta um grupo específico.
        Quando ``nome`` é informado, pesquisa grupos pelo nome.
        Quando nenhum critério é informado, lista os grupos do Realm.

        Args:
            grupo_id: ID interno do grupo no Keycloak.
            nome: Nome utilizado na pesquisa.
            limite: Quantidade máxima de grupos retornados.

        Returns:
            Lista de grupos normalizados.

        Raises:
            ValueError: Se mais de um critério de identificação for
                informado ou se o limite for inválido.
        """
        self._validar_criterios_consulta(
            grupo_id=grupo_id,
            nome=nome,
        )
        self._validar_limite(limite)

        logger.debug(
            "Consultando grupos no Keycloak.",
            extra={
                "grupo_id": grupo_id,
                "nome": nome,
                "limite": limite,
            },
        )

        if grupo_id is not None:
            grupo = self.admin.executar(
                self.admin.cliente.get_group,
                group_id=grupo_id,
            )

            return [
                self._normalizar_grupo(grupo),
            ]

        parametros: dict[str, Any] = {
            "max": limite,
        }

        if nome is not None:
            parametros["search"] = nome

        grupos = self.admin.executar(
            self.admin.cliente.get_groups,
            query=parametros,
        )

        return [self._normalizar_grupo(grupo) for grupo in grupos]

    def atualizar(
        self,
        grupo_id: str,
        nome: str | None = None,
        caminho: str | None = None,
        atributos: dict[str, Any] | None = None,
    ) -> None:
        """Atualiza um grupo no Keycloak.

        Apenas os campos informados são alterados.

        Args:
            grupo_id: ID interno do grupo no Keycloak.
            nome: Novo nome do grupo.
            caminho: Novo caminho hierárquico.
            atributos: Novos atributos do grupo.

        Raises:
            ValueError: Se nenhum campo for informado para atualização.
        """
        payload: dict[str, Any] = {}

        if nome is not None:
            payload["name"] = nome

        if caminho is not None:
            payload["path"] = caminho

        if atributos is not None:
            payload["attributes"] = atributos

        if not payload:
            raise ValueError("Informe ao menos um campo para atualização.")

        logger.info(
            "Atualizando grupo no Keycloak.",
            extra={"grupo_id": grupo_id},
        )

        self.admin.executar(
            self.admin.cliente.update_group,
            group_id=grupo_id,
            payload=payload,
        )

    def associar_role_realm(
        self,
        grupo_id: str,
        nome_role: str,
    ) -> None:
        """Associa uma Realm Role a um grupo.

        Args:
            grupo_id: ID interno do grupo no Keycloak.
            nome_role: Nome da Realm Role.

        Raises:
            RecursoNaoEncontradoError: Se a role não existir.
        """
        logger.info(
            "Associando Realm Role ao grupo.",
            extra={
                "grupo_id": grupo_id,
                "nome_role": nome_role,
            },
        )

        role = self.admin.executar(
            self.admin.cliente.get_realm_role,
            role_name=nome_role,
        )

        self.admin.executar(
            self.admin.cliente.assign_group_realm_roles,
            group_id=grupo_id,
            roles=[role],
        )

    def desassociar_role_realm(
        self,
        grupo_id: str,
        nome_role: str,
    ) -> None:
        """Remove uma Realm Role de um grupo.

        Args:
            grupo_id: ID interno do grupo no Keycloak.
            nome_role: Nome da Realm Role.

        Raises:
            RecursoNaoEncontradoError: Se a role não existir.
        """
        logger.info(
            "Removendo Realm Role do grupo.",
            extra={
                "grupo_id": grupo_id,
                "nome_role": nome_role,
            },
        )

        role = self.admin.executar(
            self.admin.cliente.get_realm_role,
            role_name=nome_role,
        )

        self.admin.executar(
            self.admin.cliente.delete_group_realm_roles,
            group_id=grupo_id,
            roles=[role],
        )

    def associar_role_client(
        self,
        grupo_id: str,
        client_uuid: str,
        nome_role: str,
    ) -> None:
        """Associa uma Client Role a um grupo.

        Args:
            grupo_id: ID interno do grupo no Keycloak.
            client_uuid: ID interno do client no Keycloak.
            nome_role: Nome da Client Role.

        Raises:
            RecursoNaoEncontradoError: Se o client ou a role não existir.
        """
        logger.info(
            "Associando Client Role ao grupo.",
            extra={
                "grupo_id": grupo_id,
                "client_uuid": client_uuid,
                "nome_role": nome_role,
            },
        )

        role = self.admin.executar(
            self.admin.cliente.get_client_role,
            client_id=client_uuid,
            role_name=nome_role,
        )

        self.admin.executar(
            self.admin.cliente.assign_group_client_roles,
            group_id=grupo_id,
            client_id=client_uuid,
            roles=[role],
        )

    def desassociar_role_client(
        self,
        grupo_id: str,
        client_uuid: str,
        nome_role: str,
    ) -> None:
        """Remove uma Client Role de um grupo.

        Args:
            grupo_id: ID interno do grupo no Keycloak.
            client_uuid: ID interno do client no Keycloak.
            nome_role: Nome da Client Role.

        Raises:
            RecursoNaoEncontradoError: Se o client ou a role não existir.
        """
        logger.info(
            "Removendo Client Role do grupo.",
            extra={
                "grupo_id": grupo_id,
                "client_uuid": client_uuid,
                "nome_role": nome_role,
            },
        )

        role = self.admin.executar(
            self.admin.cliente.get_client_role,
            client_id=client_uuid,
            role_name=nome_role,
        )

        self.admin.executar(
            self.admin.cliente.delete_group_client_roles,
            group_id=grupo_id,
            client_id=client_uuid,
            roles=[role],
        )

    @staticmethod
    def _validar_criterios_consulta(
        grupo_id: str | None,
        nome: str | None,
    ) -> None:
        """Valida os critérios utilizados na consulta.

        Args:
            grupo_id: ID interno do grupo.
            nome: Nome utilizado na pesquisa.

        Raises:
            ValueError: Se mais de um critério for informado.
        """
        criterios = [valor for valor in (grupo_id, nome) if valor is not None]

        if len(criterios) > 1:
            raise ValueError(
                "Informe apenas um critério de consulta: grupo_id ou nome."
            )

    @staticmethod
    def _validar_limite(
        limite: int,
    ) -> None:
        """Valida o limite utilizado na consulta.

        Args:
            limite: Quantidade máxima de grupos retornados.

        Raises:
            ValueError: Se o limite for menor que um.
        """
        if limite < 1:
            raise ValueError("limite deve ser maior ou igual a 1.")

    @staticmethod
    def _normalizar_grupo(
        grupo: dict[str, Any],
    ) -> dict[str, Any]:
        """Normaliza um grupo do Keycloak para o contrato interno.

        Args:
            grupo: Dados do grupo retornados pelo Keycloak.

        Returns:
            Dados do grupo normalizados.
        """
        return {
            "id": grupo.get("id"),
            "nome": grupo.get("name"),
            "caminho": grupo.get("path"),
            "atributos": grupo.get(
                "attributes",
                {},
            ),
            "subgrupos": grupo.get(
                "subGroups",
                [],
            ),
        }
