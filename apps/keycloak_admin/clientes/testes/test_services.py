"""Testes dos serviços administrativos de clientes."""

from unittest.mock import Mock

from django.test import SimpleTestCase

from apps.keycloak_admin.clientes.services import ClientService


class ClientServiceTest(SimpleTestCase):
    """Testes do serviço de administração de clients."""

    def setUp(self) -> None:
        """Prepara o mock do serviço administrativo do Keycloak."""
        self.admin = Mock()
        self.service = ClientService(admin=self.admin)

    def test_criar_client(self) -> None:
        """Deve criar um client e retornar seu ID."""
        self.admin.executar.return_value = "client-uuid"

        resultado = self.service.criar(
            client_id="Sistema Teste",
            nome="Sistema Teste",
            descricao="Descrição do sistema",
        )

        self.assertEqual(resultado, "client-uuid")
        self.admin.executar.assert_called_once()

        chamada = self.admin.executar.call_args
        payload = chamada.kwargs["payload"]

        self.assertEqual(
            payload["clientId"],
            "sistema-teste",
        )
        self.assertEqual(
            payload["name"],
            "Sistema Teste",
        )
        self.assertEqual(
            payload["description"],
            "Descrição do sistema",
        )
        self.assertTrue(payload["enabled"])
        self.assertFalse(payload["publicClient"])
        self.assertEqual(
            payload["protocol"],
            "openid-connect",
        )

    def test_criar_client_com_dados_opcionais(self) -> None:
        """Deve utilizar os dados opcionais informados."""
        self.admin.executar.return_value = "client-uuid"

        self.service.criar(
            client_id="Sistema Teste",
            nome="Sistema Teste",
            descricao="Descrição",
            habilitado=False,
            client_publico=True,
            protocolo="openid-connect",
            redirect_uris=[
                "https://sistema-teste.example.com/callback",
            ],
            web_origins=[
                "https://sistema-teste.example.com",
            ],
            atributos={
                "tipo": "interno",
            },
        )

        payload = self.admin.executar.call_args.kwargs["payload"]

        self.assertFalse(payload["enabled"])
        self.assertTrue(payload["publicClient"])
        self.assertEqual(
            payload["redirectUris"],
            [
                "https://sistema-teste.example.com/callback",
            ],
        )
        self.assertEqual(
            payload["webOrigins"],
            [
                "https://sistema-teste.example.com",
            ],
        )
        self.assertEqual(
            payload["attributes"],
            {
                "tipo": "interno",
            },
        )

    def test_criar_client_normaliza_client_id(self) -> None:
        """Deve normalizar o client_id antes da criação."""
        self.admin.executar.return_value = "client-uuid"

        self.service.criar(
            client_id="Sistema Teste Ágil",
        )

        payload = self.admin.executar.call_args.kwargs["payload"]

        self.assertEqual(
            payload["clientId"],
            "sistema-teste-agil",
        )

    def test_consultar_client_por_uuid(self) -> None:
        """Deve consultar um client específico pelo UUID."""
        self.admin.executar.return_value = {
            "id": "client-uuid",
            "clientId": "sistema-teste",
            "name": "Sistema Teste",
            "enabled": True,
            "publicClient": False,
            "protocol": "openid-connect",
            "redirectUris": [],
            "webOrigins": [],
            "attributes": {},
        }

        resultado = self.service.consultar(
            client_uuid="client-uuid",
        )

        self.assertEqual(
            resultado,
            [
                {
                    "id": "client-uuid",
                    "client_id": "sistema-teste",
                    "nome": "Sistema Teste",
                    "habilitado": True,
                    "client_publico": False,
                    "protocolo": "openid-connect",
                    "redirect_uris": [],
                    "web_origins": [],
                    "atributos": {},
                }
            ],
        )

        self.admin.executar.assert_called_once_with(
            self.admin.cliente.get_client,
            client_id="client-uuid",
        )

    def test_consultar_todos_os_clients(self) -> None:
        """Deve consultar todos os clients quando UUID não for informado."""
        self.admin.executar.return_value = [
            {
                "id": "client-uuid-1",
                "clientId": "sistema-teste-1",
                "name": "Sistema Teste 1",
                "enabled": True,
            },
            {
                "id": "client-uuid-2",
                "clientId": "sistema-teste-2",
                "name": "Sistema Teste 2",
                "enabled": False,
            },
        ]

        resultado = self.service.consultar()

        self.assertEqual(len(resultado), 2)

        self.assertEqual(
            resultado[0]["id"],
            "client-uuid-1",
        )
        self.assertEqual(
            resultado[0]["client_id"],
            "sistema-teste-1",
        )
        self.assertEqual(
            resultado[1]["id"],
            "client-uuid-2",
        )
        self.assertFalse(
            resultado[1]["habilitado"],
        )

        self.admin.executar.assert_called_once_with(
            self.admin.cliente.get_clients,
        )

    def test_atualizar_client(self) -> None:
        """Deve atualizar somente os campos informados."""
        self.service.atualizar(
            client_uuid="client-uuid",
            nome="Sistema Teste Atualizado",
            habilitado=False,
        )

        self.admin.executar.assert_called_once_with(
            self.admin.cliente.update_client,
            client_id="client-uuid",
            payload={
                "name": "Sistema Teste Atualizado",
                "enabled": False,
            },
        )

    def test_atualizar_client_sem_dados_nao_executa_operacao(self) -> None:
        """Não deve chamar o Keycloak quando não houver alterações."""
        self.service.atualizar(
            client_uuid="client-uuid",
        )

        self.admin.executar.assert_not_called()

    def test_normalizar_client(self) -> None:
        """Deve normalizar os dados retornados pelo Keycloak."""
        client = {
            "id": "client-uuid",
            "clientId": "sistema-teste",
            "name": "Sistema Teste",
            "enabled": True,
            "publicClient": False,
            "protocol": "openid-connect",
            "redirectUris": [
                "https://sistema-teste.example.com/callback",
            ],
            "webOrigins": [
                "https://sistema-teste.example.com",
            ],
            "attributes": {
                "tipo": "interno",
            },
        }

        resultado = self.service._normalizar_client(client)

        self.assertEqual(
            resultado,
            {
                "id": "client-uuid",
                "client_id": "sistema-teste",
                "nome": "Sistema Teste",
                "habilitado": True,
                "client_publico": False,
                "protocolo": "openid-connect",
                "redirect_uris": [
                    "https://sistema-teste.example.com/callback",
                ],
                "web_origins": [
                    "https://sistema-teste.example.com",
                ],
                "atributos": {
                    "tipo": "interno",
                },
            },
        )

    def test_slugificar_client_id(self) -> None:
        """Deve gerar um identificador no formato slug."""
        resultado = ClientService._slugificar_client_id(
            "Sistema Teste Ágil",
        )

        self.assertEqual(
            resultado,
            "sistema-teste-agil",
        )

    def test_slugificar_client_id_sem_nome(self) -> None:
        """Deve utilizar valor padrão quando o nome estiver vazio."""
        resultado = ClientService._slugificar_client_id("")

        self.assertEqual(
            resultado,
            "sistema-sem-nome",
        )

    def test_atualizar_client_com_todos_os_campos(self) -> None:
        """Deve atualizar todos os campos opcionais informados."""
        self.service.atualizar(
            client_uuid="client-uuid",
            nome="Sistema Teste",
            descricao="Descrição atualizada",
            habilitado=False,
            client_publico=True,
            protocolo="openid-connect",
            redirect_uris=[
                "https://sistema-teste.example.com/callback",
            ],
            web_origins=[
                "https://sistema-teste.example.com",
            ],
            atributos={
                "tipo": "interno",
            },
        )

        self.admin.executar.assert_called_once_with(
            self.admin.cliente.update_client,
            client_id="client-uuid",
            payload={
                "name": "Sistema Teste",
                "description": "Descrição atualizada",
                "enabled": False,
                "publicClient": True,
                "protocol": "openid-connect",
                "redirectUris": [
                    "https://sistema-teste.example.com/callback",
                ],
                "webOrigins": [
                    "https://sistema-teste.example.com",
                ],
                "attributes": {
                    "tipo": "interno",
                },
            },
        )
