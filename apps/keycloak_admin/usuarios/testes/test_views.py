"""Testes das views administrativas de usuários."""

from unittest.mock import MagicMock, patch

import pytest
from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


@pytest.fixture
def client() -> APIClient:
    """Retorna um cliente autenticado com API Key."""
    client = APIClient()
    client.credentials(
        HTTP_X_API_KEY=settings.API_KEY,
    )
    return client


class TestUsuarioListCreateView:
    """Testes da view de consulta e criação de usuários."""

    @patch("apps.keycloak_admin.usuarios.api.views.UsuarioService")
    def test_get_consulta_usuarios(
        self,
        mock_service: MagicMock,
        client: APIClient,
    ) -> None:
        """Deve consultar usuários."""
        mock_service.return_value.consultar.return_value = [
            {
                "id": "usuario-123",
                "username": "usuario.teste",
                "firstName": "Usuário",
                "lastName": "Teste",
                "email": "usuario@example.com",
                "enabled": True,
                "emailVerified": True,
                "cpf": "12345678901",
                "rf": "RF123",
            },
        ]

        response = client.get(
            reverse("usuarios"),
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [
            {
                "id": "usuario-123",
                "username": "usuario.teste",
                "firstName": "Usuário",
                "lastName": "Teste",
                "email": "usuario@example.com",
                "enabled": True,
                "emailVerified": True,
                "cpf": "12345678901",
                "rf": "RF123",
            },
        ]

        mock_service.return_value.consultar.assert_called_once_with(
            limite=100,
        )

    @patch("apps.keycloak_admin.usuarios.api.views.UsuarioService")
    def test_get_consulta_com_filtro(
        self,
        mock_service: MagicMock,
        client: APIClient,
    ) -> None:
        """Deve consultar usuários utilizando filtro."""
        mock_service.return_value.consultar.return_value = []

        response = client.get(
            reverse("usuarios"),
            {"cpf": "12345678901"},
        )

        assert response.status_code == status.HTTP_200_OK

        mock_service.return_value.consultar.assert_called_once_with(
            cpf="12345678901",
            limite=100,
        )

    @patch("apps.keycloak_admin.usuarios.api.views.UsuarioService")
    def test_post_cria_usuario(
        self,
        mock_service: MagicMock,
        client: APIClient,
    ) -> None:
        """Deve criar um usuário."""
        mock_service.return_value.criar.return_value = "usuario-123"

        dados = {
            "usuario": "usuario.teste",
            "nome": "Usuário",
            "sobrenome": "Teste",
            "email": "usuario@example.com",
            "cpf": "12345678901",
            "rf": "RF123",
        }

        response = client.post(
            reverse("usuarios"),
            dados,
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {
            "id": "usuario-123",
        }

        mock_service.return_value.criar.assert_called_once_with(
            **dados,
        )

    def test_post_rejeita_dados_invalidos(
        self,
        client: APIClient,
    ) -> None:
        """Deve rejeitar criação sem os campos obrigatórios."""
        response = client.post(
            reverse("usuarios"),
            {},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestUsuarioDetailView:
    """Testes da view de gerenciamento de usuário."""

    @patch("apps.keycloak_admin.usuarios.api.views.UsuarioService")
    def test_patch_atualiza_usuario(
        self,
        mock_service: MagicMock,
        client: APIClient,
    ) -> None:
        """Deve atualizar os dados do usuário."""
        dados = {
            "nome": "Novo Nome",
            "sobrenome": "Novo Sobrenome",
            "habilitado": False,
        }

        response = client.patch(
            reverse(
                "usuario-detail",
                kwargs={"usuario_id": "usuario-123"},
            ),
            dados,
            format="json",
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        mock_service.return_value.atualizar.assert_called_once_with(
            usuario_id="usuario-123",
            **dados,
        )

    def test_patch_rejeita_dados_invalidos(
        self,
        client: APIClient,
    ) -> None:
        """Deve rejeitar dados inválidos na atualização."""
        response = client.patch(
            reverse(
                "usuario-detail",
                kwargs={"usuario_id": "usuario-123"},
            ),
            {
                "habilitado": "valor-invalido",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestUsuarioEmailView:
    """Testes da view de alteração de e-mail."""

    @patch("apps.keycloak_admin.usuarios.api.views.UsuarioService")
    def test_post_altera_email(
        self,
        mock_service: MagicMock,
        client: APIClient,
    ) -> None:
        """Deve alterar o e-mail do usuário."""
        mock_service.return_value.alterar_email.return_value = {
            "email_alterado": True,
            "verificacao_enviada": True,
        }

        dados = {
            "email": "novo@example.com",
        }

        response = client.post(
            reverse(
                "usuario-email",
                kwargs={"usuario_id": "usuario-123"},
            ),
            dados,
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "email_alterado": True,
            "verificacao_enviada": True,
        }

        mock_service.return_value.alterar_email.assert_called_once_with(
            usuario_id="usuario-123",
            email="novo@example.com",
        )


class TestUsuarioSenhaView:
    """Testes da view de alteração de senha."""

    @patch("apps.keycloak_admin.usuarios.api.views.UsuarioService")
    def test_post_altera_senha(
        self,
        mock_service: MagicMock,
        client: APIClient,
    ) -> None:
        """Deve alterar a senha do usuário."""
        dados = {
            "senha": "NovaSenha123!",
        }

        response = client.post(
            reverse(
                "usuario-senha",
                kwargs={"usuario_id": "usuario-123"},
            ),
            dados,
            format="json",
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        mock_service.return_value.alterar_senha.assert_called_once_with(
            usuario_id="usuario-123",
            senha="NovaSenha123!",
        )

    def test_post_rejeita_senha_invalida(
        self,
        client: APIClient,
    ) -> None:
        """Deve rejeitar alteração sem senha."""
        response = client.post(
            reverse(
                "usuario-senha",
                kwargs={"usuario_id": "usuario-123"},
            ),
            {},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestUsuarioGrupoView:
    """Testes da view de gerenciamento de grupos."""

    @patch("apps.keycloak_admin.usuarios.api.views.UsuarioService")
    def test_post_associa_grupo(
        self,
        mock_service: MagicMock,
        client: APIClient,
    ) -> None:
        """Deve associar o usuário a um grupo."""
        response = client.post(
            reverse(
                "usuario-grupo",
                kwargs={"usuario_id": "usuario-123"},
            ),
            {
                "grupo_id": "grupo-123",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

        mock_service.return_value.associar_grupo.assert_called_once_with(
            usuario_id="usuario-123",
            grupo_id="grupo-123",
        )

    @patch("apps.keycloak_admin.usuarios.api.views.UsuarioService")
    def test_patch_desassocia_grupo(
        self,
        mock_service: MagicMock,
        client: APIClient,
    ) -> None:
        """Deve desassociar o usuário de um grupo."""
        response = client.patch(
            reverse(
                "usuario-grupo",
                kwargs={"usuario_id": "usuario-123"},
            ),
            {
                "grupo_id": "grupo-123",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

        mock_service.return_value.desassociar_grupo.assert_called_once_with(
            usuario_id="usuario-123",
            grupo_id="grupo-123",
        )

    @pytest.mark.parametrize("metodo", ["post", "patch"])
    def test_rejeita_grupo_ausente(
        self,
        client: APIClient,
        metodo: str,
    ) -> None:
        """Deve rejeitar operação sem grupo."""
        response = getattr(client, metodo)(
            reverse(
                "usuario-grupo",
                kwargs={"usuario_id": "usuario-123"},
            ),
            {},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestUsuarioRealmRoleView:
    """Testes da view de gerenciamento de Realm Roles."""

    @patch("apps.keycloak_admin.usuarios.api.views.UsuarioService")
    def test_post_associa_realm_role(
        self,
        mock_service: MagicMock,
        client: APIClient,
    ) -> None:
        """Deve associar uma Realm Role."""
        response = client.post(
            reverse(
                "usuario-realm-role",
                kwargs={"usuario_id": "usuario-123"},
            ),
            {
                "nome_permissao": "administrador",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

        mock_service.return_value.associar_role_realm.assert_called_once_with(
            usuario_id="usuario-123",
            nome_permissao="administrador",
        )

    @patch("apps.keycloak_admin.usuarios.api.views.UsuarioService")
    def test_patch_desassocia_realm_role(
        self,
        mock_service: MagicMock,
        client: APIClient,
    ) -> None:
        """Deve desassociar uma Realm Role."""
        response = client.patch(
            reverse(
                "usuario-realm-role",
                kwargs={"usuario_id": "usuario-123"},
            ),
            {
                "nome_permissao": "administrador",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

        mock_service.return_value.desassociar_role_realm.assert_called_once_with(
            usuario_id="usuario-123",
            nome_permissao="administrador",
        )

    @pytest.mark.parametrize("metodo", ["post", "patch"])
    def test_rejeita_role_ausente(
        self,
        client: APIClient,
        metodo: str,
    ) -> None:
        """Deve rejeitar operação sem nome da permissão."""
        response = getattr(client, metodo)(
            reverse(
                "usuario-realm-role",
                kwargs={"usuario_id": "usuario-123"},
            ),
            {},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestUsuarioClientRoleView:
    """Testes da view de gerenciamento de Client Roles."""

    @patch("apps.keycloak_admin.usuarios.api.views.UsuarioService")
    def test_post_associa_client_role(
        self,
        mock_service: MagicMock,
        client: APIClient,
    ) -> None:
        """Deve associar uma Client Role."""
        dados = {
            "client_uuid": "client-123",
            "nome_permissao": "administrador",
        }

        response = client.post(
            reverse(
                "usuario-client-role",
                kwargs={"usuario_id": "usuario-123"},
            ),
            dados,
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

        mock_service.return_value.associar_role_client.assert_called_once_with(
            usuario_id="usuario-123",
            client_uuid="client-123",
            nome_permissao="administrador",
        )

    @patch("apps.keycloak_admin.usuarios.api.views.UsuarioService")
    def test_patch_desassocia_client_role(
        self,
        mock_service: MagicMock,
        client: APIClient,
    ) -> None:
        """Deve desassociar uma Client Role."""
        dados = {
            "client_uuid": "client-123",
            "nome_permissao": "administrador",
        }

        response = client.patch(
            reverse(
                "usuario-client-role",
                kwargs={"usuario_id": "usuario-123"},
            ),
            dados,
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

        mock_service.return_value.desassociar_role_client.assert_called_once_with(
            usuario_id="usuario-123",
            client_uuid="client-123",
            nome_permissao="administrador",
        )

    @pytest.mark.parametrize("metodo", ["post", "patch"])
    def test_rejeita_client_role_invalida(
        self,
        client: APIClient,
        metodo: str,
    ) -> None:
        """Deve rejeitar operação sem os dados obrigatórios."""
        response = getattr(client, metodo)(
            reverse(
                "usuario-client-role",
                kwargs={"usuario_id": "usuario-123"},
            ),
            {},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
