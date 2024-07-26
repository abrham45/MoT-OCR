import cv2
import numpy as np

def rotate_image(image_path_or_url):
    # Load the image using OpenCV
    img = cv2.imread(image_path_or_url)
    
    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Detect edges in the image
    edges = cv2.Canny(gray, 50, 200)
    
    # Find lines in the edge-detected image
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=100, minLineLength=100, maxLineGap=10)
    
    # Calculate the average slope of the lines to estimate the skew angle
    angles = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        angle = np.arctan2(y2 - y1, x2 - x1) * 180 / np.pi
        angles.append(angle)
    
    # Calculate the average angle
    avg_angle = np.mean(angles)
    
    # Rotate the image based on the calculated angle
    (h, w) = img.shape[:2]
    center = (w / 2, h / 2)
    M = cv2.getRotationMatrix2D(center, avg_angle, 1.0)
    rotated = cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    
    return rotated
