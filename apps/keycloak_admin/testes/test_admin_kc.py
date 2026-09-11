"""Testes do serviço base de administração do Keycloak."""

from unittest.mock import Mock, patch

from django.conf import settings
from django.test import SimpleTestCase
from keycloak.exceptions import (
    KeycloakDeleteError,
    KeycloakGetError,
    KeycloakPostError,
    KeycloakPutError,
)

from apps.keycloak_admin.admin_kc import KeycloakAdminService
from apps.keycloak_admin.exceptions import (
    ErroAutenticacaoKeycloakError,
    ErroComunicacaoKeycloakError,
    ErroRequisicaoKeycloakError,
    OperacaoNaoPermitidaError,
    RecursoJaExisteError,
    RecursoNaoEncontradoError,
)


class KeycloakAdminServiceTestCase(SimpleTestCase):
    """Testa o serviço base de administração do Keycloak."""

    @patch("apps.keycloak_admin.admin_kc.KeycloakAdmin")
    def test_inicializa_com_realm_informado(
        self,
        mock_keycloak_admin: Mock,
    ) -> None:
        """Deve criar o cliente utilizando o realm informado."""
        realm = "CASARAO"

        service = KeycloakAdminService(realm=realm)

        self.assertEqual(service.realm, realm)
        mock_keycloak_admin.assert_called_once_with(
            server_url=settings.KEYCLOAK_URL_SERVIDOR,
            username=settings.KEYCLOAK_USUARIO_ADMIN,
            password=settings.KEYCLOAK_SENHA_ADMIN,
            realm_name=realm,
            user_realm_name="master",
            verify=settings.KEYCLOAK_VERIFICAR_SSL,
        )
        self.assertIs(service.cliente, mock_keycloak_admin.return_value)

    @patch("apps.keycloak_admin.admin_kc.KeycloakAdmin")
    def test_inicializa_com_realm_padrao(
        self,
        mock_keycloak_admin: Mock,
    ) -> None:
        """Deve utilizar o realm padrão quando nenhum realm for informado."""
        service = KeycloakAdminService()

        self.assertEqual(service.realm, settings.KEYCLOAK_REALM)
        mock_keycloak_admin.assert_called_once_with(
            server_url=settings.KEYCLOAK_URL_SERVIDOR,
            username=settings.KEYCLOAK_USUARIO_ADMIN,
            password=settings.KEYCLOAK_SENHA_ADMIN,
            realm_name=settings.KEYCLOAK_REALM,
            user_realm_name="master",
            verify=settings.KEYCLOAK_VERIFICAR_SSL,
        )

    @patch("apps.keycloak_admin.admin_kc.KeycloakAdmin")
    def test_criar_cliente_retorna_cliente_keycloak(
        self,
        mock_keycloak_admin: Mock,
    ) -> None:
        """Deve retornar a instância criada do cliente Keycloak."""
        service = KeycloakAdminService.__new__(KeycloakAdminService)
        service.realm = "CASARAO"

        cliente = service._criar_cliente()

        self.assertIs(cliente, mock_keycloak_admin.return_value)

    @patch("apps.keycloak_admin.admin_kc.KeycloakAdmin")
    def test_executar_retorna_resultado_da_operacao(
        self,
        mock_keycloak_admin: Mock,
    ) -> None:
        """Deve retornar o resultado produzido pela operação."""
        service = KeycloakAdminService()
        operacao = Mock(return_value={"id": "123"})

        resultado = service.executar(
            operacao,
            "argumento",
            parametro="valor",
        )

        self.assertEqual(resultado, {"id": "123"})
        operacao.assert_called_once_with(
            "argumento",
            parametro="valor",
        )

    @patch("apps.keycloak_admin.admin_kc.KeycloakAdmin")
    def test_executar_traduz_erro_401(
        self,
        mock_keycloak_admin: Mock,
    ) -> None:
        """Deve traduzir HTTP 401 para erro de autenticação."""
        service = KeycloakAdminService()
        operacao = Mock(
            side_effect=KeycloakGetError(response_code=401),
        )

        with self.assertRaises(ErroAutenticacaoKeycloakError):
            service.executar(operacao)

    @patch("apps.keycloak_admin.admin_kc.KeycloakAdmin")
    def test_executar_traduz_erro_403(
        self,
        mock_keycloak_admin: Mock,
    ) -> None:
        """Deve traduzir HTTP 403 para operação não permitida."""
        service = KeycloakAdminService()
        operacao = Mock(
            side_effect=KeycloakPostError(response_code=403),
        )

        with self.assertRaises(OperacaoNaoPermitidaError):
            service.executar(operacao)

    @patch("apps.keycloak_admin.admin_kc.KeycloakAdmin")
    def test_executar_traduz_erro_404(
        self,
        mock_keycloak_admin: Mock,
    ) -> None:
        """Deve traduzir HTTP 404 para recurso não encontrado."""
        service = KeycloakAdminService()
        operacao = Mock(
            side_effect=KeycloakGetError(response_code=404),
        )

        with self.assertRaises(RecursoNaoEncontradoError):
            service.executar(operacao)

    @patch("apps.keycloak_admin.admin_kc.KeycloakAdmin")
    def test_executar_traduz_erro_409(
        self,
        mock_keycloak_admin: Mock,
    ) -> None:
        """Deve traduzir HTTP 409 para recurso já existente."""
        service = KeycloakAdminService()
        operacao = Mock(
            side_effect=KeycloakPostError(response_code=409),
        )

        with self.assertRaises(RecursoJaExisteError):
            service.executar(operacao)

    @patch("apps.keycloak_admin.admin_kc.KeycloakAdmin")
    def test_executar_traduz_erro_400(
        self,
        mock_keycloak_admin: Mock,
    ) -> None:
        """Deve traduzir HTTP 400 para erro de requisição."""
        service = KeycloakAdminService()
        operacao = Mock(
            side_effect=KeycloakPutError(response_code=400),
        )

        with self.assertRaises(ErroRequisicaoKeycloakError):
            service.executar(operacao)

    @patch("apps.keycloak_admin.admin_kc.KeycloakAdmin")
    def test_executar_traduz_erro_422(
        self,
        mock_keycloak_admin: Mock,
    ) -> None:
        """Deve traduzir HTTP 422 para erro de requisição."""
        service = KeycloakAdminService()
        operacao = Mock(
            side_effect=KeycloakPutError(response_code=422),
        )

        with self.assertRaises(ErroRequisicaoKeycloakError):
            service.executar(operacao)

    @patch("apps.keycloak_admin.admin_kc.KeycloakAdmin")
    def test_executar_traduz_erro_nao_mapeado(
        self,
        mock_keycloak_admin: Mock,
    ) -> None:
        """Deve traduzir códigos HTTP não mapeados para erro de comunicação."""
        service = KeycloakAdminService()
        operacao = Mock(
            side_effect=KeycloakDeleteError(response_code=500),
        )

        with self.assertRaises(ErroComunicacaoKeycloakError):
            service.executar(operacao)

    @patch("apps.keycloak_admin.admin_kc.KeycloakAdmin")
    def test_traduzir_excecao_preserva_causa_original(
        self,
        mock_keycloak_admin: Mock,
    ) -> None:
        """Deve preservar a exceção original como causa do erro de domínio."""
        service = KeycloakAdminService()
        excecao_original = KeycloakGetError(response_code=401)

        with self.assertRaises(ErroAutenticacaoKeycloakError) as contexto:
            service.executar(Mock(side_effect=excecao_original))

        self.assertIs(contexto.exception.__cause__, excecao_original)
