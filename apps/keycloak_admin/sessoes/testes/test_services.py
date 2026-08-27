"""Testes do serviço de administração de sessões."""

from unittest.mock import Mock, patch

from apps.keycloak_admin.sessoes.services import SessaoService


class TestSessaoService:
    """Testes do serviço de sessões."""

    def setup_method(self) -> None:
        """Configura os mocks utilizados nos testes."""
        self.admin = Mock()
        self.cliente = Mock()

        self.admin.cliente = self.cliente

        self.service = SessaoService(
            admin=self.admin,
        )

    def test_inicializa_admin_quando_nao_informado(self) -> None:
        """Deve criar o serviço administrativo quando não informado."""
        with patch(
            "apps.keycloak_admin.sessoes.services.KeycloakAdminService",
        ) as admin_class:
            service = SessaoService()

        admin_class.assert_called_once_with()
        assert service.admin == admin_class.return_value

    def test_consultar_retorna_sessoes_normalizadas(self) -> None:
        """Deve consultar e normalizar as sessões do usuário."""
        sessoes = [
            {
                "id": "sessao-1",
                "userId": "usuario-1",
                "username": "joao",
                "clients": {
                    "client-1": "Sistema 1",
                    "client-2": "Sistema 2",
                },
                "ipAddress": "192.168.0.10",
                "start": 1000,
                "lastAccess": 2000,
            },
            {
                "id": "sessao-2",
                "userId": "usuario-1",
                "username": "joao",
                "clients": {
                    "client-3": "Sistema 3",
                },
                "ipAddress": "192.168.0.20",
                "start": 3000,
                "lastAccess": 4000,
            },
        ]

        self.admin.executar.return_value = sessoes

        resultado = self.service.consultar(
            usuario_id="usuario-1",
        )

        assert resultado == [
            {
                "id": "sessao-1",
                "usuario_id": "usuario-1",
                "usuario": "joao",
                "clientes": {
                    "client-1": "Sistema 1",
                    "client-2": "Sistema 2",
                },
                "endereco_ip": "192.168.0.10",
                "inicio": 1000,
                "ultimo_acesso": 2000,
            },
            {
                "id": "sessao-2",
                "usuario_id": "usuario-1",
                "usuario": "joao",
                "clientes": {
                    "client-3": "Sistema 3",
                },
                "endereco_ip": "192.168.0.20",
                "inicio": 3000,
                "ultimo_acesso": 4000,
            },
        ]

        self.admin.executar.assert_called_once_with(
            self.cliente.get_sessions,
            user_id="usuario-1",
        )

    def test_consultar_usuario_sem_sessoes(self) -> None:
        """Deve retornar lista vazia quando não houver sessões."""
        self.admin.executar.return_value = []

        resultado = self.service.consultar(
            usuario_id="usuario-1",
        )

        assert resultado == []

        self.admin.executar.assert_called_once_with(
            self.cliente.get_sessions,
            user_id="usuario-1",
        )

    def test_consultar_sessao_com_campos_ausentes(self) -> None:
        """Deve aplicar valores padrão aos campos ausentes."""
        self.admin.executar.return_value = [
            {
                "id": "sessao-1",
            },
        ]

        resultado = self.service.consultar(
            usuario_id="usuario-1",
        )

        assert resultado == [
            {
                "id": "sessao-1",
                "usuario_id": None,
                "usuario": None,
                "clientes": [],
                "endereco_ip": None,
                "inicio": None,
                "ultimo_acesso": None,
            },
        ]

    def test_encerrar_sessoes_do_usuario(self) -> None:
        """Deve encerrar todas as sessões do usuário informado."""
        self.service.encerrar(
            usuario_id="usuario-1",
        )

        self.admin.executar.assert_called_once_with(
            self.cliente.user_logout,
            user_id="usuario-1",
        )

    def test_normalizar_sessao(self) -> None:
        """Deve normalizar corretamente os dados de uma sessão."""
        sessao = {
            "id": "sessao-1",
            "userId": "usuario-1",
            "username": "joao",
            "clients": {
                "client-1": "Sistema 1",
            },
            "ipAddress": "10.0.0.1",
            "start": 100,
            "lastAccess": 200,
        }

        resultado = self.service._normalizar_sessao(sessao)

        assert resultado == {
            "id": "sessao-1",
            "usuario_id": "usuario-1",
            "usuario": "joao",
            "clientes": {
                "client-1": "Sistema 1",
            },
            "endereco_ip": "10.0.0.1",
            "inicio": 100,
            "ultimo_acesso": 200,
        }
