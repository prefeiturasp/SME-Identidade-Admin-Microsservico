"""Views da API administrativa de permissões."""

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from apps.keycloak_admin.api.base import KeycloakAdminAPIView
from apps.keycloak_admin.api.serializers import MensagemResponseSerializer
from apps.keycloak_admin.permissoes.api.serializers import (
    RoleAtualizarSerializer,
    RoleConsultaSerializer,
    RoleCriarSerializer,
    RoleSerializer,
)
from apps.keycloak_admin.permissoes.services import RoleService

_TAG = ["Permissões"]


@extend_schema(
    tags=_TAG,
    summary="Permissões de Realm",
    description="Gerencia permissões diretamente no Realm.",
)
class RealmRoleListCreateView(KeycloakAdminAPIView):
    """Consulta e cria permissões de Realm."""

    @extend_schema(
        summary="Consultar permissões de Realm",
        description=(
            "Lista as permissões disponíveis no Realm.\n\n"
            "Quando `nome` é informado, retorna somente "
            "a permissão correspondente."
        ),
        parameters=[RoleConsultaSerializer],
        responses={
            200: RoleSerializer(many=True),
            **KeycloakAdminAPIView.ERROS_PADRAO,
        },
    )
    def get(
        self,
        request: Request,
    ) -> Response:
        """Consulta permissões de Realm.

        Args:
            request: Requisição HTTP.

        Returns:
            Lista de permissões encontradas.
        """
        serializer = RoleConsultaSerializer(
            data=request.query_params,
        )
        serializer.is_valid(raise_exception=True)

        permissoes = RoleService().consultar(
            tipo="realm",
            **serializer.validated_data,
        )

        response = RoleSerializer(
            permissoes,
            many=True,
        )

        return Response(
            response.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Criar permissão de Realm",
        description="Cria uma nova permissão de Realm.",
        request=RoleCriarSerializer,
        responses={
            201: MensagemResponseSerializer,
            **KeycloakAdminAPIView.ERROS_PADRAO,
        },
    )
    def post(
        self,
        request: Request,
    ) -> Response:
        """Cria uma permissão de Realm.

        Args:
            request: Requisição HTTP.

        Returns:
            Confirmação da criação da permissão.
        """
        serializer = RoleCriarSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        RoleService().criar(
            tipo="realm",
            **serializer.validated_data,
        )

        return Response(
            {"mensagem": "Permissão criada com sucesso."},
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    tags=_TAG,
    summary="Permissão de Realm",
    description="Atualiza uma permissão específica de Realm.",
)
class RealmRoleDetailView(KeycloakAdminAPIView):
    """Atualiza uma permissão específica de Realm."""

    @extend_schema(
        summary="Atualizar permissão de Realm",
        description=(
            "Atualiza uma permissão existente de Realm. "
            "Somente os campos informados serão alterados."
        ),
        request=RoleAtualizarSerializer,
        responses={
            200: MensagemResponseSerializer,
            **KeycloakAdminAPIView.ERROS_PADRAO,
        },
    )
    def patch(
        self,
        request: Request,
        nome: str,
    ) -> Response:
        """Atualiza uma permissão de Realm.

        Args:
            request: Requisição HTTP.
            nome: Nome atual da permissão.

        Returns:
            Confirmação da atualização da permissão.
        """
        serializer = RoleAtualizarSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        RoleService().atualizar(
            nome=nome,
            tipo="realm",
            **serializer.validated_data,
        )

        return Response(
            {"mensagem": "Permissão atualizada com sucesso."},
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=_TAG,
    summary="Permissões do cliente",
    description=("Gerencia permissões vinculadas a um cliente específico."),
)
class ClientRoleListCreateView(KeycloakAdminAPIView):
    """Consulta e cria permissões de um cliente."""

    @extend_schema(
        summary="Consultar permissões do cliente",
        description=(
            "Lista as permissões pertencentes ao cliente informado.\n\n"
            "Quando `nome` é informado, retorna somente "
            "a permissão correspondente."
        ),
        parameters=[RoleConsultaSerializer],
        responses={
            200: RoleSerializer(many=True),
            **KeycloakAdminAPIView.ERROS_PADRAO,
        },
    )
    def get(
        self,
        request: Request,
        client_uuid: str,
    ) -> Response:
        """Consulta permissões de um cliente.

        Args:
            request: Requisição HTTP.
            client_uuid: ID interno do cliente.

        Returns:
            Lista de permissões encontradas.
        """
        serializer = RoleConsultaSerializer(
            data=request.query_params,
        )
        serializer.is_valid(raise_exception=True)

        permissoes = RoleService().consultar(
            tipo="client",
            client_uuid=client_uuid,
            **serializer.validated_data,
        )

        response = RoleSerializer(
            permissoes,
            many=True,
        )

        return Response(
            response.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Criar permissão no cliente",
        description=(
            "Cria uma nova permissão vinculada ao cliente informado."
        ),
        request=RoleCriarSerializer,
        responses={
            201: MensagemResponseSerializer,
            **KeycloakAdminAPIView.ERROS_PADRAO,
        },
    )
    def post(
        self,
        request: Request,
        client_uuid: str,
    ) -> Response:
        """Cria uma permissão no cliente.

        Args:
            request: Requisição HTTP.
            client_uuid: ID interno do cliente.

        Returns:
            Confirmação da criação da permissão.
        """
        serializer = RoleCriarSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        RoleService().criar(
            tipo="client",
            client_uuid=client_uuid,
            **serializer.validated_data,
        )

        return Response(
            {"mensagem": "Permissão criada com sucesso."},
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    tags=_TAG,
    summary="Permissão do cliente",
    description="Atualiza uma permissão específica de um cliente.",
)
class ClientRoleDetailView(KeycloakAdminAPIView):
    """Atualiza uma permissão específica de um cliente."""

    @extend_schema(
        summary="Atualizar permissão do cliente",
        description=(
            "Atualiza uma permissão existente no cliente. "
            "Somente os campos informados serão alterados."
        ),
        request=RoleAtualizarSerializer,
        responses={
            200: MensagemResponseSerializer,
            **KeycloakAdminAPIView.ERROS_PADRAO,
        },
    )
    def patch(
        self,
        request: Request,
        client_uuid: str,
        nome: str,
    ) -> Response:
        """Atualiza uma permissão do cliente.

        Args:
            request: Requisição HTTP.
            client_uuid: ID interno do cliente.
            nome: Nome atual da permissão.

        Returns:
            Confirmação da atualização da permissão.
        """
        serializer = RoleAtualizarSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        RoleService().atualizar(
            nome=nome,
            tipo="client",
            client_uuid=client_uuid,
            **serializer.validated_data,
        )

        return Response(
            {"mensagem": "Permissão atualizada com sucesso."},
            status=status.HTTP_200_OK,
        )
