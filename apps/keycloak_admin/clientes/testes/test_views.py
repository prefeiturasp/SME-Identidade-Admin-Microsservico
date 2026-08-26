"""Testes das views administrativas de clientes."""

from unittest.mock import MagicMock, patch
from uuid import UUID

from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient


class TestClientListCreateView:
    """Testes do endpoint de consulta e criação de clientes."""

    def setup_method(self) -> None:
        """Inicializa o cliente HTTP de teste."""
        self.client = APIClient()
        self.client.credentials(
            HTTP_X_API_KEY=settings.API_KEY,
        )

    @patch(
        "apps.keycloak_admin.clientes.api.views.ClientService",
    )
    def test_get_consulta_clientes(
        self,
        mock_service: MagicMock,
    ) -> None:
        """Deve consultar os clientes com sucesso."""
        mock_service.return_value.consultar.return_value = [
            {
                "id": "client-123",
                "client_id": "sistema-admin",
                "nome": "Sistema Administrativo",
                "habilitado": True,
                "client_publico": False,
                "protocolo": "openid-connect",
                "redirect_uris": [
                    "https://sistema.example.com/callback",
                ],
                "web_origins": [
                    "https://sistema.example.com",
                ],
                "atributos": {},
            },
        ]

        response = self.client.get(
            reverse("clients"),
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [
            {
                "id": "client-123",
                "client_id": "sistema-admin",
                "nome": "Sistema Administrativo",
                "habilitado": True,
                "client_publico": False,
                "protocolo": "openid-connect",
                "redirect_uris": [
                    "https://sistema.example.com/callback",
                ],
                "web_origins": [
                    "https://sistema.example.com",
                ],
                "atributos": {},
            },
        ]

        mock_service.return_value.consultar.assert_called_once_with()

    @patch(
        "apps.keycloak_admin.clientes.api.views.ClientService",
    )
    def test_get_consulta_com_filtro(
        self,
        mock_service: MagicMock,
    ) -> None:
        """Deve consultar um cliente específico pelo UUID."""
        mock_service.return_value.consultar.return_value = [
            {
                "id": "client-123",
                "client_id": "sistema-admin",
                "nome": "Sistema Administrativo",
                "habilitado": True,
                "client_publico": False,
                "protocolo": "openid-connect",
                "redirect_uris": [],
                "web_origins": [],
                "atributos": {},
            },
        ]

        client_uuid = "550e8400-e29b-41d4-a716-446655440000"

        response = self.client.get(
            reverse("clients"),
            {"client_uuid": client_uuid},
        )

        assert response.status_code == status.HTTP_200_OK

        mock_service.return_value.consultar.assert_called_once_with(
            client_uuid=UUID(client_uuid),
        )

    @patch(
        "apps.keycloak_admin.clientes.api.views.ClientService",
    )
    def test_post_cria_cliente(
        self,
        mock_service: MagicMock,
    ) -> None:
        """Deve criar um cliente com sucesso."""
        mock_service.return_value.criar.return_value = "client-123"

        dados = {
            "client_id": "sistema-admin",
            "nome": "Sistema Administrativo",
            "descricao": "Cliente administrativo",
            "habilitado": True,
            "client_publico": False,
            "protocolo": "openid-connect",
            "redirect_uris": [
                "https://sistema.example.com/callback",
            ],
            "web_origins": [
                "https://sistema.example.com",
            ],
            "atributos": {},
        }

        response = self.client.post(
            reverse("clients"),
            dados,
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {
            "id": "client-123",
        }

        mock_service.return_value.criar.assert_called_once_with(
            **dados,
        )

    def test_post_rejeita_dados_invalidos(self) -> None:
        """Não deve criar cliente sem client_id."""
        response = self.client.post(
            reverse("clients"),
            {
                "nome": "Sistema Administrativo",
            },
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "client_id" in response.json()


class TestClientDetailView:
    """Testes do endpoint de atualização de clientes."""

    def setup_method(self) -> None:
        """Inicializa o cliente HTTP de teste."""
        self.client = APIClient()
        self.client.credentials(
            HTTP_X_API_KEY=settings.API_KEY,
        )

    @patch(
        "apps.keycloak_admin.clientes.api.views.ClientService",
    )
    def test_patch_atualiza_cliente(
        self,
        mock_service: MagicMock,
    ) -> None:
        """Deve atualizar um cliente com sucesso."""
        client_uuid = "550e8400-e29b-41d4-a716-446655440000"

        dados = {
            "nome": "Sistema Administrativo Atualizado",
            "habilitado": False,
        }

        response = self.client.patch(
            reverse(
                "client-detail",
                kwargs={
                    "client_uuid": client_uuid,
                },
            ),
            dados,
            format="json",
        )

        assert response.status_code == status.HTTP_200_OK

        mock_service.return_value.atualizar.assert_called_once_with(
            client_uuid=client_uuid,
            **dados,
        )

    def test_patch_rejeita_client_id_invalido(self) -> None:
        """Não deve aceitar client_id acima do tamanho máximo."""
        client_uuid = "550e8400-e29b-41d4-a716-446655440000"

        dados = {
            "client_id": "a" * 256,
        }

        response = self.client.patch(
            reverse(
                "client-detail",
                kwargs={
                    "client_uuid": client_uuid,
                },
            ),
            dados,
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "client_id" in response.json()

    def test_patch_rejeita_redirect_uri_invalida(self) -> None:
        """Não deve aceitar uma URI de redirecionamento inválida."""
        client_uuid = "550e8400-e29b-41d4-a716-446655440000"

        dados = {
            "redirect_uris": [
                "uri-invalida",
            ],
        }

        response = self.client.patch(
            reverse(
                "client-detail",
                kwargs={
                    "client_uuid": client_uuid,
                },
            ),
            dados,
            format="json",
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "redirect_uris" in response.json()
