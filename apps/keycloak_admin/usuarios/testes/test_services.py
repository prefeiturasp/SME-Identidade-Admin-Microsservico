"""Testes dos serviços administrativos de usuários."""

from unittest.mock import Mock

from django.test import SimpleTestCase

from apps.keycloak_admin.exceptions import ErroComunicacaoKeycloakError
from apps.keycloak_admin.usuarios.services import UsuarioService


class UsuarioServiceTestCase(SimpleTestCase):
    """Testa as operações administrativas de usuários."""

    def setUp(self) -> None:
        """Configura o serviço e o cliente Keycloak simulado."""
        self.admin = Mock()
        self.admin.cliente = Mock()

        self.service = UsuarioService(admin=self.admin)

    def test_criar_usuario_com_senha_inicial_por_rf(self) -> None:
        """Deve criar usuário utilizando o RF como senha inicial."""
        self.admin.executar.return_value = "usuario-id"

        resultado = self.service.criar(
            usuario="usuario.teste",
            nome="Usuario Teste",
            email="usuario.teste@example.com",
            cpf="12345678900",
            rf="RF12345",
            sobrenome="Teste",
        )

        self.assertEqual(resultado, "usuario-id")

        self.admin.executar.assert_called_once_with(
            self.admin.cliente.create_user,
            payload={
                "username": "usuario.teste",
                "firstName": "Usuario Teste",
                "lastName": "Teste",
                "email": "usuario.teste@example.com",
                "enabled": True,
                "attributes": {
                    "cpf": ["12345678900"],
                    "rf": ["RF12345"],
                },
                "credentials": [
                    {
                        "type": "password",
                        "value": "RF12345",
                        "temporary": True,
                    }
                ],
            },
        )

    def test_criar_usuario_sem_sobrenome(self) -> None:
        """Deve criar usuário sem sobrenome quando não informado."""
        self.admin.executar.return_value = "usuario-id"

        resultado = self.service.criar(
            usuario="usuario.teste",
            nome="Usuario Teste",
            email="usuario.teste@example.com",
            cpf="12345678900",
            rf="RF12345",
        )

        self.assertEqual(resultado, "usuario-id")

        payload = self.admin.executar.call_args.kwargs["payload"]

        self.assertIsNone(payload["lastName"])
        self.assertEqual(
            payload["credentials"][0]["value"],
            "RF12345",
        )

    def test_criar_usuario_com_senha_inicial_por_cpf(self) -> None:
        """Deve utilizar somente os dígitos do CPF como senha inicial."""
        self.admin.executar.return_value = "usuario-id"

        self.service.criar(
            usuario="usuario.teste",
            nome="Usuario Teste",
            email="usuario.teste@example.com",
            cpf="123.456.789-00",
            rf="",
        )

        payload = self.admin.executar.call_args.kwargs["payload"]

        self.assertEqual(
            payload["credentials"][0]["value"],
            "12345678900",
        )

    def test_criar_usuario_com_senha_inicial_por_username(self) -> None:
        """Deve utilizar o username quando RF e CPF não forem informados."""
        self.admin.executar.return_value = "usuario-id"

        self.service.criar(
            usuario="usuario.teste",
            nome="Usuario Teste",
            email="usuario.teste@example.com",
            cpf="",
            rf="",
        )

        payload = self.admin.executar.call_args.kwargs["payload"]

        self.assertEqual(
            payload["credentials"][0]["value"],
            "usuario.teste",
        )

    def test_consultar_por_id(self) -> None:
        """Deve consultar e normalizar um usuário pelo ID."""
        self.admin.executar.return_value = {
            "id": "usuario-id",
            "username": "usuario.teste",
            "firstName": "Usuario Teste",
            "lastName": "Teste",
            "email": "usuario.teste@example.com",
            "enabled": True,
            "emailVerified": True,
            "attributes": {
                "cpf": ["12345678900"],
                "rf": ["RF12345"],
            },
        }

        resultado = self.service.consultar(
            usuario_id="usuario-id",
        )

        self.assertEqual(
            resultado,
            [
                {
                    "id": "usuario-id",
                    "username": "usuario.teste",
                    "firstName": "Usuario Teste",
                    "lastName": "Teste",
                    "email": "usuario.teste@example.com",
                    "enabled": True,
                    "emailVerified": True,
                    "cpf": "12345678900",
                    "rf": "RF12345",
                }
            ],
        )

        self.admin.executar.assert_called_once_with(
            self.admin.cliente.get_user,
            user_id="usuario-id",
        )

    def test_consultar_por_cpf(self) -> None:
        """Deve consultar usuários pelo CPF."""
        self.admin.executar.return_value = [
            {
                "id": "usuario-id",
                "username": "usuario.teste",
                "attributes": {
                    "cpf": ["12345678900"],
                },
            }
        ]

        resultado = self.service.consultar(
            cpf="12345678900",
        )

        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]["cpf"], "12345678900")

        self.admin.executar.assert_called_once_with(
            self.admin.cliente.get_users,
            query={"q": "cpf:12345678900"},
        )

    def test_consultar_por_rf(self) -> None:
        """Deve consultar usuários pelo registro funcional."""
        self.admin.executar.return_value = [
            {
                "id": "usuario-id",
                "username": "usuario.teste",
                "attributes": {
                    "rf": ["RF12345"],
                },
            }
        ]

        resultado = self.service.consultar(
            rf="RF12345",
        )

        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0]["rf"], "RF12345")

        self.admin.executar.assert_called_once_with(
            self.admin.cliente.get_users,
            query={"q": "rf:RF12345"},
        )

    def test_consultar_por_email(self) -> None:
        """Deve consultar usuários pelo endereço de e-mail."""
        self.admin.executar.return_value = [
            {
                "id": "usuario-id",
                "username": "usuario.teste",
                "email": "usuario.teste@example.com",
            }
        ]

        resultado = self.service.consultar(
            email="usuario.teste@example.com",
        )

        self.assertEqual(len(resultado), 1)
        self.assertEqual(
            resultado[0]["email"],
            "usuario.teste@example.com",
        )

        self.admin.executar.assert_called_once_with(
            self.admin.cliente.get_users,
            query={
                "email": "usuario.teste@example.com",
                "exact": True,
            },
        )

    def test_consultar_geral_sem_busca(self) -> None:
        """Deve consultar usuários sem filtro textual."""
        self.admin.executar.return_value = []

        resultado = self.service.consultar(limite=50)

        self.assertEqual(resultado, [])

        self.admin.executar.assert_called_once_with(
            self.admin.cliente.get_users,
            query={"max": 50},
        )

    def test_consultar_geral_com_busca(self) -> None:
        """Deve consultar usuários utilizando o texto de busca."""
        self.admin.executar.return_value = []

        resultado = self.service.consultar(
            busca="Usuario Teste",
            limite=25,
        )

        self.assertEqual(resultado, [])

        self.admin.executar.assert_called_once_with(
            self.admin.cliente.get_users,
            query={
                "max": 25,
                "search": "Usuario Teste",
            },
        )

    def test_consultar_com_multiplos_criterios(self) -> None:
        """Deve rejeitar mais de um critério de identificação."""
        with self.assertRaises(ValueError):
            self.service.consultar(
                cpf="12345678900",
                rf="RF12345",
            )

        self.admin.executar.assert_not_called()

    def test_atualizar_usuario(self) -> None:
        """Deve atualizar somente os campos informados."""
        self.admin.executar.side_effect = [
            {
                "id": "usuario-id",
                "username": "usuario.teste",
                "firstName": "Usuario",
                "lastName": "Teste",
                "email": "usuario.teste@example.com",
                "enabled": True,
                "attributes": {
                    "cpf": ["11111111111"],
                    "rf": ["RF11111"],
                },
            },
            None,
        ]

        self.service.atualizar(
            usuario_id="usuario-id",
            usuario="novo.usuario",
            nome="Usuario Teste",
            sobrenome="Novo",
            cpf="22222222222",
            rf="RF22222",
            habilitado=False,
        )

        self.assertEqual(self.admin.executar.call_count, 2)

        chamada = self.admin.executar.call_args_list[1]

        self.assertIs(
            chamada.args[0],
            self.admin.cliente.update_user,
        )

        self.assertEqual(
            chamada.kwargs["user_id"],
            "usuario-id",
        )

        self.assertEqual(
            chamada.kwargs["payload"],
            {
                "username": "novo.usuario",
                "firstName": "Usuario Teste",
                "lastName": "Novo",
                "email": "usuario.teste@example.com",
                "enabled": False,
                "attributes": {
                    "cpf": ["22222222222"],
                    "rf": ["RF22222"],
                },
            },
        )

    def test_atualizar_usuario_sem_alteracoes_opcionais(self) -> None:
        """Deve preservar dados atuais quando campos não forem informados."""
        usuario = {
            "id": "usuario-id",
            "username": "usuario.teste",
            "firstName": "Usuario",
            "lastName": "Teste",
            "email": "usuario.teste@example.com",
            "enabled": True,
            "attributes": {
                "cpf": ["12345678900"],
                "rf": ["RF12345"],
            },
        }

        self.admin.executar.side_effect = [usuario, None]

        self.service.atualizar(
            usuario_id="usuario-id",
        )

        payload = self.admin.executar.call_args_list[1].kwargs["payload"]

        self.assertEqual(payload["username"], "usuario.teste")
        self.assertEqual(payload["firstName"], "Usuario")
        self.assertEqual(payload["lastName"], "Teste")
        self.assertEqual(payload["email"], "usuario.teste@example.com")
        self.assertTrue(payload["enabled"])
        self.assertEqual(
            payload["attributes"],
            {
                "cpf": ["12345678900"],
                "rf": ["RF12345"],
            },
        )

    def test_alterar_email_com_sucesso(self) -> None:
        """Deve alterar o e-mail e solicitar sua verificação."""
        self.admin.executar.return_value = None

        resultado = self.service.alterar_email(
            usuario_id="usuario-id",
            email="novo.email@example.com",
        )

        self.assertEqual(
            resultado,
            {
                "email_alterado": True,
                "verificacao_enviada": True,
            },
        )

        self.assertEqual(self.admin.executar.call_count, 2)

        self.assertEqual(
            self.admin.executar.call_args_list[0].kwargs,
            {
                "user_id": "usuario-id",
                "payload": {
                    "email": "novo.email@example.com",
                },
            },
        )

    def test_alterar_email_quando_verificacao_falha(self) -> None:
        """Deve informar falha quando a verificação não puder ser enviada."""
        self.admin.executar.side_effect = [
            None,
            ErroComunicacaoKeycloakError(
                "Falha de comunicação.",
            ),
        ]

        resultado = self.service.alterar_email(
            usuario_id="usuario-id",
            email="novo.email@example.com",
        )

        self.assertEqual(
            resultado,
            {
                "email_alterado": True,
                "verificacao_enviada": False,
            },
        )

        self.assertEqual(self.admin.executar.call_count, 2)

    def test_alterar_senha(self) -> None:
        """Deve alterar a senha com a configuração de temporariedade."""
        self.admin.executar.return_value = None

        self.service.alterar_senha(
            usuario_id="usuario-id",
            senha="SenhaSegura123",
            senha_temporaria=True,
        )

        self.admin.executar.assert_called_once_with(
            self.admin.cliente.set_user_password,
            user_id="usuario-id",
            password="SenhaSegura123",
            temporary=True,
        )

    def test_associar_grupo(self) -> None:
        """Deve associar o usuário ao grupo informado."""
        self.admin.executar.return_value = None

        self.service.associar_grupo(
            usuario_id="usuario-id",
            grupo_id="grupo-id",
        )

        self.admin.executar.assert_called_once_with(
            self.admin.cliente.group_user_add,
            user_id="usuario-id",
            group_id="grupo-id",
        )

    def test_desassociar_grupo(self) -> None:
        """Deve desassociar o usuário do grupo informado."""
        self.admin.executar.return_value = None

        self.service.desassociar_grupo(
            usuario_id="usuario-id",
            grupo_id="grupo-id",
        )

        self.admin.executar.assert_called_once_with(
            self.admin.cliente.group_user_remove,
            user_id="usuario-id",
            group_id="grupo-id",
        )

    def test_associar_role_realm(self) -> None:
        """Deve associar uma Realm Role ao usuário."""
        role = {
            "id": "role-id",
            "name": "role-teste",
        }

        self.admin.executar.side_effect = [
            role,
            None,
        ]

        self.service.associar_role_realm(
            usuario_id="usuario-id",
            nome_permissao="role-teste",
        )

        self.assertEqual(self.admin.executar.call_count, 2)

        self.admin.executar.assert_any_call(
            self.admin.cliente.get_realm_role,
            role_name="role-teste",
        )

        self.admin.executar.assert_any_call(
            self.admin.cliente.assign_realm_roles,
            user_id="usuario-id",
            roles=[role],
        )

    def test_desassociar_role_realm(self) -> None:
        """Deve desassociar uma Realm Role do usuário."""
        role = {
            "id": "role-id",
            "name": "role-teste",
        }

        self.admin.executar.side_effect = [
            role,
            None,
        ]

        self.service.desassociar_role_realm(
            usuario_id="usuario-id",
            nome_permissao="role-teste",
        )

        self.assertEqual(self.admin.executar.call_count, 2)

        self.admin.executar.assert_any_call(
            self.admin.cliente.get_realm_role,
            role_name="role-teste",
        )

        self.admin.executar.assert_any_call(
            self.admin.cliente.delete_realm_roles_of_user,
            user_id="usuario-id",
            roles=[role],
        )

    def test_associar_role_client(self) -> None:
        """Deve associar uma Client Role ao usuário."""
        role = {
            "id": "role-id",
            "name": "role-teste",
        }

        self.admin.executar.side_effect = [
            role,
            None,
        ]

        self.service.associar_role_client(
            usuario_id="usuario-id",
            client_uuid="client-id",
            nome_permissao="role-teste",
        )

        self.assertEqual(self.admin.executar.call_count, 2)

        self.admin.executar.assert_any_call(
            self.admin.cliente.get_client_role,
            client_id="client-id",
            role_name="role-teste",
        )

        self.admin.executar.assert_any_call(
            self.admin.cliente.assign_client_role,
            user_id="usuario-id",
            client_id="client-id",
            roles=[role],
        )

    def test_desassociar_role_client(self) -> None:
        """Deve desassociar uma Client Role do usuário."""
        role = {
            "id": "role-id",
            "name": "role-teste",
        }

        self.admin.executar.side_effect = [
            role,
            None,
        ]

        self.service.desassociar_role_client(
            usuario_id="usuario-id",
            client_uuid="client-id",
            nome_permissao="role-teste",
        )

        self.assertEqual(self.admin.executar.call_count, 2)

        self.admin.executar.assert_any_call(
            self.admin.cliente.get_client_role,
            client_id="client-id",
            role_name="role-teste",
        )

        self.admin.executar.assert_any_call(
            self.admin.cliente.delete_client_roles_of_user,
            user_id="usuario-id",
            client_id="client-id",
            roles=[role],
        )

    def test_normalizar_usuario_com_atributos(self) -> None:
        """Deve normalizar os dados cadastrais e atributos do usuário."""
        usuario = {
            "id": "usuario-id",
            "username": "usuario.teste",
            "firstName": "Usuario Teste",
            "lastName": "Teste",
            "email": "usuario.teste@example.com",
            "enabled": True,
            "emailVerified": True,
            "attributes": {
                "cpf": ["12345678900"],
                "rf": ["RF12345"],
            },
        }

        resultado = UsuarioService._normalizar_usuario(usuario)

        self.assertEqual(
            resultado,
            {
                "id": "usuario-id",
                "username": "usuario.teste",
                "firstName": "Usuario Teste",
                "lastName": "Teste",
                "email": "usuario.teste@example.com",
                "enabled": True,
                "emailVerified": True,
                "cpf": "12345678900",
                "rf": "RF12345",
            },
        )

    def test_normalizar_usuario_sem_atributos_opcionais(self) -> None:
        """Deve aplicar valores padrão para dados ausentes."""
        resultado = UsuarioService._normalizar_usuario({})

        self.assertEqual(
            resultado,
            {
                "id": None,
                "username": None,
                "firstName": None,
                "lastName": None,
                "email": None,
                "enabled": False,
                "emailVerified": False,
                "cpf": None,
                "rf": None,
            },
        )

    def test_obter_atributo_inexistente(self) -> None:
        """Deve retornar None quando o atributo não existir."""
        resultado = UsuarioService._obter_atributo(
            {},
            "cpf",
        )

        self.assertIsNone(resultado)

    def test_obter_atributo_vazio(self) -> None:
        """Deve retornar None quando o atributo estiver vazio."""
        resultado = UsuarioService._obter_atributo(
            {"cpf": []},
            "cpf",
        )

        self.assertIsNone(resultado)

    def test_obter_atributo_com_valor_nao_textual(self) -> None:
        """Deve retornar None quando o primeiro valor não for textual."""
        resultado = UsuarioService._obter_atributo(
            {"cpf": [123456]},
            "cpf",
        )

        self.assertIsNone(resultado)

    def test_resolver_senha_com_rf_com_espacos(self) -> None:
        """Deve remover espaços do RF usado como senha inicial."""
        resultado = UsuarioService._resolver_senha_inicial(
            {
                "username": "usuario.teste",
                "attributes": {
                    "rf": [" RF12345 "],
                },
            }
        )

        self.assertEqual(resultado, "RF12345")

    def test_resolver_senha_com_cpf(self) -> None:
        """Deve remover caracteres não numéricos do CPF."""
        resultado = UsuarioService._resolver_senha_inicial(
            {
                "username": "usuario.teste",
                "attributes": {
                    "cpf": ["123.456.789-00"],
                },
            }
        )

        self.assertEqual(resultado, "12345678900")

    def test_resolver_senha_com_username(self) -> None:
        """Deve utilizar username quando RF e CPF não estiverem disponíveis."""
        resultado = UsuarioService._resolver_senha_inicial(
            {
                "username": "usuario.teste",
                "attributes": {},
            }
        )

        self.assertEqual(resultado, "usuario.teste")

    def test_resolver_senha_com_username_invalido(self) -> None:
        """Deve rejeitar username ausente ao determinar a senha inicial."""
        with self.assertRaises(ValueError):
            UsuarioService._resolver_senha_inicial(
                {
                    "attributes": {},
                }
            )
