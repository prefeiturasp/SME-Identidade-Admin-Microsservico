"""Testes das views administrativas de sessões."""

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


class TestSessaoListView:
    """Testes da view de consulta de sessões."""

    @patch("apps.keycloak_admin.sessoes.api.views.SessaoService")
    def test_get_consulta_sessoes(
        self,
        mock_service: MagicMock,
        client: APIClient,
    ) -> None:
        """Deve consultar as sessões ativas de um usuário."""
        mock_service.return_value.consultar.return_value = [
            {
                "id": "sessao-123",
                "usuario_id": "usuario-123",
                "usuario": "usuario.teste",
                "clientes": {
                    "cliente-123": "sistema-teste",
                },
                "endereco_ip": "192.168.0.10",
                "inicio": 1724000000000,
                "ultimo_acesso": 1724001000000,
            },
        ]

        response = client.get(
            reverse(
                "sessao-list",
                kwargs={
                    "usuario_id": "usuario-123",
                },
            ),
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [
            {
                "id": "sessao-123",
                "usuario_id": "usuario-123",
                "usuario": "usuario.teste",
                "clientes": {
                    "cliente-123": "sistema-teste",
                },
                "endereco_ip": "192.168.0.10",
                "inicio": 1724000000000,
                "ultimo_acesso": 1724001000000,
            },
        ]

        mock_service.return_value.consultar.assert_called_once_with(
            usuario_id="usuario-123",
        )

    @patch("apps.keycloak_admin.sessoes.api.views.SessaoService")
    def test_get_retorna_lista_vazia(
        self,
        mock_service: MagicMock,
        client: APIClient,
    ) -> None:
        """Deve retornar uma lista vazia quando não houver sessões."""
        mock_service.return_value.consultar.return_value = []

        response = client.get(
            reverse(
                "sessao-list",
                kwargs={
                    "usuario_id": "usuario-123",
                },
            ),
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

        mock_service.return_value.consultar.assert_called_once_with(
            usuario_id="usuario-123",
        )


class TestSessaoLogoutView:
    """Testes da view de encerramento de sessões."""

    @patch("apps.keycloak_admin.sessoes.api.views.SessaoService")
    def test_post_encerra_sessoes(
        self,
        mock_service: MagicMock,
        client: APIClient,
    ) -> None:
        """Deve encerrar todas as sessões do usuário."""
        response = client.post(
            reverse(
                "sessao-logout",
                kwargs={
                    "usuario_id": "usuario-123",
                },
            ),
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "mensagem": ("Sessões do usuário encerradas com sucesso."),
        }

        mock_service.return_value.encerrar.assert_called_once_with(
            usuario_id="usuario-123",
        )
