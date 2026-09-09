"""Testes dos serializers administrativos de grupos."""

from typing import Any

import pytest

from apps.keycloak_admin.grupos.api.serializers import (
    GrupoAtualizarSerializer,
    GrupoClientRoleSerializer,
    GrupoConsultaSerializer,
    GrupoCriarSerializer,
    GrupoRoleSerializer,
    GrupoSerializer,
)


class TestGrupoSerializer:
    """Testes do serializer de resposta de grupos."""

    def test_valida_grupo_completo(self) -> None:
        """Deve validar um grupo completo."""
        dados: dict[str, Any] = {
            "id": "grupo-123",
            "nome": "OPERADORES",
            "caminho": "/OPERADORES",
            "atributos": {
                "sistema": ["admin"],
            },
            "subgrupos": [
                {
                    "id": "subgrupo-123",
                    "name": "LEITURA",
                },
            ],
        }

        serializer = GrupoSerializer(data=dados)

        assert serializer.is_valid(), serializer.errors

        assert serializer.validated_data == {
            "nome": "OPERADORES",
            "caminho": "/OPERADORES",
            "atributos": {
                "sistema": ["admin"],
            },
            "subgrupos": [
                {
                    "id": "subgrupo-123",
                    "name": "LEITURA",
                },
            ],
        }

    def test_valida_grupo_sem_campos_opcionais(self) -> None:
        """Deve validar um grupo sem caminho, atributos e subgrupos."""
        dados: dict[str, Any] = {
            "id": "grupo-123",
            "nome": "Administradores",
        }

        serializer = GrupoSerializer(data=dados)

        assert serializer.is_valid(), serializer.errors

    def test_id_e_somente_leitura(self) -> None:
        """Não deve aceitar alteração do ID."""
        dados: dict[str, Any] = {
            "id": "grupo-123",
            "nome": "Administradores",
        }

        serializer = GrupoSerializer(data=dados)

        assert serializer.is_valid(), serializer.errors
        assert "id" not in serializer.validated_data


class TestGrupoCriarSerializer:
    """Testes do serializer de criação de grupos."""

    def test_valida_dados_obrigatorios(self) -> None:
        """Deve validar os dados obrigatórios."""
        dados: dict[str, Any] = {
            "nome": "Administradores",
        }

        serializer = GrupoCriarSerializer(data=dados)

        assert serializer.is_valid(), serializer.errors

    def test_valida_todos_os_campos(self) -> None:
        """Deve validar todos os campos de criação."""
        dados: dict[str, Any] = {
            "nome": "Administradores",
            "caminho": "/Sistemas/Administradores",
            "atributos": {
                "sistema": ["admin"],
            },
        }

        serializer = GrupoCriarSerializer(data=dados)

        assert serializer.is_valid(), serializer.errors

    def test_rejeita_nome_ausente(self) -> None:
        """Deve rejeitar criação sem nome."""
        serializer = GrupoCriarSerializer(data={})

        assert not serializer.is_valid()
        assert "nome" in serializer.errors

    def test_aceita_caminho_nulo(self) -> None:
        """Deve aceitar caminho nulo."""
        serializer = GrupoCriarSerializer(
            data={
                "nome": "Administradores",
                "caminho": None,
            },
        )

        assert serializer.is_valid(), serializer.errors

    def test_aceita_atributos_nulos(self) -> None:
        """Deve aceitar atributos nulos."""
        serializer = GrupoCriarSerializer(
            data={
                "nome": "Administradores",
                "atributos": None,
            },
        )

        assert serializer.is_valid(), serializer.errors


