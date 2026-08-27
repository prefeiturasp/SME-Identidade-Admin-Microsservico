"""Testes dos serviços administrativos de grupos."""

from unittest.mock import Mock

import pytest

from apps.keycloak_admin.grupos.services import GrupoService


@pytest.fixture
def admin() -> Mock:
    """Cria um mock do serviço administrativo do Keycloak."""
    admin = Mock()
    admin.cliente = Mock()
    return admin


@pytest.fixture
def service(admin: Mock) -> GrupoService:
    """Cria o serviço de grupos utilizando um mock."""
    return GrupoService(admin=admin)


class TestGrupoServiceCriar:
    """Testes da criação de grupos."""

    def test_cria_grupo_com_nome(
        self,
        service: GrupoService,
        admin: Mock,
    ) -> None:
        """Deve criar um grupo com o nome informado."""
        admin.executar.return_value = "grupo-123"

        resultado = service.criar(
            nome="Administradores",
        )

        assert resultado == "grupo-123"

        admin.executar.assert_called_once_with(
            admin.cliente.create_group,
            payload={
                "name": "Administradores",
            },
        )

    def test_cria_grupo_com_caminho_e_atributos(
        self,
        service: GrupoService,
        admin: Mock,
    ) -> None:
        """Deve enviar caminho e atributos quando informados."""
        admin.executar.return_value = "grupo-123"

        resultado = service.criar(
            nome="Administradores",
            caminho="/Sistemas/Administradores",
            atributos={
                "sistema": ["admin"],
            },
        )

        assert resultado == "grupo-123"

        admin.executar.assert_called_once_with(
            admin.cliente.create_group,
            payload={
                "name": "Administradores",
                "path": "/Sistemas/Administradores",
                "attributes": {
                    "sistema": ["admin"],
                },
            },
        )

    def test_rejeita_criacao_sem_id_retornado(
        self,
        service: GrupoService,
        admin: Mock,
    ) -> None:
        """Deve rejeitar criação quando o Keycloak não retorna ID."""
        admin.executar.return_value = None

        with pytest.raises(
            ValueError,
            match="O Keycloak não retornou o ID do grupo criado.",
        ):
            service.criar(
                nome="Administradores",
            )


class TestGrupoServiceConsultar:
    """Testes da consulta de grupos."""

    def test_consulta_por_id(
        self,
        service: GrupoService,
        admin: Mock,
    ) -> None:
        """Deve consultar um grupo pelo ID."""
        admin.executar.return_value = {
            "id": "grupo-123",
            "name": "Administradores",
            "path": "/Administradores",
            "attributes": {
                "sistema": ["admin"],
            },
            "subGroups": [],
        }

        resultado = service.consultar(
            grupo_id="grupo-123",
        )

        assert resultado == [
            {
                "id": "grupo-123",
                "nome": "Administradores",
                "caminho": "/Administradores",
                "atributos": {
                    "sistema": ["admin"],
                },
                "subgrupos": [],
            },
        ]

        admin.executar.assert_called_once_with(
            admin.cliente.get_group,
            group_id="grupo-123",
        )

    def test_consulta_por_nome(
        self,
        service: GrupoService,
        admin: Mock,
    ) -> None:
        """Deve pesquisar grupos pelo nome."""
        admin.executar.return_value = [
            {
                "id": "grupo-123",
                "name": "Administradores",
            },
        ]

        resultado = service.consultar(
            nome="Administradores",
            limite=50,
        )

        assert resultado == [
            {
                "id": "grupo-123",
                "nome": "Administradores",
                "caminho": None,
                "atributos": {},
                "subgrupos": [],
            },
        ]

        admin.executar.assert_called_once_with(
            admin.cliente.get_groups,
            query={
                "max": 50,
                "search": "Administradores",
            },
        )

    def test_consulta_todos_os_grupos(
        self,
        service: GrupoService,
        admin: Mock,
    ) -> None:
        """Deve listar todos os grupos respeitando o limite."""
        admin.executar.return_value = [
            {
                "id": "grupo-123",
                "name": "Administradores",
            },
            {
                "id": "grupo-456",
                "name": "Operadores",
            },
        ]

        resultado = service.consultar(
            limite=100,
        )

        assert len(resultado) == 2

        admin.executar.assert_called_once_with(
            admin.cliente.get_groups,
            query={
                "max": 100,
            },
        )

    def test_rejeita_grupo_id_e_nome_simultaneamente(
        self,
        service: GrupoService,
    ) -> None:
        """Não deve aceitar ID e nome simultaneamente."""
        with pytest.raises(
            ValueError,
            match="Informe apenas um critério de consulta",
        ):
            service.consultar(
                grupo_id="grupo-123",
                nome="Administradores",
            )

    @pytest.mark.parametrize(
        "limite",
        [0, -1],
    )
    def test_rejeita_limite_invalido(
        self,
        service: GrupoService,
        limite: int,
    ) -> None:
        """Não deve aceitar limite menor que um."""
        with pytest.raises(
            ValueError,
            match="limite deve ser maior ou igual a 1",
        ):
            service.consultar(
                limite=limite,
            )


