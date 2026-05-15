import cv2
import os
import time

from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QGridLayout
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QTimer
from detection.detector import WasteDetector
from detection.categories import CATEGORY_MAP
from database.db_manager import DatabaseManager
from ui.cards import KPICard
from ui.charts import StatsCanvas
from utils.image_utils import convert_cv_qt

class WasteApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(
            "Medical Waste Monitoring Dashboard"
        )
        self.setGeometry(100, 50, 1500, 850)
        # DETECTOR
        self.detector = WasteDetector(
            "medical_waste_best.pt"
        )
        # DATABASE
        self.db = DatabaseManager()
        # CAMERA
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(
            self.update_frame
        )
        self.prev_time = 0
        self.current_frame = None
        # STATS
        self.total_stats = {}
        self.counted_ids = set()
        self.init_ui()
    # ================= UI =================
    def init_ui(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: white;
                font-family: Arial;
            }
            QPushButton {
                background-color: #1f1f1f;
                border-radius: 12px;
                padding: 12px;
                font-size: 14px;
                color: white;
            }
            QPushButton:hover {
                background-color: #333333;
            }
            QLabel {
                color: white;
            }
        """)
        main_layout = QHBoxLayout()
        # ================= SIDEBAR =================
        sidebar = QVBoxLayout()
        title = QLabel(
            "Medical Waste\nDashboard"
        )
        title.setFont(
            QFont(
                "Arial",
                20,
                QFont.Bold
            )
        )
        self.start_btn = QPushButton(
            "▶ Start Camera"
        )
        self.stop_btn = QPushButton(
            "■ Stop"
        )
        self.upload_btn = QPushButton(
            "⬆ Upload Image"
        )
        self.save_btn = QPushButton(
            "💾 Save Result"
        )
        sidebar.addWidget(title)
        sidebar.addSpacing(20)
        sidebar.addWidget(self.start_btn)
        sidebar.addWidget(self.stop_btn)
        sidebar.addWidget(self.upload_btn)
        sidebar.addWidget(self.save_btn)
        sidebar.addStretch()
        
        # ================= CENTER =================
        center_layout = QVBoxLayout()
        self.video_label = QLabel()
        self.video_label.setFixedSize(
            850,
            600
        )
        self.video_label.setStyleSheet("""
            background-color: black;
            border-radius: 20px;
        """)
        center_layout.addWidget(
            self.video_label,
            alignment=Qt.AlignCenter
        )
        # ================= RIGHT PANEL =================
        right_layout = QVBoxLayout()
        # KPI CARDS
        self.kpi_total = KPICard(
            "Total Waste",
            0,
            "#3498db"
        )
        self.kpi_sharps = KPICard(
            "Sharps Risk",
            0,
            "#ff6b6b"
        )
        self.kpi_infectious = KPICard(
            "Infectious Risk",
            0,
            "#ffd93d"
        )
        self.kpi_pharma = KPICard(
            "Pharmaceutical",
            0,
            "#00cec9"
        )
        self.kpi_general = KPICard(
            "General Waste",
            0,
            "#fdcb6e"
        )
        self.kpi_chemical = KPICard(
            "Chemical Risk",
            0,
            "#9b59b6"
        )
        kpi_grid = QGridLayout()
        kpi_grid.addWidget(
            self.kpi_total,
            0,
            0
        )
        kpi_grid.addWidget(
            self.kpi_sharps,
            0,
            1
        )
        kpi_grid.addWidget(
            self.kpi_infectious,
            1,
            0
        )
        kpi_grid.addWidget(
            self.kpi_chemical,
            1,
            1
        )
        kpi_grid.addWidget(
            self.kpi_pharma,
            2,
            0
        )
        kpi_grid.addWidget(
            self.kpi_general,
            2,
            1
        )
        
        # INFO LABELS
        self.info_label = QLabel(
            "Detection: -"
        )
        self.category_label = QLabel(
            "Category: -"
        )
        self.fps_label = QLabel(
            "FPS: 0"
        )
        for lbl in [
            self.info_label,
            self.category_label,
            self.fps_label
        ]:
            lbl.setStyleSheet("""
                font-size: 14px;
                padding: 5px;
            """)
        # CHART
        self.chart = StatsCanvas()
        right_layout.addLayout(kpi_grid)
        right_layout.addSpacing(20)
        right_layout.addWidget(
            self.info_label
        )
        right_layout.addWidget(
            self.category_label
        )
        right_layout.addWidget(
            self.fps_label
        )
        right_layout.addSpacing(20)
        right_layout.addWidget(
            self.chart
        )
        # ================= MAIN LAYOUT =================
        main_layout.addLayout(
            sidebar,
            1
        )
        main_layout.addLayout(
            center_layout,
            3
        )
        main_layout.addLayout(
            right_layout,
            2
        )
        self.setLayout(main_layout)

        # ================= BUTTONS =================
        self.start_btn.clicked.connect(
            self.start_camera
        )
        self.stop_btn.clicked.connect(
            self.stop_camera
        )
        self.upload_btn.clicked.connect(
            self.upload_image
        )
        self.save_btn.clicked.connect(
            self.save_result
        )
    # ================= CAMERA =================
    def start_camera(self):
        self.cap = cv2.VideoCapture(0)
        self.timer.start(30)
    def stop_camera(self):
        if self.cap:
            self.cap.release()
        self.timer.stop()
    # ================= VIDEO DETECTION =================
    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return
        self.current_frame = frame.copy()
        results = self.detector.track(frame)
        annotated = results[0].plot()
        names = self.detector.model.names
        detections = results[0].boxes
        frame_stats = {}
        for box in detections:
            track_id = (
                int(box.id[0])
                if box.id is not None
                else -1
            )
            cls = int(box.cls[0])
            conf = float(box.conf[0])
            label = names[cls]
            category = CATEGORY_MAP.get(
                label,
                "General Waste"
            )
            frame_stats[category] = (
                frame_stats.get(category, 0) + 1
            )
            if track_id not in self.counted_ids:
                self.counted_ids.add(track_id)
                self.total_stats[category] = (
                    self.total_stats.get(category, 0) + 1
                )
                timestamp = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
                self.db.insert_detection(
                    label,
                    category,
                    round(conf, 2),
                    timestamp
                )

        # KPI UPDATE
        total = sum(frame_stats.values())
        self.kpi_total.update_value(total)
        self.kpi_sharps.update_value(
            frame_stats.get(
                "Sharps Waste",
                0
            )
        )
        self.kpi_infectious.update_value(
            frame_stats.get(
                "Infectious Waste",
                0
            )
        )
        self.kpi_chemical.update_value(
            frame_stats.get(
                "Chemical Waste",
                0
            )
        )
        self.kpi_pharma.update_value(
            frame_stats.get(
                "Pharmaceutical Waste",
                0
            )
        )
        self.kpi_general.update_value(
            frame_stats.get(
                "General Waste",
                0
            )
        )
        # CHART UPDATE
        self.chart.update_chart(
            self.total_stats
        )
        # FPS
        current_time = time.time()
        fps = (
            1 / (current_time - self.prev_time)
            if self.prev_time else 0
        )
        self.prev_time = current_time
        self.fps_label.setText(
            f"FPS: {int(fps)}"
        )
        self.display_image(annotated)
    # ================= IMAGE DETECTION =================
    def upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Image",
            "",
            "Images (*.png *.jpg *.jpeg)"
        )
        if not file_path:
            return
        image = cv2.imread(file_path)
        self.current_frame = image.copy()
        results = self.detector.detect(image)
        annotated = results[0].plot()
        names = self.detector.model.names
        detections = results[0].boxes
        frame_stats = {}
        texts = []
        categories = set()
        if detections is not None and len(detections) > 0:
            for box in detections:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                label = names[cls]
                category = CATEGORY_MAP.get(
                    label,
                    "General Waste"
                )
                frame_stats[category] = (
                    frame_stats.get(category, 0) + 1
                )
                self.total_stats[category] = (
                    self.total_stats.get(category, 0) + 1
                )
                texts.append(
                    f"{label} ({conf:.2f})"
                )
                categories.add(category)
            self.info_label.setText(
                "Detection: " + ", ".join(texts)
            )
            self.category_label.setText(
                "Category: " + ", ".join(categories)
            )
        self.chart.update_chart(
            self.total_stats
        )
        self.display_image(annotated)
    # ================= SAVE =================
    def save_result(self):
        if self.current_frame is None:
            return
        if not os.path.exists("results"):
            os.makedirs("results")
            
        filename = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        ) + ".jpg"
        path = os.path.join(
            "results",
            filename
        )
        cv2.imwrite(
            path,
            self.current_frame
        )
        self.info_label.setText(
            f"Saved: {filename}"
        )
    # ================= DISPLAY =================
    def display_image(self, frame):
        pixmap = convert_cv_qt(frame)
        self.video_label.setPixmap(pixmap)
    # ================= CLOSE =================
    def closeEvent(self, event):
        self.stop_camera()
        self.db.close()
        event.accept()