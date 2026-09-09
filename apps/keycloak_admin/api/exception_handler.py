"""Tratamento de exceções da API administrativa do Keycloak."""

from rest_framework import status
from rest_framework.response import Response

from apps.keycloak_admin.exceptions import (
    ErroAutenticacaoKeycloakError,
    ErroComunicacaoKeycloakError,
    KeycloakAdminError,
    OperacaoNaoPermitidaError,
    RecursoJaExisteError,
    RecursoNaoEncontradoError,
)

_EXCECOES_HTTP = {
    ErroAutenticacaoKeycloakError: (
        status.HTTP_401_UNAUTHORIZED,
        "erro_autenticacao",
    ),
    OperacaoNaoPermitidaError: (
        status.HTTP_400_BAD_REQUEST,
        "operacao_nao_permitida",
    ),
    RecursoNaoEncontradoError: (
        status.HTTP_400_BAD_REQUEST,
        "recurso_nao_encontrado",
    ),
    RecursoJaExisteError: (
        status.HTTP_400_BAD_REQUEST,
        "recurso_ja_existe",
    ),
    ErroComunicacaoKeycloakError: (
        status.HTTP_400_BAD_REQUEST,
        "erro_comunicacao",
    ),
}


def tratar_excecao_keycloak(
    exc: KeycloakAdminError,
) -> Response:
    """Trata uma exceção de domínio em uma resposta HTTP padronizada.

    Utiliza o tipo da exceção para determinar o status HTTP e o código
    funcional que serão retornados pela API. Exceções de domínio que
    ainda não possuam um mapeamento específico utilizam HTTP 500 e o
    código ``erro_interno`` como comportamento de fallback.

    Args:
        exc: Exceção de domínio gerada durante uma operação administrativa
            no Keycloak.

    Returns:
        Resposta HTTP contendo o código funcional e a mensagem associada
        à exceção.
    """
    status_code, codigo = _obter_resposta_http(exc)

    return Response(
        {
            "codigo": codigo,
            "mensagem": str(exc),
        },
        status=status_code,
    )


def _obter_resposta_http(
    exc: KeycloakAdminError,
) -> tuple[int, str]:
    """Obtém o status HTTP e o código funcional de uma exceção.

    A resolução utiliza ``isinstance`` para preservar o comportamento
    esperado quando uma exceção específica for derivada de outra exceção
    de domínio já mapeada.

    Args:
        exc: Exceção de domínio que será convertida.

    Returns:
        Tupla contendo o status HTTP e o código funcional correspondente.
        Quando a exceção não possui um mapeamento específico, retorna
        HTTP 500 e ``erro_interno``.
    """
    for excecao, resposta in _EXCECOES_HTTP.items():
        if isinstance(exc, excecao):
            return resposta

    return (
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "erro_interno",
    )
