"""Serviço de administração de usuários no Keycloak."""

import logging
from typing import Any

from django.conf import settings

from apps.keycloak_admin.admin_kc import KeycloakAdminService
from apps.keycloak_admin.exceptions import ErroComunicacaoKeycloakError

logger = logging.getLogger(__name__)


class UsuarioService:
    """Centraliza as operações administrativas de usuários no Keycloak."""

    def __init__(
        self,
        admin: KeycloakAdminService | None = None,
    ) -> None:
        """Inicializa o serviço de administração de usuários.

        Args:
            admin: Serviço responsável pela comunicação com o Keycloak.
                Quando não informado, uma nova instância é criada.
        """
        self.admin = admin or KeycloakAdminService()

    def criar(
        self,
        usuario: str,
        nome: str,
        email: str,
        cpf: str,
        rf: str,
        sobrenome: str | None = None,
    ) -> str:
        """Cria um usuário no Keycloak.

        O usuário é criado habilitado e recebe uma senha inicial temporária.
        A senha é determinada a partir do registro funcional, CPF ou nome
        de usuário, conforme a regra definida em
        ``_resolver_senha_inicial()``.

        Args:
            usuario: Nome de identificação do usuário.
            nome: Nome do usuário.
            email: Endereço de e-mail do usuário.
            cpf: CPF do usuário.
            rf: Registro funcional do usuário.
            sobrenome: Sobrenome do usuário.

        Returns:
            ID do usuário criado no Keycloak.
        """
        payload: dict[str, Any] = {
            "username": usuario,
            "firstName": nome,
            "lastName": sobrenome,
            "email": email,
            "enabled": True,
            "attributes": {
                "cpf": [cpf],
                "rf": [rf],
            },
        }

        senha_inicial = self._resolver_senha_inicial(payload)

        payload["credentials"] = [
            {
                "type": "password",
                "value": senha_inicial,
                "temporary": True,
            }
        ]

        logger.info(
            "Criando usuário no Keycloak.",
            extra={
                "usuario": usuario,
                "rf": rf,
            },
        )

        return self.admin.executar(
            self.admin.cliente.create_user,
            payload=payload,
        )

    def consultar(
        self,
        usuario_id: str | None = None,
        cpf: str | None = None,
        rf: str | None = None,
        email: str | None = None,
        busca: str | None = None,
        limite: int = 100,
    ) -> list[dict[str, Any]]:
        """Consulta usuários do realm.

        Os critérios de identificação são mutuamente exclusivos.
        Quando nenhum critério específico é informado, a consulta
        retorna os usuários encontrados pela busca geral.

        Args:
            usuario_id: ID do usuário no Keycloak.
            cpf: CPF do usuário.
            rf: Registro funcional do usuário.
            email: Endereço de e-mail do usuário.
            busca: Texto utilizado para pesquisa geral.
            limite: Quantidade máxima de usuários retornados.

        Returns:
            Lista de usuários normalizados.

        Raises:
            ValueError: Quando mais de um critério de identificação
                é informado.
        """
        criterios = {
            "usuario_id": usuario_id,
            "cpf": cpf,
            "rf": rf,
            "email": email,
        }

        informados = [
            nome for nome, valor in criterios.items() if valor is not None
        ]

        if len(informados) > 1:
            raise ValueError(
                "Informe apenas um critério de identificação: "
                "usuario_id, cpf, rf ou email."
            )

        logger.debug(
            "Consultando usuários no Keycloak.",
            extra={
                "criterio": informados[0] if informados else None,
                "limite": limite,
            },
        )

        if usuario_id is not None:
            return [self._obter_por_id(usuario_id)]

        if cpf is not None:
            usuarios = self._buscar_por_atributo(
                nome="cpf",
                valor=cpf,
            )
        elif rf is not None:
            usuarios = self._buscar_por_atributo(
                nome="rf",
                valor=rf,
            )
        elif email is not None:
            usuarios = self._buscar_por_email(email)
        else:
            parametros: dict[str, Any] = {
                "max": limite,
            }

            if busca:
                parametros["search"] = busca

            usuarios = self.admin.executar(
                self.admin.cliente.get_users,
                query=parametros,
            )

        return [self._normalizar_usuario(usuario) for usuario in usuarios]

    def atualizar(
        self,
        usuario_id: str,
        usuario: str | None = None,
        nome: str | None = None,
        sobrenome: str | None = None,
        cpf: str | None = None,
        rf: str | None = None,
        habilitado: bool | None = None,
    ) -> None:
        """Atualiza os dados cadastrais de um usuário.

        O endereço de e-mail não é alterado por este método. A alteração
        de e-mail possui fluxo próprio através de ``alterar_email()``.

        Apenas os campos informados são alterados.

        Args:
            usuario_id: ID do usuário no Keycloak.
            usuario: Novo nome de identificação.
            nome: Novo nome.
            sobrenome: Novo sobrenome.
            cpf: Novo CPF.
            rf: Novo registro funcional.
            habilitado: Define se o usuário deve permanecer habilitado.
        """
        usuario_atual = self.admin.executar(
            self.admin.cliente.get_user,
            user_id=usuario_id,
        )

        atributos = dict(
            usuario_atual.get("attributes") or {},
        )

        payload: dict[str, Any] = {
            "username": usuario_atual.get("username"),
            "firstName": usuario_atual.get("firstName"),
            "lastName": usuario_atual.get("lastName"),
            "email": usuario_atual.get("email"),
            "enabled": usuario_atual.get("enabled", True),
            "attributes": atributos,
        }

        if usuario is not None:
            payload["username"] = usuario

        if nome is not None:
            payload["firstName"] = nome

        if sobrenome is not None:
            payload["lastName"] = sobrenome

        if cpf is not None:
            atributos["cpf"] = [cpf]

        if rf is not None:
            atributos["rf"] = [rf]

        if habilitado is not None:
            payload["enabled"] = habilitado

        logger.info(
            "Atualizando usuário no Keycloak.",
            extra={"usuario_id": usuario_id},
        )

        self.admin.executar(
            self.admin.cliente.update_user,
            user_id=usuario_id,
            payload=payload,
        )

    def alterar_email(
        self,
        usuario_id: str,
        email: str,
    ) -> dict[str, bool]:
        """Altera o e-mail e solicita sua verificação.

        A alteração do e-mail e o envio da verificação são operações
        independentes no Keycloak. Uma falha no envio da verificação
        não impede que o novo e-mail permaneça configurado.

        Args:
            usuario_id: ID do usuário no Keycloak.
            email: Novo endereço de e-mail.

        Returns:
            Resultado da alteração e da solicitação de verificação.
        """
        logger.info(
            "Alterando e-mail do usuário no Keycloak.",
            extra={"usuario_id": usuario_id},
        )

        self.admin.executar(
            self.admin.cliente.update_user,
            user_id=usuario_id,
            payload={
                "email": email,
            },
        )

        try:
            self.admin.executar(
                self.admin.cliente.send_verify_email,
                user_id=usuario_id,
                client_id=settings.KEYCLOAK_LOGIN_CLIENT_ID,
            )
        except ErroComunicacaoKeycloakError:
            logger.exception(
                "Falha ao enviar verificação de e-mail.",
                extra={"usuario_id": usuario_id},
            )

            return {
                "email_alterado": True,
                "verificacao_enviada": False,
            }

        return {
            "email_alterado": True,
            "verificacao_enviada": True,
        }

    def alterar_senha(
        self,
        usuario_id: str,
        senha: str,
        senha_temporaria: bool = False,
    ) -> None:
        """Altera a senha de um usuário.

        Args:
            usuario_id: ID do usuário no Keycloak.
            senha: Nova senha do usuário.
            senha_temporaria: Indica se a senha deve ser alterada
                no próximo acesso.
        """
        logger.info(
            "Alterando senha do usuário no Keycloak.",
            extra={
                "usuario_id": usuario_id,
                "senha_temporaria": senha_temporaria,
            },
        )

        self.admin.executar(
            self.admin.cliente.set_user_password,
            user_id=usuario_id,
            password=senha,
            temporary=senha_temporaria,
        )

    def associar_grupo(
        self,
        usuario_id: str,
        grupo_id: str,
    ) -> None:
        """Associa um usuário a um grupo.

        Args:
            usuario_id: ID interno do usuário no Keycloak.
            grupo_id: ID interno do grupo no Keycloak.
        """
        logger.info(
            "Associando usuário ao grupo no Keycloak.",
            extra={
                "usuario_id": usuario_id,
                "grupo_id": grupo_id,
            },
        )

        self.admin.executar(
            self.admin.cliente.group_user_add,
            user_id=usuario_id,
            group_id=grupo_id,
        )

    def desassociar_grupo(
        self,
        usuario_id: str,
        grupo_id: str,
    ) -> None:
        """Desassocia um usuário de um grupo.

        A operação remove somente o vínculo entre o usuário e o grupo,
        mantendo ambos os recursos existentes no Keycloak.

        Args:
            usuario_id: ID interno do usuário no Keycloak.
            grupo_id: ID interno do grupo no Keycloak.
        """
        logger.info(
            "Removendo usuário do grupo no Keycloak.",
            extra={
                "usuario_id": usuario_id,
                "grupo_id": grupo_id,
            },
        )

        self.admin.executar(
            self.admin.cliente.group_user_remove,
            user_id=usuario_id,
            group_id=grupo_id,
        )

    def associar_role_realm(
        self,
        usuario_id: str,
        nome_permissao: str,
    ) -> None:
        """Associa uma Realm Role a um usuário.

        Args:
            usuario_id: ID interno do usuário no Keycloak.
            nome_permissao: Nome da Realm Role.
        """
        logger.info(
            "Associando Realm Role ao usuário no Keycloak.",
            extra={
                "usuario_id": usuario_id,
                "nome_role": nome_permissao,
            },
        )

        role = self.admin.executar(
            self.admin.cliente.get_realm_role,
            role_name=nome_permissao,
        )

        self.admin.executar(
            self.admin.cliente.assign_realm_roles,
            user_id=usuario_id,
            roles=[role],
        )

    def desassociar_role_realm(
        self,
        usuario_id: str,
        nome_permissao: str,
    ) -> None:
        """Desassocia uma Realm Role de um usuário.

        A operação remove somente o vínculo da role com o usuário.
        A Realm Role permanece existente no Keycloak.

        Args:
            usuario_id: ID interno do usuário no Keycloak.
            nome_permissao: Nome da Realm Role que será removida.
        """
        logger.info(
            "Removendo Realm Role do usuário.",
            extra={
                "usuario_id": usuario_id,
                "nome_permissao": nome_permissao,
            },
        )

        role = self.admin.executar(
            self.admin.cliente.get_realm_role,
            role_name=nome_permissao,
        )

        self.admin.executar(
            self.admin.cliente.delete_realm_roles_of_user,
            user_id=usuario_id,
            roles=[role],
        )

    def associar_role_client(
        self,
        usuario_id: str,
        client_uuid: str,
        nome_permissao: str,
    ) -> None:
        """Associa uma Client Role a um usuário.

        Args:
            usuario_id: ID interno do usuário no Keycloak.
            client_uuid: ID interno do cliente no Keycloak.
            nome_permissao: Nome da Client Role.
        """
        logger.info(
            "Associando Client Role ao usuário no Keycloak.",
            extra={
                "usuario_id": usuario_id,
                "client_uuid": client_uuid,
                "nome_role": nome_permissao,
            },
        )

        role = self.admin.executar(
            self.admin.cliente.get_client_role,
            client_id=client_uuid,
            role_name=nome_permissao,
        )

        self.admin.executar(
            self.admin.cliente.assign_client_role,
            user_id=usuario_id,
            client_id=client_uuid,
            roles=[role],
        )

    def desassociar_role_client(
        self,
        usuario_id: str,
        client_uuid: str,
        nome_permissao: str,
    ) -> None:
        """Desassocia uma Client Role de um usuário.

        A operação remove somente o vínculo da role com o usuário.
        O client e a Client Role permanecem existentes no Keycloak.

        Args:
            usuario_id: ID interno do usuário no Keycloak.
            client_uuid: ID interno do cliente no Keycloak.
            nome_permissao: Nome da Client Role que será removida.
        """
        logger.info(
            "Removendo Client Role do usuário no Keycloak.",
            extra={
                "usuario_id": usuario_id,
                "client_uuid": client_uuid,
                "nome_permissao": nome_permissao,
            },
        )

        role = self.admin.executar(
            self.admin.cliente.get_client_role,
            client_id=client_uuid,
            role_name=nome_permissao,
        )

        self.admin.executar(
            self.admin.cliente.delete_client_roles_of_user,
            user_id=usuario_id,
            client_id=client_uuid,
            roles=[role],
        )

    def _obter_por_id(
        self,
        usuario_id: str,
    ) -> dict[str, Any]:
        """Obtém e normaliza um usuário pelo ID interno do Keycloak.

        Args:
            usuario_id: ID do usuário no Keycloak.

        Returns:
            Dados do usuário normalizados.
        """
        usuario = self.admin.executar(
            self.admin.cliente.get_user,
            user_id=usuario_id,
        )

        return self._normalizar_usuario(usuario)

    def _buscar_por_atributo(
        self,
        nome: str,
        valor: str,
    ) -> list[dict[str, Any]]:
        """Busca usuários por um atributo personalizado.

        Args:
            nome: Nome do atributo no Keycloak.
            valor: Valor utilizado na pesquisa.

        Returns:
            Lista de usuários encontrados.
        """
        return self.admin.executar(
            self.admin.cliente.get_users,
            query={
                "q": f"{nome}:{valor}",
            },
        )

    def _buscar_por_email(
        self,
        email: str,
    ) -> list[dict[str, Any]]:
        """Busca usuários pelo endereço de e-mail exato.

        Args:
            email: Endereço utilizado na pesquisa.

        Returns:
            Lista de usuários associados ao e-mail informado.
        """
        return self.admin.executar(
            self.admin.cliente.get_users,
            query={
                "email": email,
                "exact": True,
            },
        )

    @staticmethod
    def _normalizar_usuario(
        usuario: dict[str, Any],
    ) -> dict[str, Any]:
        """Normaliza os dados do usuário para o contrato interno.

        Os atributos personalizados ``cpf`` e ``rf`` são extraídos dos
        atributos do Keycloak e disponibilizados diretamente no retorno.

        Args:
            usuario: Dados do usuário retornados pelo Keycloak.

        Returns:
            Dados do usuário normalizados.
        """
        atributos = usuario.get("attributes") or {}

        return {
            "id": usuario.get("id"),
            "username": usuario.get("username"),
            "firstName": usuario.get("firstName"),
            "lastName": usuario.get("lastName"),
            "email": usuario.get("email"),
            "enabled": usuario.get("enabled", False),
            "emailVerified": usuario.get(
                "emailVerified",
                False,
            ),
            "cpf": UsuarioService._obter_atributo(
                atributos,
                "cpf",
            ),
            "rf": UsuarioService._obter_atributo(
                atributos,
                "rf",
            ),
        }

    @staticmethod
    def _obter_atributo(
        atributos: dict[str, Any],
        nome: str,
    ) -> str | None:
        """Obtém o primeiro valor textual de um atributo do Keycloak.

        Args:
            atributos: Atributos retornados pelo Keycloak.
            nome: Nome do atributo que será consultado.

        Returns:
            Primeiro valor textual encontrado ou ``None`` quando o
            atributo não existe, está vazio ou não possui valor textual.
        """
        valores = atributos.get(nome)

        if not isinstance(valores, list) or not valores:
            return None

        valor = valores[0]

        if not isinstance(valor, str):
            return None

        return valor

    @staticmethod
    def _resolver_senha_inicial(
        usuario: dict[str, Any],
    ) -> str:
        """Resolve a senha inicial temporária do usuário.

        A senha segue a ordem de prioridade: registro funcional,
        CPF contendo somente dígitos e, por último, nome de usuário.

        Args:
            usuario: Dados do usuário utilizados para determinar a
                senha inicial.

        Returns:
            Valor utilizado como senha inicial.
        """
        atributos = usuario.get("attributes") or {}

        rf = UsuarioService._obter_atributo(
            atributos,
            "rf",
        )

        if rf:
            return rf.strip()

        cpf = UsuarioService._obter_atributo(
            atributos,
            "cpf",
        )

        if cpf:
            cpf_numerico = "".join(
                caractere for caractere in cpf if caractere.isdigit()
            )

            if cpf_numerico:
                return cpf_numerico

        usuario_nome: object = usuario.get("username")

        if not isinstance(usuario_nome, str):
            raise ValueError(
                "O nome de usuário é obrigatório para definir "
                "a senha inicial."
            )

        return usuario_nome
