# Smart Road Sync for Wildlife Safety 🦌🚦

## 1. Overview
Smart Road Sync for Wildlife Safety is a machine learning–based road safety system designed to detect animals on roads and alert drivers in advance. The project integrates computer vision with an Arduino-based hardware system to simulate a smart roadside warning mechanism.

The system processes road video footage, detects animals using a YOLOv3-Tiny model, and displays detection alerts on a 16×2 LCD connected to an Arduino Uno.

---

## 2. Problem Statement
Roads passing through forest and wildlife regions frequently experience animal crossings, resulting in accidents and loss of wildlife. Existing warning systems are static and ineffective.

This project proposes a **smart, automated detection system** that dynamically detects animals and provides timely alerts.

---

## 3. System Workflow
1. User uploads a road video through the GUI
2. Video frames are processed using YOLOv3-Tiny
3. Detected animals are identified and labeled
4. Detection results are sent via serial communication
5. Arduino displays alerts on an LCD screen

---

## 4. Project Structure
Animal-Recognition-App-for-Self-Driving-Cars/
│
├── vehicle_animal_detection/
│ ├── config/
│ │ └── config.yaml
│ │
│ ├── src/
│ │ ├── detection/
│ │ │ └── yolo_detector.py
│ │ │
│ │ ├── gui/
│ │ │ └── main_window.py
│ │ │
│ │ └── init.py
│ │
│ └── init.py
│
├── arduino/
│ └── lcd_animal_display.ino
│
├── assets/
│ └── images/
│ ├── elephant.png
│ └── Animal_detected_elephant.jpg
│
├── requirements.txt
├── README.md
└── LICENSE


---

## 5. Technologies Used

| Category              | Tools / Technologies              |
|----------------------|----------------------------------|
| Programming Language | Python                            |
| Deep Learning Model  | YOLOv3-Tiny (COCO pre-trained)   |
| Computer Vision      | OpenCV                            |
| GUI Framework        | PyQt5                             |
| Hardware             | Arduino Uno, 16×2 LCD             |
| Communication        | Serial (USB, 9600 baud)           |

---

## 6. Project Outputs

### 6.1 GUI Output (Animal Detection)
![GUI Animal Detection](assets/images/gui_animal_detected.png)

### 6.2 Arduino LCD Output
![Arduino LCD Output](assets/images/arduino_lcd_animal.jpg)

---

## 7. How to Run the Project

### Step 1: Clone the Repository
```bash
git clone <your-repository-url>
cd Animal-Recognition-App-for-Self-Driving-Cars

Step 2: Install Dependencies
pip install -r requirements.txt

Step 3: Arduino Setup
--Open arduino/lcd_animal_display.ino in Arduino IDE

--Connect Arduino Uno via USB

--Set baud rate to 9600

--Upload the code

--Note the COM port and update it in config.yaml

Step 4: Run the Application
python -m vehicle_animal_detection.src.gui.main_window

Step 5: Use the System
--Click Upload Video

--Select a road video file

--Click Process Video

--Observe:

    Bounding boxes and labels in the GUI

    Animal name / NO ANIMAL on LCD

---

###8. Key Features

1.Real-time animal detection from video input

2.Lightweight YOLOv3-Tiny model for fast inference

3.Smooth detection using frame aggregation

4.Reliable Arduino serial communication

5.Clear LCD-based visual alerts

---

###9. Limitations

1.Uses pre-recorded video instead of live camera feed

2.Alerts are displayed only on LCD

3.Detection accuracy depends on video quality and lighting

---

###10. Future Enhancements

1.Live roadside camera integration

2.Distance-based animal detection alerts

3.Integration with traffic signals or warning lights

4.Mobile notification system

5.Cloud-based analytics and logging

---

###11. Conclusion

Smart Road Sync for Wildlife Safety demonstrates how machine learning and embedded systems can be combined to address real-world safety challenges. The project highlights the potential of AI-driven solutions in reducing wildlife–vehicle collisions and improving road safety.
