from rest_framework import serializers


class QuestionSerializer(serializers.Serializer):
    question = serializers.CharField()


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()


class AnswerSerializer(serializers.Serializer):
    answer = serializers.CharField()
    sources = serializers.ListField(child=serializers.CharField())


class MessageSerializer(serializers.Serializer):
    detail = serializers.CharField() 