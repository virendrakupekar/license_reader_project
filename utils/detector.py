import easyocr
import cv2
import numpy as np

# Initialize reader only once
reader = easyocr.Reader(['en'], gpu=False)

def detect_license_plate(image_path):
    img = cv2.imread(image_path)
    if img is None:
        raise FileNotFoundError(f"Image not found: {image_path}")

    # Convert to grayscale for better OCR
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Run EasyOCR
    results = reader.readtext(gray)

    plate_number = "Not Found"
    plate_bbox = None

    for (bbox, text, confidence) in results:
        text_clean = text.strip().replace(" ", "")
        if 6 <= len(text_clean) <= 12 and confidence > 0.4:
            if any(c.isalpha() for c in text_clean) and any(c.isdigit() for c in text_clean):
                plate_number = text_clean
                plate_bbox = bbox
                break

    # Annotate image
    annotated_img = img.copy()
    if plate_bbox:
        pts = [tuple(map(int, point)) for point in plate_bbox]
        cv2.polylines(annotated_img, [np.array(pts)], isClosed=True, color=(0, 255, 0), thickness=2)
        cv2.putText(annotated_img, plate_number, (pts[0][0], pts[0][1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

    return plate_number, annotated_img, "Vehicle"

