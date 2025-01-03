from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import status
from PIL import Image
from io import BytesIO
import requests
import os
import pytesseract
from fuzzywuzzy import fuzz
from .serializers import OCRSerializer
from .important_components import get_important_components  # Import the function

# Set the Tesseract command path
pytesseract.pytesseract.tesseract_cmd =  r'C:\Program Files\Tesseract-OCR\tesseract.exe'
class OCRCheckView(APIView):
    parser_classes = [JSONParser]

    def post(self, request, *args, **kwargs):
        serializer = OCRSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        image_path_or_url = serializer.validated_data['image_path']
        payload = serializer.validated_data['payload']
        user_number = payload['library_number'].upper()
        code = payload['code'].upper()

        # Check if the input is a URL
        if image_path_or_url.startswith(('http://', 'https://')):
            try:
                response = requests.get(image_path_or_url)
                response.raise_for_status()  # Raise exception if invalid response
                img = Image.open(BytesIO(response.content))
            except Exception as e:
                return Response({"error": f"Failed to download or open image from URL: {str(e)}"},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            # Validate local file paths
            if not self.is_valid_image(image_path_or_url):
                return Response({"error": "Invalid image path or unsupported format"},
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                img = Image.open(image_path_or_url)
            except (IOError, OSError) as e:
                return Response({"error": f"Invalid image: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            text = self.perform_ocr(img)
        except Exception as e:
            return Response({"error": f"Failed to perform OCR: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        response_data = self.analyze_text(text, user_number, code)

        return Response(response_data, status=status.HTTP_200_OK)

    @staticmethod
    def is_valid_image(image_path):
        return os.path.isfile(image_path) and image_path.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))

    @staticmethod
    def perform_ocr(img):
        # Configure Tesseract to use only Amharic language
        config = r'--oem 3 --psm 5 -l amh'
        return pytesseract.image_to_string(img, config=config)

    @staticmethod
    def analyze_text(text, user_number, code):
        # Get important components based on the code
        important_components = get_important_components(code)

        components_found = []
        components_not_found = []

        for component in important_components:
            # Use fuzzy matching for Amharic text
            match_percentage = fuzz.partial_ratio(component, text)
            if match_percentage >= 65:
                components_found.append(component)
            else:
                components_not_found.append(component)

        at_least_two_found = len(components_found) >= 2
        match_percentage_two = fuzz.partial_ratio(user_number, text)

        response_data = {
                    "at_least_two_components_found": at_least_two_found,
                    "components_found": important_components if at_least_two_found else [],
                    "components_not_found": [] if at_least_two_found else components_not_found,
                    "number_exists": at_least_two_found and match_percentage_two >= 20,
                }

        return response_data

