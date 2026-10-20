"""Classes base para a API administrativa do Keycloak."""

import re
from contextvars import Token
from typing import Any

from django.conf import settings
from drf_spectacular.utils import OpenApiResponse
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.keycloak_admin.admin_kc import realm_requisicao
from apps.keycloak_admin.api.exception_handler import (
    tratar_excecao_keycloak,
)
from apps.keycloak_admin.api.serializers import ErroResponseSerializer
from apps.keycloak_admin.exceptions import KeycloakAdminError

_PADRAO_NOME_REALM = re.compile(r"^[A-Za-z0-9_-]+$")


class KeycloakAdminAPIView(APIView):
    """Classe base para endpoints administrativos do Keycloak.

    Centraliza comportamentos comuns às views administrativas do
    Keycloak, incluindo o tratamento das exceções de domínio e a
    definição das respostas padrão utilizadas na documentação OpenAPI.

    As subclasses podem reutilizar essa implementação para garantir
    que erros gerados pelos serviços de administração do Keycloak sejam
    convertidos de forma consistente em respostas HTTP.

    O header ``REALM_HEADER`` permite escolher o realm de trabalho por
    requisição, sem que cada view precise repassá-lo aos serviços.
    """

    _token_realm: Token[str | None] | None = None

    ERROS_PADRAO = {
        status.HTTP_400_BAD_REQUEST: OpenApiResponse(
            response=ErroResponseSerializer,
            description=(
                "Requisição inválida. Pode ocorrer quando o recurso "
                "já existe, não é encontrado ou a operação não é permitida."
            ),
        ),
        status.HTTP_401_UNAUTHORIZED: OpenApiResponse(
            response=ErroResponseSerializer,
            description="Falha de autenticação com o Keycloak.",
        ),
        status.HTTP_500_INTERNAL_SERVER_ERROR: OpenApiResponse(
            response=ErroResponseSerializer,
            description="Erro interno ao processar a operação.",
        ),
    }

    def handle_exception(
        self,
        exc: Exception,
    ) -> Response:
        """Trata exceções de domínio em respostas HTTP padronizadas.

        Exceções derivadas de ``KeycloakAdminError`` são encaminhadas
        para o tratamento específico da aplicação. Outras exceções
        permanecem sob responsabilidade do mecanismo padrão de tratamento
        de exceções do Django REST Framework.

        Args:
            exc: Exceção gerada durante o processamento da requisição.

        Returns:
            Resposta HTTP correspondente ao erro identificado. Para
            exceções que não pertencem ao domínio do Keycloak, retorna
            a resposta produzida pelo tratamento padrão do DRF.
        """
        if isinstance(exc, KeycloakAdminError):
            return tratar_excecao_keycloak(exc)

        return super().handle_exception(exc)

    def initial(
        self,
        request: Request,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """Define o realm de trabalho após autenticar a requisição.

        A autenticação ocorre antes para que credenciais de client sejam
        sempre validadas no realm configurado. O nome é validado porque
        compõe as URLs da Admin API do Keycloak.

        Args:
            request: Requisição HTTP recebida.
            *args: Argumentos posicionais da rota.
            **kwargs: Argumentos nomeados da rota.

        Raises:
            ValidationError: Se o realm informado tiver formato inválido.
        """
        super().initial(request, *args, **kwargs)

        realm = (request.headers.get(settings.REALM_HEADER) or "").strip()

        if realm and not _PADRAO_NOME_REALM.match(realm):
            raise ValidationError(
                {settings.REALM_HEADER: ["Realm informado é inválido."]}
            )

        self._token_realm = realm_requisicao.set(realm or None)

    def finalize_response(
        self,
        request: Request,
        response: Response,
        *args: Any,
        **kwargs: Any,
    ) -> Response:
        """Restaura o realm de trabalho ao concluir a requisição.

        Evita que a escolha de uma requisição permaneça no contexto
        reaproveitado pela próxima.

        Args:
            request: Requisição HTTP recebida.
            response: Resposta produzida pela view.
            *args: Argumentos posicionais da rota.
            **kwargs: Argumentos nomeados da rota.

        Returns:
            Resposta finalizada pelo DRF.
        """
        if self._token_realm is not None:
            realm_requisicao.reset(self._token_realm)
            self._token_realm = None

        return super().finalize_response(request, response, *args, **kwargs)
