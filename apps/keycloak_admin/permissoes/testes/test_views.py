"""Testes das views administrativas de permissões."""

from unittest.mock import MagicMock, patch

from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


class TestRealmRoleListCreateView:
    """Testes da view de consulta e criação de Realm Roles."""

    def setup_method(self) -> None:
        """Configura o cliente autenticado."""
        self.client = APIClient()
        self.client.credentials(
            HTTP_X_API_KEY=settings.API_KEY,
        )

    @patch(
        "apps.keycloak_admin.permissoes.api.views.RoleService.consultar",
    )
    def test_get_consulta_permissoes(
        self,
        mock_consultar: MagicMock,
    ) -> None:
        """Deve consultar as permissões de Realm."""
        mock_consultar.return_value = [
            {
                "id": "role-123",
                "nome": "administrador",
                "descricao": "Permissão administrativa",
                "composite": False,
                "container_id": "realm-123",
                "atributos": {},
            },
        ]

        response = self.client.get(
            reverse("permissoes-realm"),
        )

        assert response.status_code == status.HTTP_200_OK

        mock_consultar.assert_called_once_with(
            tipo="realm",
            limite=100,
        )

        assert response.json() == [
            {
                "id": "role-123",
                "nome": "administrador",
                "descricao": "Permissão administrativa",
                "composite": False,
                "container_id": "realm-123",
                "atributos": {},
            },
        ]

    @patch(
        "apps.keycloak_admin.permissoes.api.views.RoleService.consultar",
    )
    def test_get_consulta_com_filtro(
        self,
        mock_consultar: MagicMock,
    ) -> None:
        """Deve consultar uma permissão de Realm pelo nome."""
        mock_consultar.return_value = [
            {
                "id": "role-123",
                "nome": "administrador",
                "descricao": "Permissão administrativa",
                "composite": False,
                "container_id": "realm-123",
                "atributos": {},
            },
        ]

        response = self.client.get(
            reverse("permissoes-realm"),
            {"nome": "administrador"},
        )

        assert response.status_code == status.HTTP_200_OK

        mock_consultar.assert_called_once_with(
            tipo="realm",
            nome="administrador",
            limite=100,
        )

        assert response.json() == [
            {
                "id": "role-123",
                "nome": "administrador",
                "descricao": "Permissão administrativa",
                "composite": False,
                "container_id": "realm-123",
                "atributos": {},
            },
        ]

    @patch(
        "apps.keycloak_admin.permissoes.api.views.RoleService.criar",
    )
    def test_post_cria_permissao(
        self,
        mock_criar: MagicMock,
    ) -> None:
        """Deve criar uma permissão de Realm."""
        response = self.client.post(
            reverse("permissoes-realm"),
            {
                "nome": "administrador",
                "descricao": "Permissão administrativa",
                "atributos": {
                    "sistema": ["admin"],
                },
            },
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED

        mock_criar.assert_called_once_with(
            tipo="realm",
            nome="administrador",
            descricao="Permissão administrativa",
            atributos={
                "sistema": ["admin"],
            },
        )

        assert response.json() == {
            "mensagem": "Permissão criada com sucesso.",
        }

    def test_post_rejeita_dados_invalidos(self) -> None:
        """Não deve criar permissão sem nome."""
        response = self.client.post(
            reverse("permissoes-realm"),
            {},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestRealmRoleDetailView:
    """Testes da view de atualização de Realm Roles."""

    def setup_method(self) -> None:
        """Configura o cliente autenticado."""
        self.client = APIClient()
        self.client.credentials(
            HTTP_X_API_KEY=settings.API_KEY,
        )

    @patch(
        "apps.keycloak_admin.permissoes.api.views.RoleService.atualizar",
    )
    def test_patch_atualiza_permissao(
        self,
        mock_atualizar: MagicMock,
    ) -> None:
        """Deve atualizar uma permissão de Realm."""
        response = self.client.patch(
            reverse(
                "permissao-realm-detail",
                kwargs={
                    "nome": "administrador",
                },
            ),
            {
                "novo_nome": "admin",
                "descricao": "Nova descrição",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

        mock_atualizar.assert_called_once_with(
            nome="administrador",
            tipo="realm",
            novo_nome="admin",
            descricao="Nova descrição",
        )

        assert response.json() == {
            "mensagem": "Permissão atualizada com sucesso.",
        }

    def test_patch_rejeita_dados_vazios(self) -> None:
        """Não deve atualizar uma permissão sem campos."""
        response = self.client.patch(
            reverse(
                "permissao-realm-detail",
                kwargs={
                    "nome": "administrador",
                },
            ),
            {},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestClientRoleListCreateView:
    """Testes da view de consulta e criação de Client Roles."""

    def setup_method(self) -> None:
        """Configura o cliente autenticado."""
        self.client = APIClient()
        self.client.credentials(
            HTTP_X_API_KEY=settings.API_KEY,
        )

    @patch(
        "apps.keycloak_admin.permissoes.api.views.RoleService.consultar",
    )
    def test_get_consulta_permissoes_cliente(
        self,
        mock_consultar: MagicMock,
    ) -> None:
        """Deve consultar as permissões de um cliente."""
        mock_consultar.return_value = [
            {
                "id": "role-123",
                "nome": "administrador",
                "descricao": "Permissão administrativa",
                "composite": False,
                "container_id": "client-123",
                "atributos": {},
            },
        ]

        response = self.client.get(
            reverse(
                "permissoes-cliente",
                kwargs={
                    "client_uuid": "client-123",
                },
            ),
        )

        assert response.status_code == status.HTTP_200_OK

        mock_consultar.assert_called_once_with(
            tipo="client",
            client_uuid="client-123",
            limite=100,
        )

        assert response.json() == [
            {
                "id": "role-123",
                "nome": "administrador",
                "descricao": "Permissão administrativa",
                "composite": False,
                "container_id": "client-123",
                "atributos": {},
            },
        ]

    @patch(
        "apps.keycloak_admin.permissoes.api.views.RoleService.consultar",
    )
    def test_get_consulta_cliente_com_filtro(
        self,
        mock_consultar: MagicMock,
    ) -> None:
        """Deve consultar uma Client Role pelo nome."""
        mock_consultar.return_value = [
            {
                "id": "role-123",
                "nome": "administrador",
                "descricao": "Permissão administrativa",
                "composite": False,
                "container_id": "client-123",
                "atributos": {},
            },
        ]

        response = self.client.get(
            reverse(
                "permissoes-cliente",
                kwargs={
                    "client_uuid": "client-123",
                },
            ),
            {
                "nome": "administrador",
            },
        )

        assert response.status_code == status.HTTP_200_OK

        mock_consultar.assert_called_once_with(
            tipo="client",
            client_uuid="client-123",
            nome="administrador",
            limite=100,
        )

        assert response.json() == [
            {
                "id": "role-123",
                "nome": "administrador",
                "descricao": "Permissão administrativa",
                "composite": False,
                "container_id": "client-123",
                "atributos": {},
            },
        ]

    @patch(
        "apps.keycloak_admin.permissoes.api.views.RoleService.criar",
    )
    def test_post_cria_permissao_cliente(
        self,
        mock_criar: MagicMock,
    ) -> None:
        """Deve criar uma Client Role."""
        response = self.client.post(
            reverse(
                "permissoes-cliente",
                kwargs={
                    "client_uuid": "client-123",
                },
            ),
            {
                "nome": "administrador",
                "descricao": "Permissão administrativa",
                "atributos": {
                    "sistema": ["admin"],
                },
            },
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED

        mock_criar.assert_called_once_with(
            tipo="client",
            client_uuid="client-123",
            nome="administrador",
            descricao="Permissão administrativa",
            atributos={
                "sistema": ["admin"],
            },
        )

        assert response.json() == {
            "mensagem": "Permissão criada com sucesso.",
        }

    def test_post_rejeita_dados_invalidos(self) -> None:
        """Não deve criar Client Role sem nome."""
        response = self.client.post(
            reverse(
                "permissoes-cliente",
                kwargs={
                    "client_uuid": "client-123",
                },
            ),
            {},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestClientRoleDetailView:
    """Testes da view de atualização de Client Roles."""

    def setup_method(self) -> None:
        """Configura o cliente autenticado."""
        self.client = APIClient()
        self.client.credentials(
            HTTP_X_API_KEY=settings.API_KEY,
        )

    @patch(
        "apps.keycloak_admin.permissoes.api.views.RoleService.atualizar",
    )
    def test_patch_atualiza_permissao_cliente(
        self,
        mock_atualizar: MagicMock,
    ) -> None:
        """Deve atualizar uma Client Role."""
        response = self.client.patch(
            reverse(
                "permissao-cliente-detail",
                kwargs={
                    "client_uuid": "client-123",
                    "nome": "administrador",
                },
            ),
            {
                "novo_nome": "admin",
                "descricao": "Nova descrição",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

        mock_atualizar.assert_called_once_with(
            nome="administrador",
            tipo="client",
            client_uuid="client-123",
            novo_nome="admin",
            descricao="Nova descrição",
        )

        assert response.json() == {
            "mensagem": "Permissão atualizada com sucesso.",
        }

    def test_patch_rejeita_dados_vazios(self) -> None:
        """Não deve atualizar uma Client Role sem campos."""
        response = self.client.patch(
            reverse(
                "permissao-cliente-detail",
                kwargs={
                    "client_uuid": "client-123",
                    "nome": "administrador",
                },
            ),
            {},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
