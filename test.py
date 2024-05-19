import numpy as np
import cv2
import imutils
import pytesseract
import time
from pymongo import MongoClient
from datetime import datetime

# Setup for pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# MongoDB setup
client = MongoClient(
    "mongodb+srv://a:a@cluster0.1cih6pg.mongodb.net/")
db = client['car-number']
collection = db['number-plates']


def preprocess_image(image):
    # Convert frame to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply a bilateral filter to reduce noise while keeping edges sharp
    gray = cv2.bilateralFilter(gray, 11, 17, 17)

    # Apply edge detection
    edged = cv2.Canny(gray, 30, 200)

    # Apply morphological operations to close gaps in the edges
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    edged = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)

    return gray, edged


def find_license_plate_contour(edged):
    # Find contours in the edged image
    cnts, _ = cv2.findContours(
        edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Sort the contours based on contour area, keep only the largest ones
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)[:10]

    # Loop over the contours to find the one that resembles a license plate
    for c in cnts:
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.018 * peri, True)
        if len(approx) == 4:
            return approx
    return None


def is_valid_license_plate(text):
    # Implement simple validation for detected license plate text
    return len(text) > 5 and len(text) < 15 and any(char.isdigit() for char in text)


def save_to_mongo(license_plate):
    document = {
        "license_plate": license_plate,
        "timestamp": datetime.now()
    }
    collection.insert_one(document)
    print(f"Saved to MongoDB: {document}")


def main():
    # Start video capture from the default camera
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Unable to open camera.")
        return

    try:
        while True:
            # Capture frame-by-frame
            ret, frame = cap.read()
            if not ret:
                print("Error: Unable to fetch frame.")
                break

            # Resize frame for consistent processing speed
            frame = imutils.resize(frame, width=800)

            # Preprocess the frame
            gray, edged = preprocess_image(frame)

            # Find the license plate contour
            NumberPlateCnt = find_license_plate_contour(edged)

            if NumberPlateCnt is not None:
                # Masking other parts, only showing number plate
                mask = np.zeros(gray.shape, np.uint8)
                new_image = cv2.drawContours(
                    mask, [NumberPlateCnt], 0, 255, -1)
                new_image = cv2.bitwise_and(frame, frame, mask=mask)

                # Apply further preprocessing on the extracted plate region
                new_image_gray = cv2.cvtColor(new_image, cv2.COLOR_BGR2GRAY)
                new_image_gray = cv2.bilateralFilter(
                    new_image_gray, 11, 17, 17)
                new_image_thresh = cv2.adaptiveThreshold(
                    new_image_gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

                # Display the license plate region
                cv2.imshow("License Plate", new_image_thresh)

                # Configuration for tesseract
                config = '-l eng --oem 3 --psm 6'
                text = pytesseract.image_to_string(
                    new_image_thresh, config=config)
                text = text.strip()
                if is_valid_license_plate(text):
                    print("Detected License Plate Number:", text)
                    save_to_mongo(text)
                    time.sleep(5)  # Wait for 5 seconds before continuing

            # Display the resulting frame
            cv2.imshow("Frame", frame)

            # Press 'q' to quit the program
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        # When everything done, release the capture
        cap.release()
        cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
