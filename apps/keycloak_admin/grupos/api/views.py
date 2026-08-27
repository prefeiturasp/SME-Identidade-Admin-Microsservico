"""Views da API administrativa de grupos."""

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from apps.keycloak_admin.api.base import KeycloakAdminAPIView
from apps.keycloak_admin.api.serializers import (
    MensagemResponseSerializer,
)
from apps.keycloak_admin.grupos.api.serializers import (
    GrupoAtualizarSerializer,
    GrupoClientRoleSerializer,
    GrupoConsultaSerializer,
    GrupoCriarSerializer,
    GrupoRoleSerializer,
    GrupoSerializer,
)
from apps.keycloak_admin.grupos.services import GrupoService

_TAG = ["Grupos"]


@extend_schema(
    tags=_TAG,
    summary="Grupos",
    description="Consulta e cria grupos no Realm do Keycloak.",
)
class GrupoListCreateView(KeycloakAdminAPIView):
    """Endpoint de consulta e criação de grupos."""

    @extend_schema(
        summary="Consultar grupos",
        description=(
            "Consulta grupos do Realm.\n\n"
            "Os parâmetros `grupo_id` e `nome` são mutuamente "
            "exclusivos.\n\n"
            "Se nenhum dos dois for informado, todos os grupos "
            "serão consultados respeitando o `limite`."
        ),
        parameters=[GrupoConsultaSerializer],
        responses={
            200: GrupoSerializer(many=True),
            **KeycloakAdminAPIView.ERROS_PADRAO,
        },
    )
    def get(
        self,
        request: Request,
    ) -> Response:
        """Consulta grupos.

        Args:
            request: Requisição HTTP.

        Returns:
            Lista de grupos encontrados.
        """
        serializer = GrupoConsultaSerializer(
            data=request.query_params,
        )
        serializer.is_valid(raise_exception=True)

        grupos = GrupoService().consultar(
            **serializer.validated_data,
        )

        response = GrupoSerializer(
            grupos,
            many=True,
        )

        return Response(
            response.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Criar grupo",
        description="Cria um novo grupo no Realm do Keycloak.",
        request=GrupoCriarSerializer,
        responses={
            201: MensagemResponseSerializer,
            **KeycloakAdminAPIView.ERROS_PADRAO,
        },
    )
    def post(
        self,
        request: Request,
    ) -> Response:
        """Cria um grupo.

        Args:
            request: Requisição HTTP.

        Returns:
            Confirmação da criação do grupo.
        """
        serializer = GrupoCriarSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        GrupoService().criar(
            **serializer.validated_data,
        )

        return Response(
            {"mensagem": "Grupo criado com sucesso."},
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    tags=_TAG,
    summary="Grupo",
    description="Atualiza um grupo específico.",
)
class GrupoDetailView(KeycloakAdminAPIView):
    """Endpoint de atualização de um grupo."""

    @extend_schema(
        summary="Atualizar grupo",
        description=(
            "Atualiza somente os campos informados do grupo existente."
        ),
        request=GrupoAtualizarSerializer,
        responses={
            200: MensagemResponseSerializer,
            **KeycloakAdminAPIView.ERROS_PADRAO,
        },
    )
    def patch(
        self,
        request: Request,
        grupo_id: str,
    ) -> Response:
        """Atualiza um grupo.

        Args:
            request: Requisição HTTP.
            grupo_id: ID interno do grupo no Keycloak.

        Returns:
            Confirmação da atualização do grupo.
        """
        serializer = GrupoAtualizarSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        GrupoService().atualizar(
            grupo_id=grupo_id,
            **serializer.validated_data,
        )

        return Response(
            {"mensagem": "Grupo atualizado com sucesso."},
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=_TAG,
    summary="Realm Roles do grupo",
    description=("Associa ou desassocia Realm Roles de um grupo."),
)
class GrupoRealmRoleView(KeycloakAdminAPIView):
    """Endpoint de gerenciamento de Realm Roles do grupo."""

    @extend_schema(
        summary="Associar Realm Role",
        description=("Associa uma Realm Role existente ao grupo."),
        request=GrupoRoleSerializer,
        responses={
            200: MensagemResponseSerializer,
            **KeycloakAdminAPIView.ERROS_PADRAO,
        },
    )
    def post(
        self,
        request: Request,
        grupo_id: str,
    ) -> Response:
        """Associa uma Realm Role ao grupo.

        Args:
            request: Requisição HTTP.
            grupo_id: ID interno do grupo.

        Returns:
            Confirmação da associação.
        """
        serializer = GrupoRoleSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        GrupoService().associar_role_realm(
            grupo_id=grupo_id,
            nome_role=serializer.validated_data["nome_permissao"],
        )

        return Response(
            {"mensagem": "Realm Role associada com sucesso."},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Desassociar Realm Role",
        description=(
            "Desassocia uma Realm Role do grupo.\n\n"
            "O `nome_permissao` identifica a Realm Role "
            "que será removida do grupo."
        ),
        request=GrupoRoleSerializer,
        responses={
            200: MensagemResponseSerializer,
            **KeycloakAdminAPIView.ERROS_PADRAO,
        },
    )
    def patch(
        self,
        request: Request,
        grupo_id: str,
    ) -> Response:
        """Desassocia uma Realm Role do grupo.

        Args:
            request: Requisição HTTP.
            grupo_id: ID interno do grupo.

        Returns:
            Confirmação da desassociação.
        """
        serializer = GrupoRoleSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        GrupoService().desassociar_role_realm(
            grupo_id=grupo_id,
            nome_role=serializer.validated_data["nome_permissao"],
        )

        return Response(
            {"mensagem": "Realm Role desassociada com sucesso."},
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=_TAG,
    summary="Client Roles do grupo",
    description=("Associa ou desassocia Client Roles de um grupo."),
)
class GrupoClientRoleView(KeycloakAdminAPIView):
    """Endpoint de gerenciamento de Client Roles do grupo."""

    @extend_schema(
        summary="Associar Client Role",
        description=("Associa uma Client Role existente ao grupo."),
        request=GrupoClientRoleSerializer,
        responses={
            200: MensagemResponseSerializer,
            **KeycloakAdminAPIView.ERROS_PADRAO,
        },
    )
    def post(
        self,
        request: Request,
        grupo_id: str,
        client_uuid: str,
    ) -> Response:
        """Associa uma Client Role ao grupo.

        Args:
            request: Requisição HTTP.
            grupo_id: ID interno do grupo.
            client_uuid: ID interno do client.

        Returns:
            Confirmação da associação.
        """
        serializer = GrupoClientRoleSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        GrupoService().associar_role_client(
            grupo_id=grupo_id,
            client_uuid=client_uuid,
            nome_role=serializer.validated_data["nome_permissao"],
        )

        return Response(
            {"mensagem": "Client Role associada com sucesso."},
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Desassociar Client Role",
        description=(
            "Desassocia uma Client Role do grupo.\n\n"
            "O `client_uuid` identifica o cliente e "
            "`nome_permissao` identifica a Client Role "
            "que será removida do grupo."
        ),
        request=GrupoClientRoleSerializer,
        responses={
            200: MensagemResponseSerializer,
            **KeycloakAdminAPIView.ERROS_PADRAO,
        },
    )
    def patch(
        self,
        request: Request,
        grupo_id: str,
        client_uuid: str,
    ) -> Response:
        """Desassocia uma Client Role do grupo.

        Args:
            request: Requisição HTTP.
            grupo_id: ID interno do grupo.
            client_uuid: ID interno do client.

        Returns:
            Confirmação da desassociação.
        """
        serializer = GrupoClientRoleSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        GrupoService().desassociar_role_client(
            grupo_id=grupo_id,
            client_uuid=client_uuid,
            nome_role=serializer.validated_data["nome_permissao"],
        )

        return Response(
            {"mensagem": "Client Role desassociada com sucesso."},
            status=status.HTTP_200_OK,
        )
