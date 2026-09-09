"""Testes dos serializers administrativos de clientes."""

from django.test import SimpleTestCase

from apps.keycloak_admin.clientes.api.serializers import (
    ClientAtualizarSerializer,
    ClientConsultaSerializer,
    ClientCriadoSerializer,
    ClientCriarSerializer,
    ClientSerializer,
)


class ClientCriarSerializerTest(SimpleTestCase):
    """Testes do serializer de criação de clients."""

    def test_dados_validos(self) -> None:
        """Deve aceitar os dados mínimos necessários."""
        serializer = ClientCriarSerializer(
            data={
                "client_id": "sistema-teste",
            },
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_valores_padrao(self) -> None:
        """Deve aplicar os valores padrão da criação."""
        serializer = ClientCriarSerializer(
            data={
                "client_id": "sistema-teste",
            },
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        self.assertTrue(
            serializer.validated_data["habilitado"],
        )
        self.assertFalse(
            serializer.validated_data["client_publico"],
        )
        self.assertEqual(
            serializer.validated_data["protocolo"],
            "openid-connect",
        )
        self.assertEqual(
            serializer.validated_data["redirect_uris"],
            [],
        )
        self.assertEqual(
            serializer.validated_data["web_origins"],
            [],
        )
        self.assertEqual(
            serializer.validated_data["atributos"],
            {},
        )

    def test_client_id_obrigatorio(self) -> None:
        """Deve rejeitar a criação sem client_id."""
        serializer = ClientCriarSerializer(
            data={},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn(
            "client_id",
            serializer.errors,
        )

    def test_email_nao_e_aceito_como_redirect_uri_invalida(self) -> None:
        """Deve rejeitar uma redirect URI que não seja uma URL válida."""
        serializer = ClientCriarSerializer(
            data={
                "client_id": "sistema-teste",
                "redirect_uris": [
                    "nao-e-uma-url",
                ],
            },
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn(
            "redirect_uris",
            serializer.errors,
        )


class ClientConsultaSerializerTest(SimpleTestCase):
    """Testes do serializer de consulta de clients."""

    def test_consulta_sem_uuid(self) -> None:
        """Deve permitir consulta de todos os clients."""
        serializer = ClientConsultaSerializer(
            data={},
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_consulta_com_uuid(self) -> None:
        """Deve aceitar um UUID válido."""
        serializer = ClientConsultaSerializer(
            data={
                "client_uuid": "12345678-1234-5678-1234-567812345678",
            },
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_consulta_com_uuid_invalido(self) -> None:
        """Deve rejeitar um UUID inválido."""
        serializer = ClientConsultaSerializer(
            data={
                "client_uuid": "client-invalido",
            },
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn(
            "client_uuid",
            serializer.errors,
        )


class ClientAtualizarSerializerTest(SimpleTestCase):
    """Testes do serializer de atualização de clients."""

    def test_dados_opcionais(self) -> None:
        """Deve aceitar atualização parcial."""
        serializer = ClientAtualizarSerializer(
            data={
                "nome": "Sistema Teste",
                "habilitado": False,
            },
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

        self.assertEqual(
            serializer.validated_data["nome"],
            "Sistema Teste",
        )
        self.assertFalse(
            serializer.validated_data["habilitado"],
        )

    def test_sem_dados(self) -> None:
        """Deve aceitar uma requisição sem campos de atualização."""
        serializer = ClientAtualizarSerializer(
            data={},
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_client_id_com_tamanho_excedido(self) -> None:
        """Deve rejeitar client_id acima do tamanho permitido."""
        serializer = ClientAtualizarSerializer(
            data={
                "client_id": "a" * 256,
            },
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn(
            "client_id",
            serializer.errors,
        )


class ClientSerializerTest(SimpleTestCase):
    """Testes do serializer de resposta de clients."""

    def test_dados_validos(self) -> None:
        """Deve serializar os dados de um client."""
        dados = {
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

        serializer = ClientSerializer(data=dados)

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )


class ClientCriadoSerializerTest(SimpleTestCase):
    """Testes do serializer de resposta da criação."""

    def test_id_valido(self) -> None:
        """Deve aceitar o ID do client criado."""
        serializer = ClientCriadoSerializer(
            data={
                "id": "client-uuid",
            },
        )

        self.assertTrue(
            serializer.is_valid(),
            serializer.errors,
        )

    def test_id_obrigatorio(self) -> None:
        """Deve exigir o ID do client criado."""
        serializer = ClientCriadoSerializer(
            data={},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn(
            "id",
            serializer.errors,
        )
