"""Testes das views do módulo de grupos."""

from unittest.mock import MagicMock, patch

from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


class TestGrupoListCreateView:
    """Testes da view GrupoListCreateView."""

    def setup_method(self) -> None:
        """Configura o cliente autenticado para os testes."""
        self.client = APIClient()
        self.client.credentials(
            HTTP_X_API_KEY=settings.API_KEY,
        )

    @patch(
        "apps.keycloak_admin.grupos.api.views.GrupoService.consultar",
    )
    def test_get_consulta_grupos(
        self,
        mock_consultar: MagicMock,
    ) -> None:
        """Deve consultar todos os grupos."""
        mock_consultar.return_value = [
            {
                "id": "grupo-1",
                "nome": "Administradores",
                "caminho": "/Administradores",
                "atributos": {},
                "subgrupos": [],
            },
        ]

        response = self.client.get(
            reverse("grupo-list-create"),
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == mock_consultar.return_value

        mock_consultar.assert_called_once_with(
            limite=100,
        )

    @patch(
        "apps.keycloak_admin.grupos.api.views.GrupoService.consultar",
    )
    def test_get_consulta_com_filtro(
        self,
        mock_consultar: MagicMock,
    ) -> None:
        """Deve consultar grupos utilizando um filtro."""
        mock_consultar.return_value = [
            {
                "id": "grupo-1",
                "nome": "Administradores",
                "caminho": "/Administradores",
                "atributos": {},
                "subgrupos": [],
            },
        ]

        response = self.client.get(
            reverse("grupo-list-create"),
            {"grupo_id": "grupo-1"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == mock_consultar.return_value

        mock_consultar.assert_called_once_with(
            grupo_id="grupo-1",
            limite=100,
        )

    @patch(
        "apps.keycloak_admin.grupos.api.views.GrupoService.criar",
    )
    def test_post_cria_grupo(
        self,
        mock_criar: MagicMock,
    ) -> None:
        """Deve criar um grupo."""
        response = self.client.post(
            reverse("grupo-list-create"),
            {
                "nome": "Administradores",
                "caminho": "/Administradores",
                "atributos": {
                    "tipo": ["administrativo"],
                },
            },
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {
            "mensagem": "Grupo criado com sucesso.",
        }

        mock_criar.assert_called_once_with(
            nome="Administradores",
            caminho="/Administradores",
            atributos={
                "tipo": ["administrativo"],
            },
        )

    def test_post_rejeita_nome_ausente(
        self,
    ) -> None:
        """Deve rejeitar a criação sem nome."""
        response = self.client.post(
            reverse("grupo-list-create"),
            {
                "caminho": "/Administradores",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestGrupoDetailView:
    """Testes da view GrupoDetailView."""

    def setup_method(self) -> None:
        """Configura o cliente autenticado para os testes."""
        self.client = APIClient()
        self.client.credentials(
            HTTP_X_API_KEY=settings.API_KEY,
        )

    @patch(
        "apps.keycloak_admin.grupos.api.views.GrupoService.atualizar",
    )
    def test_patch_atualiza_grupo(
        self,
        mock_atualizar: MagicMock,
    ) -> None:
        """Deve atualizar um grupo."""
        response = self.client.patch(
            reverse(
                "grupo-detail",
                kwargs={"grupo_id": "grupo-1"},
            ),
            {
                "nome": "Administradores Atualizados",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "mensagem": "Grupo atualizado com sucesso.",
        }

        mock_atualizar.assert_called_once_with(
            grupo_id="grupo-1",
            nome="Administradores Atualizados",
        )

    def test_patch_rejeita_dados_vazios(
        self,
    ) -> None:
        """Deve rejeitar atualização sem nenhum campo."""
        response = self.client.patch(
            reverse(
                "grupo-detail",
                kwargs={"grupo_id": "grupo-1"},
            ),
            {},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestGrupoRealmRoleView:
    """Testes da view GrupoRealmRoleView."""

    def setup_method(self) -> None:
        """Configura o cliente autenticado para os testes."""
        self.client = APIClient()
        self.client.credentials(
            HTTP_X_API_KEY=settings.API_KEY,
        )

    @patch(
        "apps.keycloak_admin.grupos.api.views.GrupoService.associar_role_realm",
    )
    def test_post_associa_realm_role(
        self,
        mock_associar: MagicMock,
    ) -> None:
        """Deve associar uma Realm Role ao grupo."""
        response = self.client.post(
            reverse(
                "grupo-realm-role",
                kwargs={"grupo_id": "grupo-1"},
            ),
            {
                "nome_permissao": "administrador",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "mensagem": "Realm Role associada com sucesso.",
        }

        mock_associar.assert_called_once_with(
            grupo_id="grupo-1",
            nome_role="administrador",
        )

    @patch(
        "apps.keycloak_admin.grupos.api.views.GrupoService.desassociar_role_realm",
    )
    def test_patch_desassocia_realm_role(
        self,
        mock_desassociar: MagicMock,
    ) -> None:
        """Deve desassociar uma Realm Role do grupo."""
        response = self.client.patch(
            reverse(
                "grupo-realm-role",
                kwargs={"grupo_id": "grupo-1"},
            ),
            {
                "nome_permissao": "administrador",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "mensagem": "Realm Role desassociada com sucesso.",
        }

        mock_desassociar.assert_called_once_with(
            grupo_id="grupo-1",
            nome_role="administrador",
        )

    def test_post_rejeita_role_ausente(
        self,
    ) -> None:
        """Deve rejeitar associação sem nome da permissão."""
        response = self.client.post(
            reverse(
                "grupo-realm-role",
                kwargs={"grupo_id": "grupo-1"},
            ),
            {},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_patch_rejeita_role_ausente(
        self,
    ) -> None:
        """Deve rejeitar desassociação sem nome da permissão."""
        response = self.client.patch(
            reverse(
                "grupo-realm-role",
                kwargs={"grupo_id": "grupo-1"},
            ),
            {},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestGrupoClientRoleView:
    """Testes da view GrupoClientRoleView."""

    def setup_method(self) -> None:
        """Configura o cliente autenticado para os testes."""
        self.client = APIClient()
        self.client.credentials(
            HTTP_X_API_KEY=settings.API_KEY,
        )

    @patch(
        "apps.keycloak_admin.grupos.api.views.GrupoService.associar_role_client",
    )
    def test_post_associa_client_role(
        self,
        mock_associar: MagicMock,
    ) -> None:
        """Deve associar uma Client Role ao grupo."""
        response = self.client.post(
            reverse(
                "grupo-client-role",
                kwargs={
                    "grupo_id": "grupo-1",
                    "client_uuid": "client-1",
                },
            ),
            {
                "nome_permissao": "visualizar",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "mensagem": "Client Role associada com sucesso.",
        }

        mock_associar.assert_called_once_with(
            grupo_id="grupo-1",
            client_uuid="client-1",
            nome_role="visualizar",
        )

    @patch(
        "apps.keycloak_admin.grupos.api.views.GrupoService.desassociar_role_client",
    )
    def test_patch_desassocia_client_role(
        self,
        mock_desassociar: MagicMock,
    ) -> None:
        """Deve desassociar uma Client Role do grupo."""
        response = self.client.patch(
            reverse(
                "grupo-client-role",
                kwargs={
                    "grupo_id": "grupo-1",
                    "client_uuid": "client-1",
                },
            ),
            {
                "nome_permissao": "visualizar",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "mensagem": "Client Role desassociada com sucesso.",
        }

        mock_desassociar.assert_called_once_with(
            grupo_id="grupo-1",
            client_uuid="client-1",
            nome_role="visualizar",
        )

    def test_post_rejeita_client_role_ausente(
        self,
    ) -> None:
        """Deve rejeitar associação sem nome da permissão."""
        response = self.client.post(
            reverse(
                "grupo-client-role",
                kwargs={
                    "grupo_id": "grupo-1",
                    "client_uuid": "client-1",
                },
            ),
            {},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_patch_rejeita_client_role_ausente(
        self,
    ) -> None:
        """Deve rejeitar desassociação sem nome da permissão."""
        response = self.client.patch(
            reverse(
                "grupo-client-role",
                kwargs={
                    "grupo_id": "grupo-1",
                    "client_uuid": "client-1",
                },
            ),
            {},
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
