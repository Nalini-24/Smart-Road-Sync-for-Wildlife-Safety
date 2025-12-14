import sys
import cv2
import numpy as np
import yaml
import time

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QLabel, QProgressBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap

from ..detection.yolo_detector import detect
from ..classification.classifier import Classifier

# Try to import pyserial gracefully
try:
    import serial
except Exception:
    serial = None


# --------------------------- Detection Smoother ---------------------------
class DetectionSmoother:
    def __init__(self, smoothing_frames=5):
        self.smoothing_frames = smoothing_frames
        self.detection_history = []

    def update(self, current_detections):
        self.detection_history.append(current_detections)
        if len(self.detection_history) > self.smoothing_frames:
            self.detection_history.pop(0)

    def get_smoothed_detections(self):
        if not self.detection_history:
            return []
        smoothed_detections = []
        all_detections = [det for frame_dets in self.detection_history for det in frame_dets]
        for det in all_detections:
            similar_dets = [d for d in all_detections if self.iou(det['bbox'], d['bbox']) > 0.3]
            if len(similar_dets) >= 2:
                avg_bbox = self.average_bbox([d['bbox'] for d in similar_dets])
                avg_conf = sum(d['confidence'] for d in similar_dets) / len(similar_dets)
                smoothed_detections.append({
                    'bbox': avg_bbox,
                    'class': det.get('class', None),
                    'confidence': avg_conf
                })
        return smoothed_detections

    @staticmethod
    def average_bbox(bboxes):
        avg_bbox = [sum(box[i] for box in bboxes) / len(bboxes) for i in range(4)]
        return [int(coord) for coord in avg_bbox]

    @staticmethod
    def iou(box1, box2):
        x1 = max(box1[0], box2[0])
        y1 = max(box1[1], box2[1])
        x2 = min(box1[2], box2[2])
        y2 = min(box1[3], box2[3])
        intersection = max(0, x2 - x1) * max(0, y2 - y1)
        area1 = max(0, (box1[2] - box1[0])) * max(0, (box1[3] - box1[1]))
        area2 = max(0, (box2[2] - box2[0])) * max(0, (box2[3] - box2[1]))
        union = area1 + area2 - intersection
        return intersection / union if union > 0 else 0


# --------------------------- Processing Thread ---------------------------
class ProcessingThread(QThread):
    progress_signal = pyqtSignal(int)
    frame_processed_signal = pyqtSignal(np.ndarray)
    finished_signal = pyqtSignal(list)
    error_signal = pyqtSignal(str)
    alert_signal = pyqtSignal(str)

    def __init__(self, config, video_path, config_path):
        super().__init__()
        self.config = config
        self.video_path = video_path
        self.config_path = config_path
        #self.classifier = Classifier(self.config_path)
        self.detection_smoother = DetectionSmoother()

        self.last_state = None
        self.last_species = None
        self.arduino = None

        self.cooldown = 0   # persistence counter

        serial_cfg = self.config.get('serial', {}) if isinstance(self.config, dict) else {}
        if serial_cfg.get('enabled', False):
            if serial is None:
                print("[WARNING] pyserial not installed.")
            else:
                port = serial_cfg.get('port', None)
                baud = serial_cfg.get('baudrate', 9600)
                if port:
                    try:
                        self.arduino = serial.Serial(port=port, baudrate=baud, timeout=1)
                        time.sleep(2)
                        print(f"[INFO] Arduino connected on {port} @ {baud}")
                    except Exception as e:
                        print(f"[WARNING] Could not connect to Arduino: {e}")
                        self.arduino = None

    def send_to_arduino(self, value):
        if self.arduino:
            try:
                self.arduino.write((value + "\n").encode())
                print(f"[SERIAL SENT] {value}")
            except Exception as e:
                print(f"[ERROR] Failed to send: {e}")

    def send_alert(self, state):
        if state != self.last_state:
            self.send_to_arduino(state)
            self.alert_signal.emit(state)
            self.last_state = state

    def run(self):
        cap = cv2.VideoCapture(self.video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) if cap.isOpened() else 0
        processed_frames = []

        if total_frames == 0:
            self.error_signal.emit("Video could not be opened or contains no frames.")
            self.finished_signal.emit(processed_frames)
            return

        for i in range(0, total_frames, self.config['performance']['frame_skip']):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.resize(frame, tuple(self.config['performance']['target_resolution']))
            frame, detections = detect(frame, return_detections=True)
            self.detection_smoother.update(detections)
            smoothed_detections = self.detection_smoother.get_smoothed_detections()

            detected = False
            species = None

            for detection in smoothed_detections:
                x1, y1, x2, y2 = map(int, detection['bbox'])
                h, w = frame.shape[:2]
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(w - 1, x2), min(h - 1, y2)
                if x2 <= x1 or y2 <= y1:
                    continue

                # YOLO already gives class → no classifier needed
                detected = True
                species = detection['class'].upper()

                # Draw bounding box & label (confidence directly from YOLO)
                label = f"{species}"
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                break  # only use first detection

   

            # --------------- UPDATED SERIAL LOGIC (LCD SAFE) ---------------
            # ---------------------- RELIABLE SERIAL LOGIC ----------------------
            # If detection found, update species immediately
            # --------------- UPDATED SERIAL LOGIC (LCD SAFE) ---------------
            # ---------------------- RELIABLE SERIAL LOGIC ----------------------
            # If detection found, update species immediately
            if detected:
                msg = species
            else:
                msg = "NONE"

            # Always send message if different OR if enough time passed
            current_time = time.time()

            # Send only if changed AND at least 1 second passed
            # Send ONLY when YOLO state changes
            if msg != self.last_state:
                self.send_alert(msg)
                self.last_state = msg

            # --------------------------------------------------------------

            processed_frames.append(frame)
            self.frame_processed_signal.emit(frame)

            try:
                progress_value = int((i + 1) / total_frames * 100)
            except:
                progress_value = 0
            self.progress_signal.emit(progress_value)

        cap.release()
        if self.arduino:
            try:
                self.arduino.close()
            except:
                pass

        self.finished_signal.emit(processed_frames)


