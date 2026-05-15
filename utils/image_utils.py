import cv2
from PyQt5.QtGui import QImage, QPixmap

def convert_cv_qt(frame):
    rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )
    h, w, ch = rgb.shape
    qt_img = QImage(
        rgb.data,
        w,
        h,
        ch * w,
        QImage.Format_RGB888
    )
    return QPixmap.fromImage(qt_img)