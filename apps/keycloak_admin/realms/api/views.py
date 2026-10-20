"""Views da API administrativa de realms."""

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from apps.keycloak_admin.api.base import KeycloakAdminAPIView
from apps.keycloak_admin.api.serializers import MensagemResponseSerializer
from apps.keycloak_admin.realms.api.serializers import (
    FinalidadesSerializer,
    RealmAtualizarSerializer,
    RealmCriarSerializer,
    RealmSerializer,
)
from apps.keycloak_admin.realms.services import RealmService

_TAG = ["Realms"]


@extend_schema(
    tags=_TAG,
    summary="Realms",
    description="Consulta e cria realms no Keycloak.",
)
class RealmListCreateView(KeycloakAdminAPIView):
    """Endpoint de consulta e criação de realms."""

    @extend_schema(
        summary="Consultar realms",
        description="Consulta os realms do servidor Keycloak.",
        responses={
            200: RealmSerializer(many=True),
            **KeycloakAdminAPIView.ERROS_PADRAO,
        },
    )
    def get(
        self,
        request: Request,
    ) -> Response:
        """Consulta realms.

        Args:
            request: Requisição HTTP.

        Returns:
            Lista de realms encontrados.
        """
        realms = RealmService().consultar()

        response = RealmSerializer(
            realms,
            many=True,
        )

        return Response(
            response.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Criar realm",
        description="Cria um novo realm no Keycloak.",
        request=RealmCriarSerializer,
        responses={
            201: MensagemResponseSerializer,
            **KeycloakAdminAPIView.ERROS_PADRAO,
        },
    )
    def post(
        self,
        request: Request,
    ) -> Response:
        """Cria um realm.

        Args:
            request: Requisição HTTP.

        Returns:
            Mensagem de confirmação da criação.
        """
        serializer = RealmCriarSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        RealmService().criar(
            **serializer.validated_data,
        )

        return Response(
            {"mensagem": "Realm criado com sucesso."},
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    tags=_TAG,
    summary="Realm",
    description="Consulta e atualiza um realm específico.",
)
class RealmDetailView(KeycloakAdminAPIView):
    """Endpoint de gerenciamento de um realm específico."""

    @extend_schema(
        summary="Consultar realm",
        description="Consulta um realm pelo seu identificador.",
        responses={
            200: RealmSerializer,
            **KeycloakAdminAPIView.ERROS_PADRAO,
        },
    )
    def get(
        self,
        request: Request,
        nome: str,
    ) -> Response:
        """Consulta um realm.

        Args:
            request: Requisição HTTP.
            nome: Identificador do realm.

        Returns:
            Dados do realm.
        """
        realm = RealmService().consultar(nome=nome)[0]

        return Response(
            RealmSerializer(realm).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Atualizar realm",
        description=(
            "Atualiza o nome de exibição, a situação ou a marcação de "
            "topologia oficial de um realm. Realms oficiais, o master e "
            "o configurado na aplicação não podem ser desabilitados."
        ),
        request=RealmAtualizarSerializer,
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
        """Atualiza um realm.

        Args:
            request: Requisição HTTP.
            nome: Identificador do realm.

        Returns:
            Mensagem de confirmação da atualização.
        """
        serializer = RealmAtualizarSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        RealmService().atualizar(
            nome=nome,
            **serializer.validated_data,
        )

        return Response(
            {"mensagem": "Realm atualizado com sucesso."},
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=_TAG,
    summary="Finalidades de teste",
    description="Lista as finalidades de teste aceitas para os realms.",
)
class RealmFinalidadesView(KeycloakAdminAPIView):
    """Endpoint de consulta das finalidades de teste."""

    @extend_schema(
        summary="Consultar finalidades de teste",
        description=(
            "Retorna as finalidades de teste configuradas no ambiente e o "
            "rótulo usado para realms sem finalidade (uso normal)."
        ),
        responses={
            200: FinalidadesSerializer,
            **KeycloakAdminAPIView.ERROS_PADRAO,
        },
    )
    def get(
        self,
        request: Request,
    ) -> Response:
        """Consulta as finalidades de teste.

        Args:
            request: Requisição HTTP.

        Returns:
            Lista de finalidades aceitas.
        """
        response = FinalidadesSerializer(
            {
                "finalidades": RealmService.listar_finalidades(),
                "padrao": RealmService.finalidade_padrao(),
            },
        )

        return Response(
            response.data,
            status=status.HTTP_200_OK,
        )
