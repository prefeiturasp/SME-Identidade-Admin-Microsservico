"""Testes dos serializers administrativos de realms."""

from django.test import SimpleTestCase, override_settings

from apps.keycloak_admin.realms.api.serializers import (
    RealmAtualizarSerializer,
    RealmCriarSerializer,
)


class RealmCriarSerializerTest(SimpleTestCase):
    """Testes da validação de criação de realm."""

    def test_valida_dados_obrigatorios(self) -> None:
        """Deve aplicar habilitado como verdadeiro por padrão."""
        serializer = RealmCriarSerializer(data={"nome": "sme-apps_1"})

        self.assertTrue(serializer.is_valid())
        self.assertEqual(
            serializer.validated_data,
            {"nome": "sme-apps_1", "habilitado": True, "oficial": False},
        )

    def test_rejeita_nome_ausente(self) -> None:
        """Deve exigir o nome do realm."""
        serializer = RealmCriarSerializer(data={})

        self.assertFalse(serializer.is_valid())
        self.assertIn("nome", serializer.errors)

    def test_rejeita_nome_com_caracteres_invalidos(self) -> None:
        """Deve recusar espaços e caracteres especiais no nome."""
        for nome in ("sme apps", "sme/apps", "seção"):
            serializer = RealmCriarSerializer(data={"nome": nome})

            self.assertFalse(serializer.is_valid())
            self.assertEqual(
                serializer.errors["nome"],
                ["Use apenas letras, números, hífen ou sublinhado."],
            )

    def test_permite_nome_exibicao_vazio(self) -> None:
        """Deve aceitar o nome de exibição vazio."""
        serializer = RealmCriarSerializer(
            data={"nome": "sme", "nome_exibicao": ""},
        )

        self.assertTrue(serializer.is_valid())


class RealmAtualizarSerializerTest(SimpleTestCase):
    """Testes da validação de atualização de realm."""

    def test_valida_campos_informados(self) -> None:
        """Deve aceitar a atualização da situação do realm."""
        serializer = RealmAtualizarSerializer(data={"habilitado": False})

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data, {"habilitado": False})

    def test_rejeita_atualizacao_sem_campos(self) -> None:
        """Deve exigir ao menos um campo."""
        serializer = RealmAtualizarSerializer(data={})

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors["non_field_errors"],
            ["Informe ao menos um campo para atualização."],
        )


@override_settings(REALM_FINALIDADES_TESTE=["Sandbox", "UX"])
class FinalidadeSerializerTest(SimpleTestCase):
    """Testes da validação da finalidade de teste."""

    def test_aceita_finalidade_configurada(self) -> None:
        """Deve aceitar uma finalidade da lista configurada."""
        serializer = RealmAtualizarSerializer(data={"finalidade": "UX"})

        self.assertTrue(serializer.is_valid())

    def test_aceita_finalidade_vazia(self) -> None:
        """Deve aceitar vazio para remover a finalidade."""
        serializer = RealmCriarSerializer(
            data={"nome": "sandbox", "finalidade": ""},
        )

        self.assertTrue(serializer.is_valid())

    def test_rejeita_finalidade_fora_da_lista(self) -> None:
        """Deve recusar finalidade não configurada."""
        serializer = RealmAtualizarSerializer(data={"finalidade": "QA"})

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors["finalidade"],
            ["Finalidade inválida. Opções: Sandbox, UX."],
        )

    @override_settings(REALM_FINALIDADES_TESTE=[])
    def test_rejeita_finalidade_sem_lista_configurada(self) -> None:
        """Deve informar quando nenhuma finalidade está configurada."""
        serializer = RealmAtualizarSerializer(data={"finalidade": "UX"})

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors["finalidade"],
            ["Finalidade inválida. Opções: nenhuma configurada."],
        )
