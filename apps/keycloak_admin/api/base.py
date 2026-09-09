"""Classes base para a API administrativa do Keycloak."""

from drf_spectacular.utils import OpenApiResponse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.keycloak_admin.api.exception_handler import (
    tratar_excecao_keycloak,
)
from apps.keycloak_admin.api.serializers import ErroResponseSerializer
from apps.keycloak_admin.exceptions import KeycloakAdminError


class KeycloakAdminAPIView(APIView):
    """Classe base para endpoints administrativos do Keycloak.

    Centraliza comportamentos comuns às views administrativas do
    Keycloak, incluindo o tratamento das exceções de domínio e a
    definição das respostas padrão utilizadas na documentação OpenAPI.

    As subclasses podem reutilizar essa implementação para garantir
    que erros gerados pelos serviços de administração do Keycloak sejam
    convertidos de forma consistente em respostas HTTP.
    """

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
