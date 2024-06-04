import cv2
import numpy as np
from PIL import Image

class PreprocessImage:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)

    def apply_gaussian_blur(self, kernel_size=(5, 5)):
        self.image = cv2.GaussianBlur(self.image, kernel_size, 0)
        return self

    def apply_threshold(self):
        _, self.image = cv2.threshold(self.image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return self

    def apply_dilation_and_erosion(self, kernel_size=(1, 1), iterations=1):
        kernel = np.ones(kernel_size, np.uint8)
        self.image = cv2.dilate(self.image, kernel, iterations=iterations)
        self.image = cv2.erode(self.image, kernel, iterations=iterations)
        return self

    def resize_image(self, scale_factor=2):
        self.image = cv2.resize(self.image, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_LINEAR)
        return self

    def invert_image(self):
        self.image = cv2.bitwise_not(self.image)
        return self

    def get_preprocessed_image(self):
        return self.image

    def get_pil_image(self):
        return Image.fromarray(self.image)