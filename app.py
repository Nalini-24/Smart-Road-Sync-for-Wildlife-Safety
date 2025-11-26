import cv2
from detection.yolo_detector import detect

# Open webcam (or video file)
cap = cv2.VideoCapture(0)  # Replace 0 with video path if needed

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Run YOLO detection
    frame = detect(frame)

    # Show annotated frame
    cv2.imshow("Animal Detection", frame)

    # Exit on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