class TestGrupoServiceAtualizar:
    """Testes da atualização de grupos."""

    def test_atualiza_nome(
        self,
        service: GrupoService,
        admin: Mock,
    ) -> None:
        """Deve atualizar o nome do grupo."""
        service.atualizar(
            grupo_id="grupo-123",
            nome="Administradores",
        )

        admin.executar.assert_called_once_with(
            admin.cliente.update_group,
            group_id="grupo-123",
            payload={
                "name": "Administradores",
            },
        )

    def test_atualiza_todos_os_campos(
        self,
        service: GrupoService,
        admin: Mock,
    ) -> None:
        """Deve atualizar nome, caminho e atributos."""
        service.atualizar(
            grupo_id="grupo-123",
            nome="Administradores",
            caminho="/Sistemas/Administradores",
            atributos={
                "sistema": ["admin"],
            },
        )

        admin.executar.assert_called_once_with(
            admin.cliente.update_group,
            group_id="grupo-123",
            payload={
                "name": "Administradores",
                "path": "/Sistemas/Administradores",
                "attributes": {
                    "sistema": ["admin"],
                },
            },
        )

    def test_rejeita_atualizacao_sem_campos(
        self,
        service: GrupoService,
    ) -> None:
        """Deve rejeitar atualização sem campos."""
        with pytest.raises(
            ValueError,
            match="Informe ao menos um campo para atualização.",
        ):
            service.atualizar(
                grupo_id="grupo-123",
            )


class TestGrupoServiceRoles:
    """Testes das operações de roles dos grupos."""

    def test_associa_realm_role(
        self,
        service: GrupoService,
        admin: Mock,
    ) -> None:
        """Deve associar uma Realm Role ao grupo."""
        role = {
            "id": "role-123",
            "name": "administrador",
        }

        admin.executar.return_value = role

        service.associar_role_realm(
            grupo_id="grupo-123",
            nome_role="administrador",
        )

        assert admin.executar.call_count == 2

        admin.executar.assert_any_call(
            admin.cliente.get_realm_role,
            role_name="administrador",
        )

        admin.executar.assert_any_call(
            admin.cliente.assign_group_realm_roles,
            group_id="grupo-123",
            roles=[role],
        )

    def test_desassocia_realm_role(
        self,
        service: GrupoService,
        admin: Mock,
    ) -> None:
        """Deve desassociar uma Realm Role do grupo."""
        role = {
            "id": "role-123",
            "name": "administrador",
        }

        admin.executar.return_value = role

        service.desassociar_role_realm(
            grupo_id="grupo-123",
            nome_role="administrador",
        )

        assert admin.executar.call_count == 2

        admin.executar.assert_any_call(
            admin.cliente.get_realm_role,
            role_name="administrador",
        )

        admin.executar.assert_any_call(
            admin.cliente.delete_group_realm_roles,
            group_id="grupo-123",
            roles=[role],
        )

    def test_associa_client_role(
        self,
        service: GrupoService,
        admin: Mock,
    ) -> None:
        """Deve associar uma Client Role ao grupo."""
        role = {
            "id": "role-123",
            "name": "administrador",
        }

        admin.executar.return_value = role

        service.associar_role_client(
            grupo_id="grupo-123",
            client_uuid="client-123",
            nome_role="administrador",
        )

        assert admin.executar.call_count == 2

        admin.executar.assert_any_call(
            admin.cliente.get_client_role,
            client_id="client-123",
            role_name="administrador",
        )

        admin.executar.assert_any_call(
            admin.cliente.assign_group_client_roles,
            group_id="grupo-123",
            client_id="client-123",
            roles=[role],
        )

    def test_desassocia_client_role(
        self,
        service: GrupoService,
        admin: Mock,
    ) -> None:
        """Deve desassociar uma Client Role do grupo."""
        role = {
            "id": "role-123",
            "name": "administrador",
        }

        admin.executar.return_value = role

        service.desassociar_role_client(
            grupo_id="grupo-123",
            client_uuid="client-123",
            nome_role="administrador",
        )

        assert admin.executar.call_count == 2

        admin.executar.assert_any_call(
            admin.cliente.get_client_role,
            client_id="client-123",
            role_name="administrador",
        )

        admin.executar.assert_any_call(
            admin.cliente.delete_group_client_roles,
            group_id="grupo-123",
            client_id="client-123",
            roles=[role],
        )


class TestGrupoServiceNormalizacao:
    """Testes da normalização de grupos."""

    def test_normaliza_grupo_completo(self) -> None:
        """Deve normalizar todos os campos do grupo."""
        grupo = {
            "id": "grupo-123",
            "name": "Administradores",
            "path": "/Administradores",
            "attributes": {
                "sistema": ["admin"],
            },
            "subGroups": [
                {
                    "id": "grupo-456",
                    "name": "Operadores",
                },
            ],
        }

        resultado = GrupoService._normalizar_grupo(grupo)

        assert resultado == {
            "id": "grupo-123",
            "nome": "Administradores",
            "caminho": "/Administradores",
            "atributos": {
                "sistema": ["admin"],
            },
            "subgrupos": [
                {
                    "id": "grupo-456",
                    "name": "Operadores",
                },
            ],
        }

    def test_normaliza_grupo_sem_campos_opcionais(self) -> None:
        """Deve aplicar valores padrão aos campos ausentes."""
        resultado = GrupoService._normalizar_grupo(
            {
                "id": "grupo-123",
                "name": "Administradores",
            },
        )

        assert resultado == {
            "id": "grupo-123",
            "nome": "Administradores",
            "caminho": None,
            "atributos": {},
            "subgrupos": [],
        }
