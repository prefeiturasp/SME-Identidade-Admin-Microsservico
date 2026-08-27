"""Serializers da API administrativa do Keycloak."""

from rest_framework import serializers


class ErroResponseSerializer(serializers.Serializer):
    """Representa uma resposta de erro da API."""

    codigo = serializers.CharField(
        help_text="Código que identifica o tipo do erro.",
    )
    mensagem = serializers.CharField(
        help_text="Descrição do erro.",
    )


class MensagemResponseSerializer(serializers.Serializer):
    """Representa uma resposta de sucesso com uma mensagem."""

    mensagem = serializers.CharField()