# --------------------------- GUI Main Window ---------------------------
class MainWindow(QMainWindow):
    def __init__(self, config_path, parent=None):
        super().__init__(parent)
        self.config_path = config_path

        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        self.setWindowTitle(self.config['gui']['window_title'])
        self.setGeometry(
            100, 100,
            self.config['gui']['window_size']['width'],
            self.config['gui']['window_size']['height']
        )

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.video_label)

        self.load_button = QPushButton("Upload Video")
        self.process_button = QPushButton("Process Video")
        self.play_pause_button = QPushButton("Play")

        self.process_button.setEnabled(False)
        self.play_pause_button.setEnabled(False)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.load_button)
        btn_layout.addWidget(self.process_button)
        btn_layout.addWidget(self.play_pause_button)
        self.main_layout.addLayout(btn_layout)

        self.progress_bar = QProgressBar()
        self.main_layout.addWidget(self.progress_bar)

        self.load_button.clicked.connect(self.load_video)
        self.process_button.clicked.connect(self.process_video)
        self.play_pause_button.clicked.connect(self.play_pause_video)

        self.video_path = None
        self.processed_frames = None
        self.processing_thread = None
        self.video_playing = False

    def load_video(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Video", "", "Video Files (*.mp4 *.avi)")
        if file_name:
            self.video_path = file_name
            self.process_button.setEnabled(True)

    def process_video(self):
        if self.video_path:
            self.processing_thread = ProcessingThread(self.config, self.video_path, self.config_path)
            self.processing_thread.progress_signal.connect(self.update_progress)
            self.processing_thread.frame_processed_signal.connect(self.update_image)
            self.processing_thread.finished_signal.connect(self.processing_finished)
            self.processing_thread.alert_signal.connect(self.show_alert)
            self.processing_thread.start()
            self.process_button.setEnabled(False)
            self.load_button.setEnabled(False)

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def update_image(self, cv_img):
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_img = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_img).scaled(
            self.video_label.width(), self.video_label.height(), Qt.KeepAspectRatio
        )
        self.video_label.setPixmap(pixmap)

    def processing_finished(self, processed_frames):
        self.processed_frames = processed_frames
        self.play_pause_button.setEnabled(True)

    def play_pause_video(self):
        if not self.video_playing:
            if self.processed_frames:
                self.video_playing = True
                self.play_pause_button.setText("Pause")
                for frame in self.processed_frames:
                    self.update_image(frame)
            else:
                self.video_playing = False
                self.play_pause_button.setText("Play")

    def show_alert(self, message: str):
        print("[ALERT]", message)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow('vehicle_animal_detection/config/config.yaml')
    main_window.show()
    sys.exit(app.exec_())
