"""Serviço base para administração do Keycloak."""

from collections.abc import Callable
from typing import NoReturn, ParamSpec, TypeVar

from django.conf import settings
from keycloak import KeycloakAdmin
from keycloak.exceptions import (
    KeycloakDeleteError,
    KeycloakGetError,
    KeycloakPostError,
    KeycloakPutError,
)

from apps.keycloak_admin.exceptions import (
    ErroAutenticacaoKeycloakError,
    ErroComunicacaoKeycloakError,
    ErroRequisicaoKeycloakError,
    OperacaoNaoPermitidaError,
    RecursoJaExisteError,
    RecursoNaoEncontradoError,
)

P = ParamSpec("P")
T = TypeVar("T")


class KeycloakAdminService:
    """Centraliza a comunicação administrativa com o Keycloak.

    Responsabiliza-se por criar o cliente administrativo para o realm
    configurado e por centralizar a execução das operações da Admin API,
    traduzindo exceções da biblioteca python-keycloak para exceções do
    domínio da aplicação.
    """

    def __init__(self, realm: str | None = None) -> None:
        """Inicializa o serviço administrativo do Keycloak.

        Args:
            realm: Realm no qual as operações administrativas serão
                executadas. Quando ``None``, utiliza o realm padrão
                configurado em ``KEYCLOAK_REALM``.
        """
        self.realm = realm if realm is not None else settings.KEYCLOAK_REALM
        self.cliente = self._criar_cliente()

    def _criar_cliente(self) -> KeycloakAdmin:
        """Cria o cliente administrativo autenticado no Keycloak.

        Utiliza as configurações da aplicação para definir o servidor,
        as credenciais administrativas, o realm de destino e a política
        de verificação do certificado SSL.

        Returns:
            Instância de ``KeycloakAdmin`` configurada para realizar
            operações administrativas no realm selecionado.
        """
        return KeycloakAdmin(
            server_url=settings.KEYCLOAK_URL_SERVIDOR,
            username=settings.KEYCLOAK_USUARIO_ADMIN,
            password=settings.KEYCLOAK_SENHA_ADMIN,
            realm_name=self.realm,
            user_realm_name="master",
            verify=settings.KEYCLOAK_VERIFICAR_SSL,
        )

    def executar(
        self,
        operacao: Callable[P, T],
        *args: P.args,
        **kwargs: P.kwargs,
    ) -> T:
        """Executa uma operação administrativa do Keycloak.

        Este método centraliza a execução das operações realizadas por
        meio do cliente ``KeycloakAdmin``. Exceções HTTP geradas pelo
        python-keycloak são encaminhadas para ``_traduzir_excecao()``,
        que as converte para exceções específicas do domínio da aplicação.

        Args:
            operacao: Função ou método do cliente administrativo que
                será executado.
            *args: Argumentos posicionais necessários para a operação.
            **kwargs: Argumentos nomeados necessários para a operação.

        Returns:
            Resultado retornado pela operação executada.

        Raises:
            ErroAutenticacaoKeycloakError: Quando o Keycloak retorna HTTP
                401, indicando falha de autenticação.
            OperacaoNaoPermitidaError: Quando o Keycloak retorna HTTP 403,
                indicando que a operação não é permitida.
            RecursoNaoEncontradoError: Quando o Keycloak retorna HTTP 404,
                indicando que o recurso solicitado não existe.
            RecursoJaExisteError: Quando o Keycloak retorna HTTP 409,
                indicando conflito com um recurso existente.
            ErroRequisicaoKeycloakError: Quando o Keycloak retorna HTTP 400
                ou 422, indicando uma requisição inválida.
            ErroComunicacaoKeycloakError: Quando ocorre outro erro HTTP
                durante a comunicação com o Keycloak.
        """
        try:
            return operacao(*args, **kwargs)
        except (
            KeycloakGetError,
            KeycloakPostError,
            KeycloakPutError,
            KeycloakDeleteError,
        ) as exc:
            self._traduzir_excecao(exc)

    @staticmethod
    def _traduzir_excecao(exc: Exception) -> NoReturn:
        """Trata uma exceção do python-keycloak para o domínio.

        A conversão utiliza o código HTTP armazenado em ``response_code``
        pela biblioteca python-keycloak. A exceção original é preservada
        como causa da exceção de domínio para facilitar diagnóstico e
        rastreamento do erro.

        Args:
            exc: Exceção HTTP gerada pela biblioteca python-keycloak.

        Raises:
            ErroAutenticacaoKeycloakError: Para HTTP 401.
            OperacaoNaoPermitidaError: Para HTTP 403.
            RecursoNaoEncontradoError: Para HTTP 404.
            RecursoJaExisteError: Para HTTP 409.
            ErroRequisicaoKeycloakError: Para HTTP 400 ou 422.
            ErroComunicacaoKeycloakError: Para outros códigos HTTP.
        """
        status_code = getattr(exc, "response_code", None)

        if status_code == 401:
            raise ErroAutenticacaoKeycloakError(
                "Falha na autenticação com o Keycloak."
            ) from exc

        if status_code == 403:
            raise OperacaoNaoPermitidaError(
                "Operação não permitida pelo Keycloak."
            ) from exc

        if status_code == 404:
            raise RecursoNaoEncontradoError(
                "Recurso não encontrado no Keycloak."
            ) from exc

        if status_code == 409:
            raise RecursoJaExisteError(
                "Recurso já existe no Keycloak."
            ) from exc

        if status_code in {400, 422}:
            raise ErroRequisicaoKeycloakError(
                "Requisição inválida para o Keycloak."
            ) from exc

        raise ErroComunicacaoKeycloakError(
            "Erro ao executar operação no Keycloak."
        ) from exc
