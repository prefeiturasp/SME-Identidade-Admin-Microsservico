"""Exceções personalizadas para a integração com o Keycloak."""


class KeycloakAdminError(Exception):
    """Exceção base para erros da administração do Keycloak."""


class RecursoNaoEncontradoError(KeycloakAdminError):
    """Indica que um recurso não foi encontrado no Keycloak."""


class RecursoJaExisteError(KeycloakAdminError):
    """Indica que um recurso já existe no Keycloak."""


class OperacaoNaoPermitidaError(KeycloakAdminError):
    """Indica que uma operação não é permitida pelo Keycloak."""


class ErroAutenticacaoKeycloakError(KeycloakAdminError):
    """Indica falha na autenticação administrativa com o Keycloak."""


class ErroRequisicaoKeycloakError(KeycloakAdminError):
    """Indica que uma requisição enviada ao Keycloak é inválida."""


class ErroComunicacaoKeycloakError(KeycloakAdminError):
    """Indica falha de comunicação com o Keycloak."""
