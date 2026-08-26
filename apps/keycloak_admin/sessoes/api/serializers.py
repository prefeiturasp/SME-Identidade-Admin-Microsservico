"""Serializers da API administrativa de sessões."""

from rest_framework import serializers


class SessaoSerializer(serializers.Serializer):
    """Representa uma sessão ativa de um usuário."""

    id = serializers.CharField(
        allow_null=True,
        help_text="Identificador da sessão no Keycloak.",
    )
    usuario_id = serializers.CharField(
        allow_null=True,
        help_text="ID do usuário associado à sessão.",
    )
    usuario = serializers.CharField(
        allow_null=True,
        help_text="Nome do usuário associado à sessão.",
    )
    clientes = serializers.JSONField(
        default=dict,
        help_text="Clientes associados à sessão.",
    )
    endereco_ip = serializers.CharField(
        allow_null=True,
        help_text="Endereço IP associado à sessão.",
    )
    inicio = serializers.IntegerField(
        allow_null=True,
        help_text="Timestamp de início da sessão.",
    )
    ultimo_acesso = serializers.IntegerField(
        allow_null=True,
        help_text="Timestamp do último acesso à sessão.",
    )
