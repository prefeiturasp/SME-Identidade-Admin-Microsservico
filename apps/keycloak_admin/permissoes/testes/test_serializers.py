"""Testes dos serializers administrativos de permissões."""

from rest_framework.test import APISimpleTestCase

from apps.keycloak_admin.permissoes.api.serializers import (
    RoleAtualizarSerializer,
    RoleConsultaSerializer,
    RoleCriarSerializer,
    RoleSerializer,
)


class RoleCriarSerializerTest(APISimpleTestCase):
    """Testes do serializer de criação de permissões."""

    def test_valida_dados_obrigatorios(self) -> None:
        """Deve validar uma permissão com apenas os dados obrigatórios."""
        serializer = RoleCriarSerializer(
            data={
                "nome": "Permissao Teste",
            },
        )

        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            serializer.validated_data["nome"],
            "Permissao Teste",
        )

    def test_valida_dados_completos(self) -> None:
        """Deve validar todos os campos disponíveis."""
        dados = {
            "nome": "Permissao Teste",
            "descricao": "Descricao da permissao.",
            "atributos": {
                "origem": "teste",
            },
        }

        serializer = RoleCriarSerializer(data=dados)

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data, dados)

    def test_rejeita_nome_ausente(self) -> None:
        """Deve rejeitar a criação sem nome."""
        serializer = RoleCriarSerializer(data={})

        self.assertFalse(serializer.is_valid())
        self.assertIn("nome", serializer.errors)

    def test_rejeita_nome_maior_que_o_limite(self) -> None:
        """Deve rejeitar nome com mais de 255 caracteres."""
        serializer = RoleCriarSerializer(
            data={
                "nome": "A" * 256,
            },
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("nome", serializer.errors)

    def test_permite_descricao_vazia(self) -> None:
        """Deve aceitar descrição vazia."""
        serializer = RoleCriarSerializer(
            data={
                "nome": "Permissao Teste",
                "descricao": "",
            },
        )

        self.assertTrue(serializer.is_valid())

    def test_rejeita_atributos_com_formato_invalido(self) -> None:
        """Deve rejeitar atributos que não sejam um objeto."""
        serializer = RoleCriarSerializer(
            data={
                "nome": "Permissao Teste",
                "atributos": "invalido",
            },
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("atributos", serializer.errors)


class RoleConsultaSerializerTest(APISimpleTestCase):
    """Testes do serializer de consulta de permissões."""

    def test_valida_consulta_sem_filtros(self) -> None:
        """Deve validar consulta sem nome."""
        serializer = RoleConsultaSerializer(data={})

        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            serializer.validated_data["limite"],
            100,
        )

    def test_valida_consulta_por_nome(self) -> None:
        """Deve validar consulta por nome."""
        serializer = RoleConsultaSerializer(
            data={
                "nome": "Permissao Teste",
            },
        )

        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            serializer.validated_data["nome"],
            "Permissao Teste",
        )

    def test_aplica_limite_informado(self) -> None:
        """Deve aceitar limite dentro do intervalo permitido."""
        serializer = RoleConsultaSerializer(
            data={
                "limite": 500,
            },
        )

        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            serializer.validated_data["limite"],
            500,
        )

    def test_rejeita_limite_menor_que_um(self) -> None:
        """Deve rejeitar limite menor que 1."""
        serializer = RoleConsultaSerializer(
            data={
                "limite": 0,
            },
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("limite", serializer.errors)

    def test_rejeita_limite_maior_que_mil(self) -> None:
        """Deve rejeitar limite maior que 1000."""
        serializer = RoleConsultaSerializer(
            data={
                "limite": 1001,
            },
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("limite", serializer.errors)


class RoleAtualizarSerializerTest(APISimpleTestCase):
    """Testes do serializer de atualização de permissões."""

    def test_valida_novo_nome(self) -> None:
        """Deve validar atualização somente do nome."""
        serializer = RoleAtualizarSerializer(
            data={
                "novo_nome": "Nova Permissao",
            },
        )

        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            serializer.validated_data["novo_nome"],
            "Nova Permissao",
        )

    def test_valida_descricao(self) -> None:
        """Deve validar atualização da descrição."""
        serializer = RoleAtualizarSerializer(
            data={
                "descricao": "Nova descricao.",
            },
        )

        self.assertTrue(serializer.is_valid())

    def test_valida_atributos(self) -> None:
        """Deve validar atualização dos atributos."""
        serializer = RoleAtualizarSerializer(
            data={
                "atributos": {
                    "origem": "teste",
                },
            },
        )

        self.assertTrue(serializer.is_valid())

    def test_valida_multiplos_campos(self) -> None:
        """Deve validar atualização com múltiplos campos."""
        serializer = RoleAtualizarSerializer(
            data={
                "novo_nome": "Nova Permissao",
                "descricao": "Nova descricao.",
                "atributos": {
                    "origem": "teste",
                },
            },
        )

        self.assertTrue(serializer.is_valid())

    def test_rejeita_dados_vazios(self) -> None:
        """Deve rejeitar atualização sem nenhum campo."""
        serializer = RoleAtualizarSerializer(data={})

        self.assertFalse(serializer.is_valid())
        self.assertIn(
            "non_field_errors",
            serializer.errors,
        )

    def test_rejeita_novo_nome_maior_que_o_limite(self) -> None:
        """Deve rejeitar novo nome com mais de 255 caracteres."""
        serializer = RoleAtualizarSerializer(
            data={
                "novo_nome": "A" * 256,
            },
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("novo_nome", serializer.errors)


class RoleSerializerTest(APISimpleTestCase):
    """Testes do serializer de resposta de permissões."""

    def test_serializa_permissao(self) -> None:
        """Deve serializar uma permissão corretamente."""
        dados = {
            "id": "role-id",
            "nome": "Permissao Teste",
            "descricao": "Descricao da permissao.",
            "composite": False,
            "container_id": "container-id",
            "atributos": {
                "origem": "teste",
            },
        }

        serializer = RoleSerializer(instance=dados)

        self.assertEqual(serializer.data, dados)

    def test_aceita_valores_nulos(self) -> None:
        """Deve aceitar valores nulos nos campos configurados."""
        dados: dict[str, object] = {
            "id": None,
            "nome": None,
            "descricao": None,
            "composite": False,
            "container_id": None,
            "atributos": {},
        }

        serializer = RoleSerializer(instance=dados)

        self.assertEqual(serializer.data, dados)
