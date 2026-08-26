"""Serviço de administração de sessões no Keycloak."""

import logging
from typing import Any

from apps.keycloak_admin.admin_kc import KeycloakAdminService

logger = logging.getLogger(__name__)


class SessaoService:
    """Centraliza a administração de sessões de usuários no Keycloak."""

    def __init__(
        self,
        admin: KeycloakAdminService | None = None,
    ) -> None:
        """Inicializa o serviço de administração de sessões.

        Args:
            admin: Serviço responsável pela comunicação com o Keycloak.
                Quando não informado, uma nova instância é criada.
        """
        self.admin = admin or KeycloakAdminService()

    def consultar(
        self,
        usuario_id: str,
    ) -> list[dict[str, Any]]:
        """Consulta as sessões ativas de um usuário.

        A consulta é realizada exclusivamente para o usuário informado.

        Args:
            usuario_id: ID interno do usuário no Keycloak.

        Returns:
            Lista de sessões ativas do usuário.
        """
        logger.debug(
            "Consultando sessões do usuário no Keycloak.",
            extra={
                "usuario_id": usuario_id,
            },
        )

        sessoes = self.admin.executar(
            self.admin.cliente.get_sessions,
            user_id=usuario_id,
        )

        return [self._normalizar_sessao(sessao) for sessao in sessoes]

    def encerrar(
        self,
        usuario_id: str,
    ) -> None:
        """Encerra todas as sessões ativas de um usuário.

        A operação é realizada exclusivamente para o usuário informado.

        Args:
            usuario_id: ID interno do usuário no Keycloak.
        """
        logger.info(
            "Encerrando sessões do usuário no Keycloak.",
            extra={
                "usuario_id": usuario_id,
            },
        )

        self.admin.executar(
            self.admin.cliente.user_logout,
            user_id=usuario_id,
        )

    @staticmethod
    def _normalizar_sessao(
        sessao: dict[str, Any],
    ) -> dict[str, Any]:
        """Normaliza uma sessão do Keycloak.

        Args:
            sessao: Dados da sessão retornados pelo Keycloak.

        Returns:
            Dados da sessão normalizados para o contrato do Admin-MS.
        """
        return {
            "id": sessao.get("id"),
            "usuario_id": sessao.get("userId"),
            "usuario": sessao.get("username"),
            "clientes": sessao.get("clients", []),
            "endereco_ip": sessao.get("ipAddress"),
            "inicio": sessao.get("start"),
            "ultimo_acesso": sessao.get("lastAccess"),
        }
