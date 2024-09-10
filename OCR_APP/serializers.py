from rest_framework import serializers


class PayloadSerializer(serializers.Serializer):
    library_number = serializers.CharField(max_length=100)
    code = serializers.CharField(max_length=100)
    plate_number = serializers.CharField(max_length=100, required=False, allow_blank=True)

class OCRSerializer(serializers.Serializer):
    image_path = serializers.CharField(max_length=255)
    payload = PayloadSerializer()