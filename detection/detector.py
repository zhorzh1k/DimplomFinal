import torch
from ultralytics import YOLO

class WasteDetector:
    def __init__(self, model_path="medical_waste_best.pt"):
        self.model = YOLO(model_path)
        if torch.cuda.is_available():
            self.model.to("cuda")
            print("Using GPU")
    def detect(self, frame):
        return self.model(
            frame,
            imgsz=416
        )
    def track(self, frame):
        return self.model.track(
            frame,
            persist=True,
            imgsz=416
        )