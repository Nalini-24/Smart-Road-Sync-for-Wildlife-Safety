import cv2
import numpy as np

class YOLOTinyDetector:
    def __init__(self, config):
        self.config = config
        self.net = cv2.dnn.readNet(
            self.config['models']['yolo_tiny']['weights'],
            self.config['models']['yolo_tiny']['config']
        )
        with open(self.config['models']['yolo_tiny']['classes'], 'r') as f:
            self.classes = [line.strip() for line in f.readlines()]

        self.output_layers = self.net.getUnconnectedOutLayersNames()
        self.conf_threshold = self.config['models']['yolo_tiny']['confidence_threshold']
        self.nms_threshold = self.config['models']['yolo_tiny']['nms_threshold']
        self.animal_classes = ['dog', 'cat', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe']

        self.frame_buffer = []
        self.buffer_size = 3  # smooth detections across frames

    def detect(self, frame, return_detections=True):
        # Optional buffering to smooth detections
        self.frame_buffer.append(frame)
        if len(self.frame_buffer) > self.buffer_size:
            self.frame_buffer.pop(0)

        all_detections = []
        for buffered_frame in self.frame_buffer:
            all_detections.extend(self._detect_single_frame(buffered_frame))

        final_detections = self._remove_duplicates(all_detections)

        # 🔎 Debug: print how many detections found
        print(f"[YOLO DEBUG] Detections found: {len(final_detections)}")
        for det in final_detections:
            print(f"  -> {det}")

        # Draw bounding boxes on frame
        for det in final_detections:
            x1, y1, x2, y2 = det['bbox']
            color = (0, 255, 0)
            label = f"{det['class']} ({det['confidence']:.2f})"
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        if return_detections:
            return frame, final_detections
        else:
            return frame

    def _detect_single_frame(self, frame):
        height, width = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True, crop=False)
        self.net.setInput(blob)
        layer_outputs = self.net.forward(self.output_layers)

        boxes, confidences, class_ids = [], [], []

        for output in layer_outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > self.conf_threshold:
                    center_x, center_y, w, h = (detection[:4] * np.array([width, height, width, height])).astype('int')
                    x = int(center_x - w/2)
                    y = int(center_y - h/2)
                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        indices = cv2.dnn.NMSBoxes(boxes, confidences, self.conf_threshold, self.nms_threshold)

        animal_detections = []
        for i in indices:
            i = i[0] if isinstance(i, (tuple, list, np.ndarray)) else i
            x, y, w, h = boxes[i]
            class_name = self.classes[class_ids[i]]
            if class_name in self.animal_classes:
                animal_detections.append({
                    'bbox': [x, y, x+w, y+h],
                    'class': class_name,
                    'confidence': confidences[i]
                })

        # 🔎 Debug: raw YOLO detections before filtering
        print(f"[YOLO DEBUG] Frame raw detections: {len(animal_detections)}")

        return animal_detections

    def _remove_duplicates(self, detections):
        final_detections = []
        for det in detections:
            if not any(self._iou(det['bbox'], d['bbox']) > 0.5 for d in final_detections):
                final_detections.append(det)
        return final_detections

    def _iou(self, box1, box2):
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])

        intersection = max(0, x2 - x1) * max(0, y2 - y1)
        area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
        area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])
        union = area1 + area2 - intersection

        return intersection / union if union > 0 else 0


# Create a singleton detector instance (optional)
yolo_detector = None
def detect(frame, return_detections=True):
    global yolo_detector
    if yolo_detector is None:
        import yaml
        with open('vehicle_animal_detection/config/config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        yolo_detector = YOLOTinyDetector(config)
    return yolo_detector.detect(frame, return_detections)

