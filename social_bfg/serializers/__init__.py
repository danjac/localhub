# Django Rest Framework
from rest_framework import serializers


class GenericObjectSerializer(serializers.Serializer):
    """This probably should be somewhere else as we can use it for
    other things e.g. comments, flags etc."""

    id = serializers.IntegerField()
    title = serializers.SerializerMethodField()
    object_type = serializers.SerializerMethodField()

    def get_object_type(self, obj):
        return obj._meta.model_name

    def get_title(self, obj):
        return str(obj)