class TestGrupoConsultaSerializer:
    """Testes do serializer de consulta de grupos."""

    def test_consulta_sem_filtros(self) -> None:
        """Deve aceitar consulta sem filtros."""
        serializer = GrupoConsultaSerializer(data={})

        assert serializer.is_valid(), serializer.errors
        assert serializer.validated_data["limite"] == 100

    def test_consulta_por_grupo_id(self) -> None:
        """Deve aceitar consulta por ID."""
        serializer = GrupoConsultaSerializer(
            data={
                "grupo_id": "grupo-123",
            },
        )

        assert serializer.is_valid(), serializer.errors

    def test_consulta_por_nome(self) -> None:
        """Deve aceitar consulta por nome."""
        serializer = GrupoConsultaSerializer(
            data={
                "nome": "Administradores",
            },
        )

        assert serializer.is_valid(), serializer.errors

    def test_rejeita_grupo_id_e_nome(self) -> None:
        """Não deve aceitar ID e nome simultaneamente."""
        serializer = GrupoConsultaSerializer(
            data={
                "grupo_id": "grupo-123",
                "nome": "Administradores",
            },
        )

        assert not serializer.is_valid()

        assert "Informe apenas um critério de consulta" in str(
            serializer.errors
        )

    @pytest.mark.parametrize(
        "limite",
        [0, -1],
    )
    def test_rejeita_limite_menor_que_um(
        self,
        limite: int,
    ) -> None:
        """Não deve aceitar limite menor que um."""
        serializer = GrupoConsultaSerializer(
            data={
                "limite": limite,
            },
        )

        assert not serializer.is_valid()
        assert "limite" in serializer.errors

    def test_rejeita_limite_maior_que_mil(self) -> None:
        """Não deve aceitar limite superior a 1000."""
        serializer = GrupoConsultaSerializer(
            data={
                "limite": 1001,
            },
        )

        assert not serializer.is_valid()
        assert "limite" in serializer.errors

    def test_aceita_limite_maximo(self) -> None:
        """Deve aceitar limite igual a 1000."""
        serializer = GrupoConsultaSerializer(
            data={
                "limite": 1000,
            },
        )

        assert serializer.is_valid(), serializer.errors


class TestGrupoAtualizarSerializer:
    """Testes do serializer de atualização de grupos."""

    @pytest.mark.parametrize(
        "dados",
        [
            {"nome": "Administradores"},
            {"caminho": "/Administradores"},
            {"caminho": None},
            {"atributos": {"sistema": ["admin"]}},
            {"atributos": None},
        ],
    )
    def test_aceita_atualizacao_com_campo(
        self,
        dados: dict[str, Any],
    ) -> None:
        """Deve aceitar atualização com pelo menos um campo."""
        serializer = GrupoAtualizarSerializer(data=dados)

        assert serializer.is_valid(), serializer.errors

    def test_aceita_todos_os_campos(self) -> None:
        """Deve aceitar atualização com todos os campos."""
        serializer = GrupoAtualizarSerializer(
            data={
                "nome": "Administradores",
                "caminho": "/Administradores",
                "atributos": {
                    "sistema": ["admin"],
                },
            },
        )

        assert serializer.is_valid(), serializer.errors

    def test_rejeita_dados_vazios(self) -> None:
        """Não deve aceitar atualização sem campos."""
        serializer = GrupoAtualizarSerializer(data={})

        assert not serializer.is_valid()

        assert "Informe ao menos um campo para atualização." in str(
            serializer.errors
        )


class TestGrupoRoleSerializer:
    """Testes do serializer de Realm Role."""

    def test_valida_nome_da_permissao(self) -> None:
        """Deve validar o nome da permissão."""
        serializer = GrupoRoleSerializer(
            data={
                "nome_permissao": "administrador",
            },
        )

        assert serializer.is_valid(), serializer.errors

    def test_rejeita_nome_da_permissao_ausente(self) -> None:
        """Deve rejeitar ausência do nome da permissão."""
        serializer = GrupoRoleSerializer(data={})

        assert not serializer.is_valid()
        assert "nome_permissao" in serializer.errors


class TestGrupoClientRoleSerializer:
    """Testes do serializer de Client Role."""

    def test_valida_nome_da_permissao(self) -> None:
        """Deve validar o nome da Client Role."""
        serializer = GrupoClientRoleSerializer(
            data={
                "nome_permissao": "administrador",
            },
        )

        assert serializer.is_valid(), serializer.errors

    def test_rejeita_nome_da_permissao_ausente(self) -> None:
        """Deve rejeitar ausência do nome da Client Role."""
        serializer = GrupoClientRoleSerializer(data={})

        assert not serializer.is_valid()
        assert "nome_permissao" in serializer.errors
