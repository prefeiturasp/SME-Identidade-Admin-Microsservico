"""Testes dos serializers da API administrativa de usuários."""

from django.test import SimpleTestCase

from apps.keycloak_admin.usuarios.api.serializers import (
    UsuarioAlterarEmailSerializer,
    UsuarioAlterarSenhaSerializer,
    UsuarioAtualizarSerializer,
    UsuarioClientRoleSerializer,
    UsuarioConsultaSerializer,
    UsuarioCriarSerializer,
    UsuarioGrupoSerializer,
    UsuarioRealmRoleSerializer,
    UsuarioSerializer,
)


class UsuarioCriarSerializerTest(SimpleTestCase):
    """Testa o serializer de criação de usuários."""

    def dados_validos(self) -> dict[str, str]:
        """Retorna dados válidos para criação de um usuário."""
        return {
            "usuario": "Usuario Teste",
            "nome": "Usuario",
            "sobrenome": "Teste",
            "email": "usuario.teste@example.com",
            "cpf": "12345678901",
            "rf": "RF12345",
        }

    def test_deve_validar_dados_obrigatorios(self) -> None:
        """Deve aceitar dados válidos para criação."""
        serializer = UsuarioCriarSerializer(
            data=self.dados_validos(),
        )

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["usuario"], "Usuario Teste")

    def test_deve_permitir_sobrenome_ausente(self) -> None:
        """Deve aceitar a criação sem sobrenome."""
        dados = self.dados_validos()
        dados.pop("sobrenome")

        serializer = UsuarioCriarSerializer(data=dados)

        self.assertTrue(serializer.is_valid())

    def test_deve_permitir_sobrenome_vazio(self) -> None:
        """Deve aceitar sobrenome vazio."""
        dados = self.dados_validos()
        dados["sobrenome"] = ""

        serializer = UsuarioCriarSerializer(data=dados)

        self.assertTrue(serializer.is_valid())

    def test_deve_rejeitar_email_invalido(self) -> None:
        """Deve rejeitar endereço de e-mail inválido."""
        dados = self.dados_validos()
        dados["email"] = "email-invalido"

        serializer = UsuarioCriarSerializer(data=dados)

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_deve_rejeitar_cpf_maior_que_o_limite(self) -> None:
        """Deve rejeitar CPF com mais de 11 caracteres."""
        dados = self.dados_validos()
        dados["cpf"] = "123456789012"

        serializer = UsuarioCriarSerializer(data=dados)

        self.assertFalse(serializer.is_valid())
        self.assertIn("cpf", serializer.errors)

    def test_deve_rejeitar_campo_obrigatorio_ausente(self) -> None:
        """Deve rejeitar ausência de campo obrigatório."""
        dados = self.dados_validos()
        dados.pop("rf")

        serializer = UsuarioCriarSerializer(data=dados)

        self.assertFalse(serializer.is_valid())
        self.assertIn("rf", serializer.errors)


