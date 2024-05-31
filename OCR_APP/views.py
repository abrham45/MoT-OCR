from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers
import pytesseract
from PIL import Image
import os

class OCRCheckView(APIView):
    parser_classes = [JSONParser]

    def post(self, request, *args, **kwargs):
        """
        Performs OCR on an image, checking for specific components and user-entered number.

        Expected request data:
            - image_path (str): Path to the image file.
            - library_number (str): The number the user expects to find in the image.
        """

        serializer = OCRSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)  # Raise validation errors

        # Extract validated data
        image_path = serializer.validated_data['image_path']
        user_number = serializer.validated_data['library_number'].upper()

        # Validate image existence and format (optional for enhanced robustness)
        try:
            # Check if file exists and has a supported image extension
            if not os.path.isfile(image_path) or not image_path.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                raise IOError("Invalid image path or unsupported format")
            img = Image.open(image_path)  # Attempt to open the image
        except (IOError, OSError) as e:
            return Response({"error": f"Invalid image: {str(e)}"}, status=400)

        # Perform OCR on the image
        text = pytesseract.image_to_string(img).upper()

        # Check for important components
        important_components = ["COMPONENT1", "COMPONENT2"]  # Replace with actual values
        all_components_found = all(component in text for component in important_components)

        # Check if the user-entered number exists
        number_exists = user_number in text

        # Prepare response
        response_data = {
            "components_found": all_components_found,
            "number_exists": number_exists
        }

class OCRSerializer(serializers.Serializer):
    image_path = serializers.CharField(max_length=255)
    library_number = serializers.CharField(max_length=50)

    def validate_image_path(self, value):
        # Additional validation for image existence and format (optional)
        # ... (implementation as shown above in OCRCheckView)
        return value