# Cria uma classe de autenticação personalizada para autenticar requisições usando credenciais de cliente (client credentials) do Keycloak.

"""Autenticação por API Key para os endpoints do SME-Identidade-Admin."""

from __future__ import annotations

from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request

from apps.keycloak_admin.admin_kc import KeycloakAdminService


class _UsuarioCredencialsClientKey:
    """Representação mínima de usuário autenticado por credenciais cliente."""

    is_authenticated = True


class AutenticacaoCredenciaisCliente(BaseAuthentication):
    """Autentica requisições via credenciais cliente no header configurado.

    A chave é comparada com cliente do Keycloak.
    O header utilizado é definido por ``settings.CLIENT_ID_HEADER``
    e ``settings.CLIENT_SECRET_HEADER``.
    """

    def authenticate(
        self, request: Request
    ) -> tuple[_UsuarioCredencialsClientKey, None] | None:
        """Valida as credenciais de cliente presente no header da requisição.

        Args:
            request: Requisição HTTP recebida.

        Returns:
            Tupla (usuário, None) se autenticado, None se header ausente.

        Raises:
            AuthenticationFailed: Se as credenciais de cliente forem inválidas.
        """
        header_client_id = settings.CLIENT_ID_HEADER.upper().replace("-", "_")
        header_client_secret = settings.CLIENT_SECRET_HEADER.upper().replace(
            "-", "_"
        )
        client_id = request.META.get(f"HTTP_{header_client_id}", "")
        client_secret = request.META.get(f"HTTP_{header_client_secret}", "")
        if not client_id or not client_secret:
            return None

        token = KeycloakAdminService().authenticate_client(
            client_id, client_secret
        )

        if not token:
            raise AuthenticationFailed("Credenciais de cliente inválidas.")

        return (_UsuarioCredencialsClientKey(), None)

    def authenticate_header(self, request: Request) -> list[str]:
        """Retorna o nome do header de autenticação esperado."""
        return [settings.CLIENT_ID_HEADER, settings.CLIENT_SECRET_HEADER]
