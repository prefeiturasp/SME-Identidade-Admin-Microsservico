"""Views da API administrativa de sessões."""

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from apps.keycloak_admin.api.base import KeycloakAdminAPIView
from apps.keycloak_admin.api.serializers import MensagemResponseSerializer
from apps.keycloak_admin.sessoes.api.serializers import (
    SessaoSerializer,
)
from apps.keycloak_admin.sessoes.services import SessaoService

_TAG = ["Sessões"]


@extend_schema(
    tags=_TAG,
    summary="Consultar sessões de usuário",
    description=(
        "Consulta as sessões ativas de um usuário específico no Keycloak."
    ),
)
class SessaoListView(KeycloakAdminAPIView):
    """Endpoint de consulta das sessões de um usuário."""

    @extend_schema(
        summary="Consultar sessões ativas",
        description=(
            "Retorna todas as sessões atualmente ativas para "
            "o usuário informado.\n\n"
            "O `usuario_id` corresponde ao ID interno do usuário "
            "no Keycloak."
        ),
        responses={
            200: SessaoSerializer(many=True),
            **KeycloakAdminAPIView.ERROS_PADRAO,
        },
    )
    def get(
        self,
        request: Request,
        usuario_id: str,
    ) -> Response:
        """Consulta as sessões ativas de um usuário.

        Args:
            request: Requisição HTTP.
            usuario_id: ID interno do usuário no Keycloak.

        Returns:
            Lista de sessões ativas.
        """
        sessoes = SessaoService().consultar(
            usuario_id=usuario_id,
        )

        serializer = SessaoSerializer(
            sessoes,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=_TAG,
    summary="Encerrar sessões de usuário",
    description=(
        "Encerra todas as sessões ativas de um usuário específico "
        "no Keycloak."
    ),
)
class SessaoLogoutView(KeycloakAdminAPIView):
    """Endpoint para encerramento das sessões de um usuário."""

    @extend_schema(
        summary="Encerrar sessões ativas",
        description=(
            "Encerra todas as sessões ativas do usuário informado.\n\n"
            "A operação afeta somente as sessões do usuário informado."
        ),
        request=None,
        responses={
            200: MensagemResponseSerializer,
            **KeycloakAdminAPIView.ERROS_PADRAO,
        },
    )
    def post(
        self,
        request: Request,
        usuario_id: str,
    ) -> Response:
        """Encerra as sessões ativas de um usuário.

        Args:
            request: Requisição HTTP.
            usuario_id: ID interno do usuário no Keycloak.

        Returns:
            Confirmação do encerramento das sessões.
        """
        SessaoService().encerrar(
            usuario_id=usuario_id,
        )

        return Response(
            {
                "mensagem": ("Sessões do usuário encerradas com sucesso."),
            },
            status=status.HTTP_200_OK,
        )
