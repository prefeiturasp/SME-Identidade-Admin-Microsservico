"""Testes das views base da API administrativa do Keycloak."""

from unittest.mock import Mock, patch

from django.test import SimpleTestCase
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.keycloak_admin.api.base import KeycloakAdminAPIView
from apps.keycloak_admin.exceptions import KeycloakAdminError


class KeycloakAdminAPIViewTestCase(SimpleTestCase):
    """Testa a view base da API administrativa do Keycloak."""

    def setUp(self) -> None:
        """Inicializa uma instância da view para os testes."""
        self.view = KeycloakAdminAPIView()

    @patch("apps.keycloak_admin.api.base.tratar_excecao_keycloak")
    def test_handle_exception_trata_erro_do_keycloak(
        self,
        mock_tratar_excecao: Mock,
    ) -> None:
        """Deve encaminhar erros de domínio para o handler do Keycloak."""
        excecao = KeycloakAdminError("Erro administrativo.")
        resposta = Response(
            {"detail": "Erro administrativo."},
            status=400,
        )
        mock_tratar_excecao.return_value = resposta

        resultado = self.view.handle_exception(excecao)

        mock_tratar_excecao.assert_called_once_with(excecao)
        self.assertIs(resultado, resposta)

    @patch.object(APIView, "handle_exception")
    def test_handle_exception_delega_erros_nao_keycloak(
        self,
        mock_handle_exception: Mock,
    ) -> None:
        """Deve delegar exceções não relacionadas ao Keycloak ao DRF."""
        excecao = ValueError("Erro inesperado.")
        resposta = Response(
            {"detail": "Erro interno."},
            status=500,
        )
        mock_handle_exception.return_value = resposta

        resultado = self.view.handle_exception(excecao)

        mock_handle_exception.assert_called_once_with(excecao)
        self.assertIs(resultado, resposta)

    def test_erros_padrao_contem_status_400(self) -> None:
        """Deve documentar a resposta padrão para HTTP 400."""
        resposta = KeycloakAdminAPIView.ERROS_PADRAO[400]

        self.assertEqual(
            resposta.response,
            KeycloakAdminAPIView.ERROS_PADRAO[400].response,
        )
        self.assertEqual(
            resposta.description,
            (
                "Requisição inválida. Pode ocorrer quando o recurso "
                "já existe, não é encontrado ou a operação não é permitida."
            ),
        )

    def test_erros_padrao_contem_status_401(self) -> None:
        """Deve documentar a resposta padrão para HTTP 401."""
        resposta = KeycloakAdminAPIView.ERROS_PADRAO[401]

        self.assertEqual(
            resposta.description,
            "Falha de autenticação com o Keycloak.",
        )

    def test_erros_padrao_contem_status_500(self) -> None:
        """Deve documentar a resposta padrão para HTTP 500."""
        resposta = KeycloakAdminAPIView.ERROS_PADRAO[500]

        self.assertEqual(
            resposta.description,
            "Erro interno ao processar a operação.",
        )
