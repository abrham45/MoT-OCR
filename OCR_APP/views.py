from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
import pytesseract
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
from PIL import Image
import os
from rest_framework import status

class OCRCheckView(APIView):
    parser_classes = [JSONParser]

    def post(self, request, *args, **kwargs):
        serializer = OCRSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        image_path = serializer.validated_data['image_path']
        user_number = serializer.validated_data['library_number'].upper()

        try:
            if not os.path.isfile(image_path) or not image_path.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                raise IOError("Invalid image path or unsupported format")
            img = Image.open(image_path)
        except (IOError, OSError) as e:
            return Response({"error": f"Invalid image: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        text = pytesseract.image_to_string(img, lang='amh')
        print(text)
        important_components = ["COMPONENT1", "COMPONENT2"]
        all_components_found = all(component in text for component in important_components)
        number_exists = user_number in text

        response_data = {
            "components_found": all_components_found,
            "number_exists": number_exists
        }

        return Response(response_data, status=status.HTTP_200_OK)

class OCRSerializer(serializers.Serializer):
    image_path = serializers.CharField(max_length=255)
    library_number = serializers.CharField(max_length=50)

    def validate_image_path(self, value):
        # Additional validation for image existence and format (optional)
        # ... (implementation as shown above in OCRCheckView)
        return value