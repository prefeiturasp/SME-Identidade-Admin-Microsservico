"""Testes dos serviços administrativos de permissões."""

from unittest.mock import Mock

from django.test import SimpleTestCase

from apps.keycloak_admin.permissoes.services import RoleService


class RoleServiceTest(SimpleTestCase):
    """Testa as operações administrativas de permissões."""

    def setUp(self) -> None:
        """Configura o mock utilizado nos testes."""
        self.admin = Mock()
        self.service = RoleService(admin=self.admin)

    def test_criar_role_realm(self) -> None:
        """Deve criar uma Realm Role com os dados informados."""
        self.service.criar(
            nome="permissao-teste",
            tipo="realm",
            descricao="Descrição da permissão",
            atributos={
                "origem": ["teste"],
            },
        )

        self.admin.executar.assert_called_once_with(
            self.admin.cliente.create_realm_role,
            payload={
                "name": "permissao-teste",
                "description": "Descrição da permissão",
                "attributes": {
                    "origem": ["teste"],
                },
            },
        )

    def test_criar_role_client(self) -> None:
        """Deve criar uma Client Role para o client informado."""
        client_uuid = "client-uuid-teste"

        self.service.criar(
            nome="permissao-teste",
            tipo="client",
            client_uuid=client_uuid,
        )

        self.admin.executar.assert_called_once_with(
            self.admin.cliente.create_client_role,
            client_role_id=client_uuid,
            payload={
                "name": "permissao-teste",
            },
        )

    def test_criar_role_com_apenas_nome(self) -> None:
        """Deve criar uma permissão sem campos opcionais."""
        self.service.criar(
            nome="permissao-teste",
        )

        self.admin.executar.assert_called_once_with(
            self.admin.cliente.create_realm_role,
            payload={
                "name": "permissao-teste",
            },
        )

    def test_criar_role_client_exige_client_uuid(self) -> None:
        """Deve rejeitar Client Role sem client_uuid."""
        with self.assertRaises(ValueError):
            self.service.criar(
                nome="permissao-teste",
                tipo="client",
            )

        self.admin.executar.assert_not_called()

    def test_criar_role_realm_nao_aceita_client_uuid(self) -> None:
        """Deve rejeitar client_uuid para Realm Role."""
        with self.assertRaises(ValueError):
            self.service.criar(
                nome="permissao-teste",
                tipo="realm",
                client_uuid="client-uuid-teste",
            )

        self.admin.executar.assert_not_called()

    def test_criar_role_rejeita_tipo_invalido(self) -> None:
        """Deve rejeitar um tipo de permissão desconhecido."""
        with self.assertRaises(ValueError):
            self.service.criar(
                nome="permissao-teste",
                tipo="invalido",
            )

        self.admin.executar.assert_not_called()

    def test_consultar_role_realm_por_nome(self) -> None:
        """Deve consultar uma Realm Role pelo nome."""
        self.admin.executar.return_value = {
            "id": "role-uuid-teste",
            "name": "permissao-teste",
            "description": "Descrição",
            "composite": False,
            "containerId": "realm-teste",
            "attributes": {},
        }

        resultado = self.service.consultar(
            nome="permissao-teste",
            tipo="realm",
        )

        self.assertEqual(
            resultado,
            [
                {
                    "id": "role-uuid-teste",
                    "nome": "permissao-teste",
                    "descricao": "Descrição",
                    "composite": False,
                    "container_id": "realm-teste",
                    "atributos": {},
                },
            ],
        )

        self.admin.executar.assert_called_once_with(
            self.admin.cliente.get_realm_role,
            role_name="permissao-teste",
        )

    def test_consultar_roles_realm(self) -> None:
        """Deve listar as Realm Roles respeitando o limite."""
        self.admin.executar.return_value = [
            {
                "id": "role-1",
                "name": "permissao-1",
            },
            {
                "id": "role-2",
                "name": "permissao-2",
            },
        ]

        resultado = self.service.consultar(
            tipo="realm",
            limite=10,
        )

        self.assertEqual(
            resultado,
            [
                {
                    "id": "role-1",
                    "nome": "permissao-1",
                    "descricao": None,
                    "composite": False,
                    "container_id": None,
                    "atributos": {},
                },
                {
                    "id": "role-2",
                    "nome": "permissao-2",
                    "descricao": None,
                    "composite": False,
                    "container_id": None,
                    "atributos": {},
                },
            ],
        )

        self.admin.executar.assert_called_once_with(
            self.admin.cliente.get_realm_roles,
            query={
                "max": 10,
            },
        )

    def test_consultar_role_client_por_nome(self) -> None:
        """Deve consultar uma Client Role pelo nome."""
        client_uuid = "client-uuid-teste"

        self.admin.executar.return_value = {
            "id": "role-uuid-teste",
            "name": "permissao-teste",
        }

        resultado = self.service.consultar(
            nome="permissao-teste",
            tipo="client",
            client_uuid=client_uuid,
        )

        self.assertEqual(
            resultado,
            [
                {
                    "id": "role-uuid-teste",
                    "nome": "permissao-teste",
                    "descricao": None,
                    "composite": False,
                    "container_id": None,
                    "atributos": {},
                },
            ],
        )

        self.admin.executar.assert_called_once_with(
            self.admin.cliente.get_client_role,
            client_id=client_uuid,
            role_name="permissao-teste",
        )

    def test_consultar_roles_client(self) -> None:
        """Deve listar as Client Roles respeitando o limite."""
        client_uuid = "client-uuid-teste"

        self.admin.executar.return_value = [
            {
                "id": "role-1",
                "name": "permissao-1",
            },
            {
                "id": "role-2",
                "name": "permissao-2",
            },
            {
                "id": "role-3",
                "name": "permissao-3",
            },
        ]

        resultado = self.service.consultar(
            tipo="client",
            client_uuid=client_uuid,
            limite=2,
        )

        self.assertEqual(
            resultado,
            [
                {
                    "id": "role-1",
                    "nome": "permissao-1",
                    "descricao": None,
                    "composite": False,
                    "container_id": None,
                    "atributos": {},
                },
                {
                    "id": "role-2",
                    "nome": "permissao-2",
                    "descricao": None,
                    "composite": False,
                    "container_id": None,
                    "atributos": {},
                },
            ],
        )

        self.admin.executar.assert_called_once_with(
            self.admin.cliente.get_client_roles,
            client_id=client_uuid,
        )

    def test_consultar_role_client_exige_client_uuid(self) -> None:
        """Deve rejeitar consulta de Client Role sem client_uuid."""
        with self.assertRaises(ValueError):
            self.service.consultar(
                tipo="client",
            )

        self.admin.executar.assert_not_called()

    def test_consultar_role_rejeita_limite_invalido(self) -> None:
        """Deve rejeitar limite menor que um."""
        with self.assertRaises(ValueError):
            self.service.consultar(
                limite=0,
            )

        self.admin.executar.assert_not_called()

    def test_consultar_role_rejeita_tipo_invalido(self) -> None:
        """Deve rejeitar tipo de permissão inválido."""
        with self.assertRaises(ValueError):
            self.service.consultar(
                tipo="invalido",
            )

        self.admin.executar.assert_not_called()

    def test_atualizar_role_realm(self) -> None:
        """Deve atualizar uma Realm Role."""
        self.service.atualizar(
            nome="permissao-atual",
            tipo="realm",
            novo_nome="permissao-nova",
            descricao="Nova descrição",
            atributos={
                "origem": ["teste"],
            },
        )

        self.admin.executar.assert_called_once_with(
            self.admin.cliente.update_realm_role,
            role_name="permissao-atual",
            payload={
                "name": "permissao-nova",
                "description": "Nova descrição",
                "attributes": {
                    "origem": ["teste"],
                },
            },
        )

    def test_atualizar_role_client(self) -> None:
        """Deve atualizar uma Client Role."""
        client_uuid = "client-uuid-teste"

        self.service.atualizar(
            nome="permissao-atual",
            tipo="client",
            client_uuid=client_uuid,
            novo_nome="permissao-nova",
        )

        self.admin.executar.assert_called_once_with(
            self.admin.cliente.update_client_role,
            client_id=client_uuid,
            role_name="permissao-atual",
            payload={
                "name": "permissao-nova",
            },
        )

    def test_atualizar_role_sem_campos(self) -> None:
        """Deve rejeitar atualização sem nenhum campo informado."""
        with self.assertRaises(ValueError):
            self.service.atualizar(
                nome="permissao-teste",
            )

        self.admin.executar.assert_not_called()

    def test_atualizar_role_client_exige_client_uuid(self) -> None:
        """Deve rejeitar atualização de Client Role sem client_uuid."""
        with self.assertRaises(ValueError):
            self.service.atualizar(
                nome="permissao-teste",
                tipo="client",
                novo_nome="permissao-nova",
            )

        self.admin.executar.assert_not_called()

    def test_normalizar_permissao(self) -> None:
        """Deve normalizar os campos retornados pelo Keycloak."""
        resultado = RoleService._normalizar_permissao(
            {
                "id": "role-uuid-teste",
                "name": "permissao-teste",
                "description": "Descrição",
                "composite": True,
                "containerId": "container-teste",
                "attributes": {
                    "origem": ["teste"],
                },
            },
        )

        self.assertEqual(
            resultado,
            {
                "id": "role-uuid-teste",
                "nome": "permissao-teste",
                "descricao": "Descrição",
                "composite": True,
                "container_id": "container-teste",
                "atributos": {
                    "origem": ["teste"],
                },
            },
        )

    def test_validar_limite_aceita_um(self) -> None:
        """Deve aceitar limite igual a um."""
        RoleService._validar_limite(1)

    def test_validar_tipo_aceita_realm_sem_client(self) -> None:
        """Deve aceitar Realm Role sem client_uuid."""
        RoleService._validar_tipo(
            tipo="realm",
            client_uuid=None,
        )

    def test_validar_tipo_aceita_client_com_client_uuid(self) -> None:
        """Deve aceitar Client Role com client_uuid."""
        RoleService._validar_tipo(
            tipo="client",
            client_uuid="client-uuid-teste",
        )
