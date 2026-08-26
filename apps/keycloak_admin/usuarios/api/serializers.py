"""Serializers da API administrativa de usuários."""

from typing import Any

from rest_framework import serializers


class UsuarioCriarSerializer(serializers.Serializer):
    """Valida os dados necessários para criação de um usuário."""

    usuario = serializers.CharField(
        max_length=150,
        help_text="Nome de identificação do usuário no Keycloak.",
    )
    nome = serializers.CharField(
        max_length=150,
        help_text="Nome do usuário.",
    )
    sobrenome = serializers.CharField(
        max_length=150,
        required=False,
        allow_blank=True,
        help_text="Sobrenome do usuário.",
    )
    email = serializers.EmailField(
        help_text="Endereço de e-mail do usuário.",
    )
    cpf = serializers.CharField(
        max_length=11,
        help_text="CPF do usuário.",
    )
    rf = serializers.CharField(
        max_length=50,
        help_text="Registro funcional do usuário.",
    )


class UsuarioConsultaSerializer(serializers.Serializer):
    """Valida os parâmetros utilizados na consulta de usuários."""

    usuario_id = serializers.CharField(
        required=False,
        help_text=(
            "ID interno do usuário no Keycloak. "
            "Não pode ser utilizado junto com cpf, rf ou email."
        ),
    )

    cpf = serializers.CharField(
        required=False,
        help_text=(
            "CPF do usuário. "
            "Não pode ser utilizado junto com usuario_id, rf ou email."
        ),
    )

    rf = serializers.CharField(
        required=False,
        help_text=(
            "Registro funcional do usuário. "
            "Não pode ser utilizado junto com usuario_id, cpf ou email."
        ),
    )

    email = serializers.EmailField(
        required=False,
        help_text=(
            "Endereço de e-mail exato do usuário. "
            "Não pode ser utilizado junto com usuario_id, cpf ou rf."
        ),
    )

    busca = serializers.CharField(
        required=False,
        help_text=(
            "Texto utilizado para pesquisa geral de usuários. "
            "Não pode ser utilizado junto com um identificador específico."
        ),
    )

    limite = serializers.IntegerField(
        required=False,
        min_value=1,
        max_value=1000,
        default=100,
        help_text=(
            "Quantidade máxima de usuários retornados. " "Valor padrão: 100."
        ),
    )

    def validate(
        self,
        attrs: dict[str, Any],
    ) -> dict[str, Any]:
        """Valida as combinações permitidas dos parâmetros de consulta.

        Apenas um identificador específico pode ser informado por consulta.
        O parâmetro ``busca`` também é exclusivo e não pode ser combinado
        com um identificador específico.

        Args:
            attrs: Dados recebidos após a validação individual dos campos.

        Returns:
            Dados validados e aceitos pelo serializer.

        Raises:
            serializers.ValidationError: Quando mais de um identificador
                é informado ou quando ``busca`` é combinado com um
                identificador específico.
        """
        criterios = (
            "usuario_id",
            "cpf",
            "rf",
            "email",
        )

        identificadores = [
            criterio
            for criterio in criterios
            if attrs.get(criterio) is not None
        ]

        if len(identificadores) > 1:
            raise serializers.ValidationError(
                {
                    "consulta": (
                        "Informe apenas um dos seguintes parâmetros: "
                        "usuario_id, cpf, rf ou email."
                    )
                }
            )

        if attrs.get("busca") and identificadores:
            raise serializers.ValidationError(
                {
                    "busca": (
                        "O parâmetro busca não pode ser utilizado "
                        "junto com um identificador específico."
                    )
                }
            )

        return attrs


class UsuarioAtualizarSerializer(serializers.Serializer):
    """Valida os dados opcionais para atualização de um usuário."""

    usuario = serializers.CharField(
        max_length=150,
        required=False,
        help_text="Novo nome de identificação do usuário.",
    )
    nome = serializers.CharField(
        max_length=150,
        required=False,
        help_text="Novo nome do usuário.",
    )
    sobrenome = serializers.CharField(
        max_length=150,
        required=False,
        allow_blank=True,
        help_text="Novo sobrenome do usuário.",
    )
    cpf = serializers.CharField(
        max_length=11,
        required=False,
        help_text="Novo CPF do usuário.",
    )
    rf = serializers.CharField(
        max_length=50,
        required=False,
        help_text="Novo registro funcional do usuário.",
    )
    habilitado = serializers.BooleanField(
        required=False,
        help_text="Define se o usuário permanecerá habilitado no Keycloak.",
    )


class UsuarioAlterarEmailSerializer(serializers.Serializer):
    """Valida o novo endereço de e-mail de um usuário."""

    email = serializers.EmailField(
        help_text="Novo endereço de e-mail do usuário.",
    )


class UsuarioAlterarSenhaSerializer(serializers.Serializer):
    """Valida a nova senha de um usuário."""

    senha = serializers.CharField(
        write_only=True,
        help_text="Nova senha do usuário (transporte HTTPS).",
    )


class UsuarioSerializer(serializers.Serializer):
    """Representa os dados de um usuário retornados pela API."""

    id = serializers.CharField()
    username = serializers.CharField(allow_null=True)
    firstName = serializers.CharField(allow_null=True)
    lastName = serializers.CharField(allow_null=True)
    email = serializers.EmailField(allow_null=True)
    enabled = serializers.BooleanField()
    emailVerified = serializers.BooleanField()
    cpf = serializers.CharField(allow_null=True)
    rf = serializers.CharField(allow_null=True)


class UsuarioCriadoSerializer(serializers.Serializer):
    """Representa a resposta retornada após a criação de um usuário."""

    id = serializers.CharField()


class UsuarioEmailSerializer(serializers.Serializer):
    """Representa o resultado da alteração e verificação do e-mail."""

    email_alterado = serializers.BooleanField()
    verificacao_enviada = serializers.BooleanField()


class UsuarioGrupoSerializer(serializers.Serializer):
    """Valida os dados para associação de um usuário a um grupo."""

    grupo_id = serializers.CharField(
        required=True,
        help_text="ID interno do grupo no Keycloak.",
    )


class UsuarioRealmRoleSerializer(serializers.Serializer):
    """Valida os dados para associação de uma Realm Role a um usuário."""

    nome_permissao = serializers.CharField(
        required=True,
        help_text="Nome da Realm Role no Keycloak.",
    )


class UsuarioClientRoleSerializer(serializers.Serializer):
    """Valida os dados para associação de uma Client Role a um usuário."""

    client_uuid = serializers.CharField(
        required=True,
        help_text="ID interno do cliente no Keycloak.",
    )
    nome_permissao = serializers.CharField(
        required=True,
        help_text="Nome da Client Role no Keycloak.",
    )
