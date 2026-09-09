"""Serializers da API administrativa de clientes."""

from rest_framework import serializers


class ClientCriarSerializer(serializers.Serializer):
    """Valida os dados para criação de um cliente."""

    client_id = serializers.CharField(
        max_length=255,
        help_text="Identificador público do cliente.",
    )
    nome = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        help_text="Nome de apresentação do cliente.",
    )
    descricao = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        help_text="Descrição do cliente.",
    )
    habilitado = serializers.BooleanField(
        required=False,
        default=True,
        help_text="Define se o cliente será habilitado.",
    )
    client_publico = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Define se o cliente será público.",
    )
    protocolo = serializers.CharField(
        required=False,
        default="openid-connect",
        help_text="Protocolo utilizado pelo cliente.",
    )
    redirect_uris = serializers.ListField(
        child=serializers.URLField(),
        required=False,
        default=list,
        help_text="URIs autorizadas para redirecionamento.",
    )
    web_origins = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list,
        help_text="Origens web autorizadas.",
    )
    atributos = serializers.DictField(
        required=False,
        default=dict,
        help_text="Atributos adicionais do cliente.",
    )


class ClientConsultaSerializer(serializers.Serializer):
    """Define os parâmetros para consulta de clientes."""

    client_uuid = serializers.UUIDField(
        required=False,
        allow_null=True,
        help_text=(
            "UUID interno do cliente no Keycloak. "
            "Quando informado, consulta somente esse cliente."
        ),
    )


class ClientAtualizarSerializer(serializers.Serializer):
    """Valida os dados para atualização de um cliente."""

    client_id = serializers.CharField(
        max_length=255,
        required=False,
        help_text="Novo identificador público do client.",
    )
    nome = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        help_text="Novo nome de apresentação.",
    )
    descricao = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True,
        help_text="Descrição do cliente.",
    )
    habilitado = serializers.BooleanField(
        required=False,
        help_text="Define se o cliente ficará habilitado.",
    )
    client_publico = serializers.BooleanField(
        required=False,
        help_text="Define se o cliente será público.",
    )
    protocolo = serializers.CharField(
        required=False,
        help_text="Novo protocolo do cliente.",
    )
    redirect_uris = serializers.ListField(
        child=serializers.URLField(),
        required=False,
        help_text="Novas URIs de redirecionamento.",
    )
    web_origins = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="Novas origens web autorizadas.",
    )
    atributos = serializers.DictField(
        required=False,
        help_text="Novos atributos do cliente.",
    )


class ClientSerializer(serializers.Serializer):
    """Representa um cliente na resposta da API."""

    id = serializers.CharField()
    client_id = serializers.CharField(allow_null=True)
    nome = serializers.CharField(allow_null=True)
    habilitado = serializers.BooleanField()
    client_publico = serializers.BooleanField()
    protocolo = serializers.CharField()
    redirect_uris = serializers.ListField(
        child=serializers.CharField(),
    )
    web_origins = serializers.ListField(
        child=serializers.CharField(),
    )
    atributos = serializers.DictField()


class ClientCriadoSerializer(serializers.Serializer):
    """Representa a resposta da criação de um cliente."""

    id = serializers.CharField()
