"""Views da API administrativa de usuários."""

from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response

from apps.keycloak_admin.api.base import KeycloakAdminAPIView
from apps.keycloak_admin.usuarios.api.serializers import (
    UsuarioAlterarEmailSerializer,
    UsuarioAlterarSenhaSerializer,
    UsuarioAtualizarSerializer,
    UsuarioClientRoleSerializer,
    UsuarioConsultaSerializer,
    UsuarioCriadoSerializer,
    UsuarioCriarSerializer,
    UsuarioEmailSerializer,
    UsuarioGrupoSerializer,
    UsuarioRealmRoleSerializer,
    UsuarioSerializer,
)
from apps.keycloak_admin.usuarios.services import UsuarioService

_TAG = ["Usuários"]


@extend_schema(
    tags=_TAG,
    summary="Usuários",
    description="Consulta e cria usuários no Keycloak.",
)
class UsuarioListCreateView(KeycloakAdminAPIView):
    """Endpoint para consulta e criação de usuários."""

    @extend_schema(
        summary="Consultar usuários",
        description=(
            "Consulta usuários administrativos do Keycloak.\n\n"
            "**Formas de consulta:**\n\n"
            "- `usuario_id`: consulta por ID.\n"
            "- `cpf`: consulta por CPF.\n"
            "- `rf`: consulta por registro funcional.\n"
            "- `email`: consulta por e-mail exato.\n"
            "- `busca`: pesquisa textual geral.\n\n"
            "**Regras:**\n\n"
            "- Apenas um identificador pode ser informado por vez.\n"
            "- `busca` não pode ser combinada com um identificador.\n"
            "- Todos os parâmetros de identificação são opcionais.\n"
            "- Quando nenhum identificador ou `busca` for informado, "
            "a consulta retorna a lista de usuários.\n"
            "- `limite` é opcional e possui padrão de 100 registros."
        ),
        parameters=[UsuarioConsultaSerializer],
        responses={
            200: UsuarioSerializer(many=True),
            **KeycloakAdminAPIView.ERROS_PADRAO,
        },
    )
    def get(self, request: Request) -> Response:
        """Consulta usuários de acordo com os parâmetros informados.

        Args:
            request: Requisição HTTP contendo os filtros de consulta.

        Returns:
            Resposta HTTP contendo os usuários encontrados.
        """
        serializer = UsuarioConsultaSerializer(
            data=request.query_params,
        )
        serializer.is_valid(raise_exception=True)

        usuarios = UsuarioService().consultar(
            **serializer.validated_data,
        )

        response = UsuarioSerializer(
            usuarios,
            many=True,
        )

        return Response(
            response.data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Criar usuário",
        description="Cria um novo usuário no Keycloak.",
        request=UsuarioCriarSerializer,
        responses={
            201: UsuarioCriadoSerializer,
            **KeycloakAdminAPIView.ERROS_PADRAO,
        },
    )
    def post(self, request: Request) -> Response:
        """Cria um novo usuário no Keycloak.

        Args:
            request: Requisição HTTP contendo os dados do usuário.

        Returns:
            Resposta HTTP contendo o ID do usuário criado.
        """
        serializer = UsuarioCriarSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        usuario_id = UsuarioService().criar(
            **serializer.validated_data,
        )

        response = UsuarioCriadoSerializer(
            {"id": usuario_id},
        )

        return Response(
            response.data,
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    tags=_TAG,
    summary="Usuário",
    description="Atualiza os dados de um usuário no Keycloak.",
)
class UsuarioDetailView(KeycloakAdminAPIView):
    """Endpoint para gerenciamento de um usuário específico."""

    @extend_schema(
        summary="Atualizar usuário",
        description="Atualiza os dados cadastrais de um usuário.",
        request=UsuarioAtualizarSerializer,
        responses={
            204: None,
            **KeycloakAdminAPIView.ERROS_PADRAO,
        },
    )
    def patch(
        self,
        request: Request,
        usuario_id: str,
    ) -> Response:
        """Atualiza os dados cadastrais de um usuário.

        Args:
            request: Requisição HTTP contendo os campos a atualizar.
            usuario_id: ID interno do usuário no Keycloak.

        Returns:
            Resposta HTTP sem conteúdo.
        """
        serializer = UsuarioAtualizarSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        UsuarioService().atualizar(
            usuario_id=usuario_id,
            **serializer.validated_data,
        )

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )


