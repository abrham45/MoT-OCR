import pytesseract
import os
from rest_framework.views import APIView
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework import status
from fuzzywuzzy import fuzz
from PIL import Image
from .serializers import OCRSerializer  # Assuming OCRSerializer is in the same directory
import requests
from io import BytesIO

pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'


class OCRCheckView(APIView):
    parser_classes = [JSONParser]

    def post(self, request, *args, **kwargs):
        serializer = OCRSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        image_path_or_url = serializer.validated_data['image_path']
        user_number = serializer.validated_data['library_number'].upper()

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
            # Existing logic for local file paths
            if not self.is_valid_image(image_path_or_url):
                return Response({"error": "Invalid image path or unsupported format"},
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                img = Image.open(image_path_or_url)
            except (IOError, OSError) as e:
                return Response({"error": f"Invalid image: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        # Perform OSD for orientation detection
        # osd_data = pytesseract.image_to_osd(img)
        # orientation = int(osd_data.split('\n')[1].split(':')[1])

        # # Rotate image based on detected orientation (if needed)
        # if orientation not in (0, -1):  # Check for valid orientations
        #     angle = (360 - orientation) % 360  # Calculate rotation angle
        #     img = img.rotate(angle, expand=True)  # Rotate and expand to avoid cropping

        text = self.perform_ocr(img)

        response_data = self.analyze_text(text, user_number)

        return Response(response_data, status=status.HTTP_200_OK)

    @staticmethod
    def is_valid_image(image_path):
        return os.path.isfile(image_path) and image_path.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))

    @staticmethod
    def perform_ocr(img):
        # Ensure that the Amharic language is supported in your Tesseract installation
        config = r'--oem 3 --psm 5 -l amh+eng'
        return pytesseract.image_to_string(img, config=config)

    @staticmethod
    def analyze_text(text, user_number):
        important_components = [
            "ዜግነት",  # Chassis Number
            "ክልል",
            "የሰሌዳ ቁጥር",  # Plate Number
            "የተሽከርካሪው ዓይነት"  # Type of Vehicle
        ]
        print(text)
        components_found = []
        number_exists = False
        components_not_found = []

        for component in important_components:
            # Using fuzzy matching to find the best match for each component in the text
            match_percentage = fuzz.partial_ratio(component, text)
            print(match_percentage)
            if match_percentage >= 80:
                components_found.append(component)
            else:
                components_not_found.append(component)

        at_least_two_found = len(components_found) >= 2
        if at_least_two_found:
            match_percentage_two = fuzz.partial_ratio(user_number, text)
            if match_percentage_two >= 30:
                return True
            else:
                return False
           

        return {
            
            "at_least_two_components_found": at_least_two_found,
            "components_found": components_found,  # List of components found with fuzzy matching
            "components_not_found": components_not_found,
            "number_exists": number_exists
        }

