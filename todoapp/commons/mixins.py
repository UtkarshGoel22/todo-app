from rest_framework import serializers


class SerializerToActionMapperMixin:
    """
    Mixin for mapping serializer to request actions. 
    """

    serializer_classes = NotImplemented

    def get_serializer_class(self) -> serializers.Serializer:
        """
        Method to get serializer class based on request action.

        Returns:
            serializers.Serializer: Serializer class based on request action.
        """

        return self.serializer_classes[self.action]
