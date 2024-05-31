from rest_framework import serializers

class OCRSerializer(serializers.Serializer):
    image_path = serializers.CharField(max_length=255)
    library_number = serializers.CharField(max_length=50)