"""Testes para apps.autenticacao.api.credencials_client."""

from __future__ import annotations

from typing import Any
from unittest.mock import Mock, patch

from django.test import RequestFactory, SimpleTestCase, override_settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request

from apps.autenticacao.api.credencials_client import (
    AutenticacaoCredenciaisCliente,
)


@override_settings(
    CLIENT_ID_HEADER="X-Client-Id",
    CLIENT_SECRET_HEADER="X-Client-Secret",
)
class TestAutenticacaoCredenciaisCliente(SimpleTestCase):
    """Testa a autenticação por credenciais de cliente."""

    def setUp(self) -> None:
        """Cria os objetos utilizados pelos testes."""
        self.factory = RequestFactory()
        self.auth = AutenticacaoCredenciaisCliente()

    def _drf_request(
        self,
        headers: dict[str, str] | None = None,
    ) -> Request:
        """Cria uma requisição DRF para os testes."""
        extra: dict[str, Any] = headers or {}

        rf_request = self.factory.get("/", **extra)
        return Request(rf_request)

    def test_sem_headers_retorna_none(self) -> None:
        """Verifica que a ausência dos headers retorna None."""
        req = self._drf_request()

        assert self.auth.authenticate(req) is None

    def test_com_apenas_um_header_retorna_none(self) -> None:
        """Verifica que credenciais incompletas não autenticam."""
        req = self._drf_request({"HTTP_X_CLIENT_ID": "cliente"})

        assert self.auth.authenticate(req) is None

    @patch("apps.autenticacao.api.credencials_client.KeycloakAdminService")
    def test_credenciais_validas_autenticam(
        self,
        servico_keycloak: Mock,
    ) -> None:
        """Verifica que credenciais válidas retornam usuário autenticado."""
        servico_keycloak.return_value.authenticate_client.return_value = {
            "access_token": "token"
        }
        req = self._drf_request(
            {
                "HTTP_X_CLIENT_ID": "cliente",
                "HTTP_X_CLIENT_SECRET": "segredo",
            }
        )

        resultado = self.auth.authenticate(req)

        assert resultado is not None
        usuario, autenticador = resultado
        assert usuario.is_authenticated is True
        assert autenticador is None
        servico_keycloak.return_value.authenticate_client.assert_called_once_with(
            "cliente", "segredo"
        )

    @patch("apps.autenticacao.api.credencials_client.KeycloakAdminService")
    def test_credenciais_invalidas_lancam_excecao(
        self,
        servico_keycloak: Mock,
    ) -> None:
        """Verifica que o Keycloak rejeita credenciais inválidas."""
        servico_keycloak.return_value.authenticate_client.return_value = None
        req = self._drf_request(
            {
                "HTTP_X_CLIENT_ID": "cliente",
                "HTTP_X_CLIENT_SECRET": "segredo-incorreto",
            }
        )

        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(req)

    def test_authenticate_header_retorna_headers_configurados(self) -> None:
        """Verifica que authenticate_header retorna os headers esperados."""
        req = self._drf_request()

        assert self.auth.authenticate_header(req) == [
            "X-Client-Id",
            "X-Client-Secret",
        ]

    @override_settings(
        CLIENT_ID_HEADER="X-Internal-Client-Id",
        CLIENT_SECRET_HEADER="X-Internal-Client-Secret",
    )
    @patch("apps.autenticacao.api.credencials_client.KeycloakAdminService")
    def test_headers_com_hifens_sao_normalizados(
        self,
        servico_keycloak: Mock,
    ) -> None:
        """Verifica a normalização de headers configurados com hífens."""
        servico_keycloak.return_value.authenticate_client.return_value = {
            "access_token": "token"
        }
        req = self._drf_request(
            {
                "HTTP_X_INTERNAL_CLIENT_ID": "cliente",
                "HTTP_X_INTERNAL_CLIENT_SECRET": "segredo",
            }
        )

        assert self.auth.authenticate(req) is not None