@extend_schema(
    tags=_TAG,
    summary="Alterar e-mail do usuário",
    description="Altera o e-mail de um usuário.",
)
class UsuarioEmailView(KeycloakAdminAPIView):
    """Endpoint para alteração de e-mail de um usuário."""

    @extend_schema(
        request=UsuarioAlterarEmailSerializer,
        responses={
            200: UsuarioEmailSerializer,
            **KeycloakAdminAPIView.ERROS_PADRAO,
        },
    )
    def post(
        self,
        request: Request,
        usuario_id: str,
    ) -> Response:
        """Altera o e-mail de um usuário e solicita sua verificação.

        Args:
            request: Requisição HTTP contendo o novo e-mail.
            usuario_id: ID interno do usuário no Keycloak.

        Returns:
            Resposta HTTP contendo o resultado da alteração e
            da solicitação de verificação.
        """
        serializer = UsuarioAlterarEmailSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        resultado = UsuarioService().alterar_email(
            usuario_id=usuario_id,
            **serializer.validated_data,
        )

        response = UsuarioEmailSerializer(resultado)

        return Response(
            response.data,
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=_TAG,
    summary="Alterar senha do usuário",
    description="Altera a senha de um usuário.",
)
class UsuarioSenhaView(KeycloakAdminAPIView):
    """Endpoint para alteração da senha de um usuário."""

    @extend_schema(
        request=UsuarioAlterarSenhaSerializer,
        responses={
            204: None,
            **KeycloakAdminAPIView.ERROS_PADRAO,
        },
    )
    def post(
        self,
        request: Request,
        usuario_id: str,
    ) -> Response:
        """Altera a senha de um usuário.

        Args:
            request: Requisição HTTP contendo a nova senha.
            usuario_id: ID interno do usuário no Keycloak.

        Returns:
            Resposta HTTP sem conteúdo.
        """
        serializer = UsuarioAlterarSenhaSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        UsuarioService().alterar_senha(
            usuario_id=usuario_id,
            **serializer.validated_data,
        )

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )


@extend_schema(
    tags=_TAG,
    summary="Gerenciar grupo do usuário",
    description=("Associa ou desassocia um usuário de um grupo específico."),
)
class UsuarioGrupoView(KeycloakAdminAPIView):
    """Endpoint para associação e desassociação de grupo do usuário."""

    @extend_schema(
        summary="Associar usuário ao grupo",
        description="Associa o usuário ao grupo informado.",
        request=UsuarioGrupoSerializer,
        responses={
            200: None,
            **KeycloakAdminAPIView.ERROS_PADRAO,
        },
    )
    def post(
        self,
        request: Request,
        usuario_id: str,
    ) -> Response:
        """Associa um usuário a um grupo.

        Args:
            request: Requisição HTTP contendo o ID do grupo.
            usuario_id: ID interno do usuário no Keycloak.

        Returns:
            Resposta HTTP sem conteúdo.
        """
        serializer = UsuarioGrupoSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        UsuarioService().associar_grupo(
            usuario_id=usuario_id,
            grupo_id=serializer.validated_data["grupo_id"],
        )

        return Response(
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Desassociar usuário do grupo",
        description=(
            "Desassocia o usuário do grupo informado.\n\n"
            "O `grupo_id` identifica o grupo que será desassociado "
            "do usuário."
        ),
        request=UsuarioGrupoSerializer,
        responses={
            200: None,
            **KeycloakAdminAPIView.ERROS_PADRAO,
        },
    )
    def patch(
        self,
        request: Request,
        usuario_id: str,
    ) -> Response:
        """Desassocia um usuário de um grupo.

        Args:
            request: Requisição HTTP contendo o ID do grupo.
            usuario_id: ID interno do usuário no Keycloak.

        Returns:
            Resposta HTTP sem conteúdo.
        """
        serializer = UsuarioGrupoSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        UsuarioService().desassociar_grupo(
            usuario_id=usuario_id,
            grupo_id=serializer.validated_data["grupo_id"],
        )

        return Response(
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=_TAG,
    summary="Gerenciar Realm Role do usuário",
    description=("Associa ou desassocia uma Realm Role de um usuário."),
)
class UsuarioRealmRoleView(KeycloakAdminAPIView):
    """Endpoint para associação e desassociação de Realm Role."""

    @extend_schema(
        summary="Associar Realm Role ao usuário",
        description="Associa a Realm Role informada ao usuário.",
        request=UsuarioRealmRoleSerializer,
        responses={
            200: None,
            **KeycloakAdminAPIView.ERROS_PADRAO,
        },
    )
    def post(
        self,
        request: Request,
        usuario_id: str,
    ) -> Response:
        """Associa uma Realm Role ao usuário.

        Args:
            request: Requisição HTTP contendo o nome da permissão.
            usuario_id: ID interno do usuário no Keycloak.

        Returns:
            Resposta HTTP sem conteúdo.
        """
        serializer = UsuarioRealmRoleSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        UsuarioService().associar_role_realm(
            usuario_id=usuario_id,
            nome_permissao=serializer.validated_data["nome_permissao"],
        )

        return Response(
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Desassociar Realm Role do usuário",
        description=(
            "Desassocia uma Realm Role do usuário.\n\n"
            "O `nome_permissao` identifica a Realm Role "
            "que será desassociada."
        ),
        request=UsuarioRealmRoleSerializer,
        responses={
            200: None,
            **KeycloakAdminAPIView.ERROS_PADRAO,
        },
    )
    def patch(
        self,
        request: Request,
        usuario_id: str,
    ) -> Response:
        """Desassocia uma Realm Role do usuário.

        Args:
            request: Requisição HTTP contendo o nome da permissão.
            usuario_id: ID interno do usuário no Keycloak.

        Returns:
            Resposta HTTP sem conteúdo.
        """
        serializer = UsuarioRealmRoleSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        UsuarioService().desassociar_role_realm(
            usuario_id=usuario_id,
            nome_permissao=serializer.validated_data["nome_permissao"],
        )

        return Response(
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=_TAG,
    summary="Gerenciar Client Role do usuário",
    description=("Associa ou desassocia uma Client Role de um usuário."),
)
class UsuarioClientRoleView(KeycloakAdminAPIView):
    """Endpoint para associação e desassociação de Client Role."""

    @extend_schema(
        summary="Associar Client Role ao usuário",
        description="Associa a Client Role informada ao usuário.",
        request=UsuarioClientRoleSerializer,
        responses={
            200: None,
            **KeycloakAdminAPIView.ERROS_PADRAO,
        },
    )
    def post(
        self,
        request: Request,
        usuario_id: str,
    ) -> Response:
        """Associa uma Client Role ao usuário.

        Args:
            request: Requisição HTTP contendo o client e a permissão.
            usuario_id: ID interno do usuário no Keycloak.

        Returns:
            Resposta HTTP sem conteúdo.
        """
        serializer = UsuarioClientRoleSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        UsuarioService().associar_role_client(
            usuario_id=usuario_id,
            client_uuid=serializer.validated_data["client_uuid"],
            nome_permissao=serializer.validated_data["nome_permissao"],
        )

        return Response(
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        summary="Desassociar Client Role do usuário",
        description=(
            "Desassocia uma Client Role do usuário.\n\n"
            "O `client_uuid` identifica o cliente e "
            "`nome_permissao` identifica a Client Role "
            "que será desassociada."
        ),
        request=UsuarioClientRoleSerializer,
        responses={
            200: None,
            **KeycloakAdminAPIView.ERROS_PADRAO,
        },
    )
    def patch(
        self,
        request: Request,
        usuario_id: str,
    ) -> Response:
        """Desassocia uma Client Role do usuário.

        Args:
            request: Requisição HTTP contendo o client e a permissão.
            usuario_id: ID interno do usuário no Keycloak.

        Returns:
            Resposta HTTP sem conteúdo.
        """
        serializer = UsuarioClientRoleSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        UsuarioService().desassociar_role_client(
            usuario_id=usuario_id,
            client_uuid=serializer.validated_data["client_uuid"],
            nome_permissao=serializer.validated_data["nome_permissao"],
        )

        return Response(
            status=status.HTTP_200_OK,
        )