class UsuarioConsultaSerializerTest(SimpleTestCase):
    """Testa o serializer de consulta de usuários."""

    def test_deve_aceitar_consulta_sem_filtros(self) -> None:
        """Deve aceitar consulta sem filtros específicos."""
        serializer = UsuarioConsultaSerializer(data={})

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["limite"], 100)

    def test_deve_aceitar_usuario_id(self) -> None:
        """Deve aceitar consulta por ID do usuário."""
        serializer = UsuarioConsultaSerializer(
            data={"usuario_id": "usuario-id"},
        )

        self.assertTrue(serializer.is_valid())

    def test_deve_aceitar_cpf(self) -> None:
        """Deve aceitar consulta por CPF."""
        serializer = UsuarioConsultaSerializer(
            data={"cpf": "12345678901"},
        )

        self.assertTrue(serializer.is_valid())

    def test_deve_aceitar_rf(self) -> None:
        """Deve aceitar consulta por registro funcional."""
        serializer = UsuarioConsultaSerializer(
            data={"rf": "RF12345"},
        )

        self.assertTrue(serializer.is_valid())

    def test_deve_aceitar_email(self) -> None:
        """Deve aceitar consulta por e-mail."""
        serializer = UsuarioConsultaSerializer(
            data={"email": "usuario.teste@example.com"},
        )

        self.assertTrue(serializer.is_valid())

    def test_deve_aceitar_busca(self) -> None:
        """Deve aceitar pesquisa geral."""
        serializer = UsuarioConsultaSerializer(
            data={"busca": "Usuario Teste"},
        )

        self.assertTrue(serializer.is_valid())

    def test_deve_aceitar_limite_dentro_do_intervalo(self) -> None:
        """Deve aceitar limite entre 1 e 1000."""
        serializer = UsuarioConsultaSerializer(
            data={"limite": 500},
        )

        self.assertTrue(serializer.is_valid())

    def test_deve_rejeitar_limite_menor_que_um(self) -> None:
        """Deve rejeitar limite inferior a 1."""
        serializer = UsuarioConsultaSerializer(
            data={"limite": 0},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("limite", serializer.errors)

    def test_deve_rejeitar_limite_maior_que_mil(self) -> None:
        """Deve rejeitar limite superior a 1000."""
        serializer = UsuarioConsultaSerializer(
            data={"limite": 1001},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("limite", serializer.errors)

    def test_deve_rejeitar_dois_identificadores(self) -> None:
        """Deve rejeitar mais de um identificador específico."""
        serializer = UsuarioConsultaSerializer(
            data={
                "usuario_id": "usuario-id",
                "cpf": "12345678901",
            },
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("consulta", serializer.errors)

    def test_deve_rejeitar_tres_identificadores(self) -> None:
        """Deve rejeitar três identificadores específicos."""
        serializer = UsuarioConsultaSerializer(
            data={
                "usuario_id": "usuario-id",
                "cpf": "12345678901",
                "rf": "RF12345",
            },
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("consulta", serializer.errors)

    def test_deve_rejeitar_busca_com_usuario_id(self) -> None:
        """Deve rejeitar busca combinada com ID."""
        serializer = UsuarioConsultaSerializer(
            data={
                "usuario_id": "usuario-id",
                "busca": "Usuario Teste",
            },
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("busca", serializer.errors)

    def test_deve_rejeitar_busca_com_cpf(self) -> None:
        """Deve rejeitar busca combinada com CPF."""
        serializer = UsuarioConsultaSerializer(
            data={
                "cpf": "12345678901",
                "busca": "Usuario Teste",
            },
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("busca", serializer.errors)

    def test_deve_rejeitar_busca_com_rf(self) -> None:
        """Deve rejeitar busca combinada com RF."""
        serializer = UsuarioConsultaSerializer(
            data={
                "rf": "RF12345",
                "busca": "Usuario Teste",
            },
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("busca", serializer.errors)

    def test_deve_rejeitar_busca_com_email(self) -> None:
        """Deve rejeitar busca combinada com e-mail."""
        serializer = UsuarioConsultaSerializer(
            data={
                "email": "usuario.teste@example.com",
                "busca": "Usuario Teste",
            },
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("busca", serializer.errors)


class UsuarioAtualizarSerializerTest(SimpleTestCase):
    """Testa o serializer de atualização de usuários."""

    def test_deve_aceitar_dados_vazios(self) -> None:
        """Deve aceitar atualização sem campos informados."""
        serializer = UsuarioAtualizarSerializer(data={})

        self.assertTrue(serializer.is_valid())

    def test_deve_aceitar_dados_validos(self) -> None:
        """Deve aceitar campos válidos para atualização."""
        serializer = UsuarioAtualizarSerializer(
            data={
                "usuario": "Usuario Teste",
                "nome": "Usuario",
                "sobrenome": "Teste",
                "cpf": "12345678901",
                "rf": "RF12345",
                "habilitado": True,
            },
        )

        self.assertTrue(serializer.is_valid())

    def test_deve_aceitar_sobrenome_vazio(self) -> None:
        """Deve aceitar sobrenome vazio."""
        serializer = UsuarioAtualizarSerializer(
            data={"sobrenome": ""},
        )

        self.assertTrue(serializer.is_valid())

    def test_deve_rejeitar_cpf_maior_que_o_limite(self) -> None:
        """Deve rejeitar CPF acima do tamanho permitido."""
        serializer = UsuarioAtualizarSerializer(
            data={"cpf": "123456789012"},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("cpf", serializer.errors)


class UsuarioAlterarEmailSerializerTest(SimpleTestCase):
    """Testa o serializer de alteração de e-mail."""

    def test_deve_aceitar_email_valido(self) -> None:
        """Deve aceitar um endereço de e-mail válido."""
        serializer = UsuarioAlterarEmailSerializer(
            data={"email": "usuario.teste@example.com"},
        )

        self.assertTrue(serializer.is_valid())

    def test_deve_rejeitar_email_invalido(self) -> None:
        """Deve rejeitar um endereço de e-mail inválido."""
        serializer = UsuarioAlterarEmailSerializer(
            data={"email": "email-invalido"},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)


class UsuarioAlterarSenhaSerializerTest(SimpleTestCase):
    """Testa o serializer de alteração de senha."""

    def test_deve_aceitar_senha(self) -> None:
        """Deve aceitar uma senha informada."""
        serializer = UsuarioAlterarSenhaSerializer(
            data={"senha": "SenhaSegura123"},
        )

        self.assertTrue(serializer.is_valid())

    def test_deve_expor_senha_apenas_na_escrita(self) -> None:
        """Deve configurar o campo de senha como somente escrita."""
        campo = UsuarioAlterarSenhaSerializer().fields["senha"]

        self.assertTrue(campo.write_only)


class UsuarioSerializerTest(SimpleTestCase):
    """Testa o serializer de representação de usuários."""

    def dados_validos(self) -> dict[str, object]:
        """Retorna dados válidos para representação de um usuário."""
        return {
            "id": "usuario-id",
            "username": "Usuario Teste",
            "firstName": "Usuario",
            "lastName": "Teste",
            "email": "usuario.teste@example.com",
            "enabled": True,
            "emailVerified": True,
            "cpf": "12345678901",
            "rf": "RF12345",
        }

    def test_deve_serializar_usuario(self) -> None:
        """Deve serializar os dados de um usuário."""
        serializer = UsuarioSerializer(data=self.dados_validos())

        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["id"], "usuario-id")

    def test_deve_aceitar_campos_nulos(self) -> None:
        """Deve aceitar campos opcionais com valor nulo."""
        dados = self.dados_validos()
        dados.update(
            {
                "username": None,
                "firstName": None,
                "lastName": None,
                "email": None,
                "cpf": None,
                "rf": None,
            }
        )

        serializer = UsuarioSerializer(data=dados)

        self.assertTrue(serializer.is_valid())


class UsuarioGrupoSerializerTest(SimpleTestCase):
    """Testa o serializer de associação de usuário a grupo."""

    def test_deve_aceitar_grupo_id(self) -> None:
        """Deve aceitar o ID de um grupo."""
        serializer = UsuarioGrupoSerializer(
            data={"grupo_id": "grupo-id"},
        )

        self.assertTrue(serializer.is_valid())

    def test_deve_exigir_grupo_id(self) -> None:
        """Deve exigir o ID do grupo."""
        serializer = UsuarioGrupoSerializer(data={})

        self.assertFalse(serializer.is_valid())
        self.assertIn("grupo_id", serializer.errors)


class UsuarioRealmRoleSerializerTest(SimpleTestCase):
    """Testa o serializer de associação de Realm Role."""

    def test_deve_aceitar_nome_da_permissao(self) -> None:
        """Deve aceitar o nome da Realm Role."""
        serializer = UsuarioRealmRoleSerializer(
            data={"nome_permissao": "Administrador"},
        )

        self.assertTrue(serializer.is_valid())

    def test_deve_exigir_nome_da_permissao(self) -> None:
        """Deve exigir o nome da Realm Role."""
        serializer = UsuarioRealmRoleSerializer(data={})

        self.assertFalse(serializer.is_valid())
        self.assertIn("nome_permissao", serializer.errors)


class UsuarioClientRoleSerializerTest(SimpleTestCase):
    """Testa o serializer de associação de Client Role."""

    def dados_validos(self) -> dict[str, str]:
        """Retorna dados válidos para associação de Client Role."""
        return {
            "client_uuid": "client-id",
            "nome_permissao": "Administrador",
        }

    def test_deve_aceitar_dados_validos(self) -> None:
        """Deve aceitar client e role válidos."""
        serializer = UsuarioClientRoleSerializer(
            data=self.dados_validos(),
        )

        self.assertTrue(serializer.is_valid())

    def test_deve_exigir_client_uuid(self) -> None:
        """Deve exigir o ID do client."""
        dados = self.dados_validos()
        dados.pop("client_uuid")

        serializer = UsuarioClientRoleSerializer(data=dados)

        self.assertFalse(serializer.is_valid())
        self.assertIn("client_uuid", serializer.errors)

    def test_deve_exigir_nome_da_permissao(self) -> None:
        """Deve exigir o nome da Client Role."""
        dados = self.dados_validos()
        dados.pop("nome_permissao")

        serializer = UsuarioClientRoleSerializer(data=dados)

        self.assertFalse(serializer.is_valid())
        self.assertIn("nome_permissao", serializer.errors)
