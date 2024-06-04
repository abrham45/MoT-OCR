import pytesseract
import os
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import status
from fuzzywuzzy import fuzz
from PIL import Image
from .serializers import OCRSerializer  # Assuming OCRSerializer is in the same directory

class OCRCheckView(APIView):
    parser_classes = [JSONParser]

    def post(self, request, *args, **kwargs):
        serializer = OCRSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        image_path = serializer.validated_data['image_path']
        user_number = serializer.validated_data['library_number'].upper()

        if not self.is_valid_image(image_path):
            return Response({"error": "Invalid image path or unsupported format"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            img = Image.open(image_path)
        except (IOError, OSError) as e:
            return Response({"error": f"Invalid image: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        text = self.perform_ocr(img)
        print(text)
        response_data = self.analyze_text(text, user_number)

        return Response(response_data, status=status.HTTP_200_OK)

    @staticmethod
    def is_valid_image(image_path):
        return os.path.isfile(image_path) and image_path.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))

    @staticmethod
    def perform_ocr(img):
        # Ensure that the Amharic language is supported in your Tesseract installation
        config = '--psm 1 -l eng+amh'
        return pytesseract.image_to_string(img, config=config)

    @staticmethod
    def analyze_text(text, user_number):
        important_components = [
            "የሻንሲ ቁጥር",  # Chassis Number
            "Motor Number",
            "የሰሌዳ ቁጥር",  # Plate Number
            "የተሽከርካሪው ዓይነት"  # Type of Vehicle
        ]
        components_found = []

        for component in important_components:
            # Using fuzzy matching to find the best match for each component in the text
            match_percentage = fuzz.partial_ratio(component, text)
            if match_percentage >= 90:
                components_found.append(component)

        at_least_two_found = len(components_found) >= 2
        number_exists = user_number in text  # Assuming exact match for user_number

        return {
            "at_least_two_components_found": at_least_two_found,
            "components_found": components_found,  # List of components found with fuzzy matching
            "number_exists": number_exists
        }

