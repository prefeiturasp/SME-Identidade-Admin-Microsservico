"""Views da API administrativa de clientes."""

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from apps.keycloak_admin.api.base import KeycloakAdminAPIView
from apps.keycloak_admin.clientes.api.serializers import (
    ClientAtualizarSerializer,
    ClientConsultaSerializer,
    ClientCriadoSerializer,
    ClientCriarSerializer,
    ClientSerializer,
)
from apps.keycloak_admin.clientes.services import ClientService

_TAG = ["Clientes"]


@extend_schema(
    tags=_TAG,
    summary="Clientes",
    description="Consulta e cria clientes no Keycloak.",
)
class ClientListCreateView(KeycloakAdminAPIView):
    """Endpoint de consulta e criação de clientes."""

    @extend_schema(
        summary="Consultar clientes",
        description=("Consulta os clientes administrativos do Keycloak."),
        parameters=[ClientConsultaSerializer],
        responses={
            200: ClientSerializer(many=True),
            **KeycloakAdminAPIView.ERROS_PADRAO,
        },
    )
    def get(
        self,
        request: Request,
    ) -> Response:
        """Consulta clientes.

        Args:
            request: Requisição HTTP.

        Returns:
            Lista de clientes encontrados.
        """
        serializer = ClientConsultaSerializer(
            data=request.query_params,
        )
        serializer.is_valid(raise_exception=True)

        clientes = ClientService().consultar(
            **serializer.validated_data,
        )

        response = ClientSerializer(
            clientes,
            many=True,
        )

        return Response(
            response.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Criar cliente",
        description="Cria um novo cliente no Keycloak.",
        request=ClientCriarSerializer,
        responses={
            201: ClientCriadoSerializer,
            **KeycloakAdminAPIView.ERROS_PADRAO,
        },
    )
    def post(
        self,
        request: Request,
    ) -> Response:
        """Cria um cliente.

        Args:
            request: Requisição HTTP.

        Returns:
            ID do cliente criado.
        """
        serializer = ClientCriarSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        client_uuid = ClientService().criar(
            **serializer.validated_data,
        )

        response = ClientCriadoSerializer(
            {"id": client_uuid},
        )

        return Response(
            response.data,
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    tags=_TAG,
    summary="Cliente",
    description="Atualiza um cliente específico.",
)
class ClientDetailView(KeycloakAdminAPIView):
    """Endpoint de gerenciamento de um cliente específico."""

    @extend_schema(
        summary="Atualizar cliente",
        description=("Atualiza a configuração de um cliente existente."),
        request=ClientAtualizarSerializer,
        responses={
            200: None,
            **KeycloakAdminAPIView.ERROS_PADRAO,
        },
    )
    def patch(
        self,
        request: Request,
        client_uuid: str,
    ) -> Response:
        """Atualiza um cliente.

        Args:
            request: Requisição HTTP.
            client_uuid: ID interno do cliente no Keycloak.

        Returns:
            Resposta indicando que o cliente foi atualizado.
        """
        serializer = ClientAtualizarSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        ClientService().atualizar(
            client_uuid=client_uuid,
            **serializer.validated_data,
        )

        return Response(
            status=status.HTTP_200_OK,
        )
