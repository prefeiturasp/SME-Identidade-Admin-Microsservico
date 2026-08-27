"""Testes do tratamento de exceções da API administrativa do Keycloak."""

from django.test import SimpleTestCase
from rest_framework import status

from apps.keycloak_admin.api.exception_handler import (
    tratar_excecao_keycloak,
)
from apps.keycloak_admin.exceptions import (
    ErroAutenticacaoKeycloakError,
    ErroComunicacaoKeycloakError,
    KeycloakAdminError,
    OperacaoNaoPermitidaError,
    RecursoJaExisteError,
    RecursoNaoEncontradoError,
)


class TratarExcecaoKeycloakTestCase(SimpleTestCase):
    """Testa a conversão de exceções de domínio em respostas HTTP."""

    def test_trata_erro_autenticacao(self) -> None:
        """Deve retornar HTTP 401 para erro de autenticação."""
        excecao = ErroAutenticacaoKeycloakError("Falha na autenticação.")

        resposta = tratar_excecao_keycloak(excecao)

        self.assertEqual(
            resposta.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        self.assertEqual(
            resposta.data,
            {
                "codigo": "erro_autenticacao",
                "mensagem": "Falha na autenticação.",
            },
        )

    def test_trata_operacao_nao_permitida(self) -> None:
        """Deve retornar HTTP 400 para operação não permitida."""
        excecao = OperacaoNaoPermitidaError("Operação não permitida.")

        resposta = tratar_excecao_keycloak(excecao)

        self.assertEqual(
            resposta.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            resposta.data,
            {
                "codigo": "operacao_nao_permitida",
                "mensagem": "Operação não permitida.",
            },
        )

    def test_trata_recurso_nao_encontrado(self) -> None:
        """Deve retornar HTTP 400 para recurso não encontrado."""
        excecao = RecursoNaoEncontradoError("Recurso não encontrado.")

        resposta = tratar_excecao_keycloak(excecao)

        self.assertEqual(
            resposta.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            resposta.data,
            {
                "codigo": "recurso_nao_encontrado",
                "mensagem": "Recurso não encontrado.",
            },
        )

    def test_trata_recurso_ja_existe(self) -> None:
        """Deve retornar HTTP 400 para recurso já existente."""
        excecao = RecursoJaExisteError("Recurso já existe.")

        resposta = tratar_excecao_keycloak(excecao)

        self.assertEqual(
            resposta.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            resposta.data,
            {
                "codigo": "recurso_ja_existe",
                "mensagem": "Recurso já existe.",
            },
        )

    def test_trata_erro_comunicacao(self) -> None:
        """Deve retornar HTTP 400 para erro de comunicação."""
        excecao = ErroComunicacaoKeycloakError("Falha de comunicação.")

        resposta = tratar_excecao_keycloak(excecao)

        self.assertEqual(
            resposta.status_code,
            status.HTTP_400_BAD_REQUEST,
        )
        self.assertEqual(
            resposta.data,
            {
                "codigo": "erro_comunicacao",
                "mensagem": "Falha de comunicação.",
            },
        )

    def test_trata_excecao_nao_mapeada(self) -> None:
        """Deve utilizar HTTP 500 para exceção sem mapeamento específico."""
        excecao = KeycloakAdminError("Erro administrativo não mapeado.")

        resposta = tratar_excecao_keycloak(excecao)

        self.assertEqual(
            resposta.status_code,
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
        self.assertEqual(
            resposta.data,
            {
                "codigo": "erro_interno",
                "mensagem": "Erro administrativo não mapeado.",
            },
        )

    def test_utiliza_mapeamento_de_classe_base(self) -> None:
        """Deve reconhecer subclasses das exceções mapeadas."""
        excecao = ErroAutenticacaoKeycloakError("Falha de autenticação.")

        resposta = tratar_excecao_keycloak(excecao)

        self.assertEqual(
            resposta.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        self.assertEqual(
            resposta.data["codigo"],
            "erro_autenticacao",
        )
