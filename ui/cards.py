from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout

class KPICard(QFrame):
    def __init__(self, title, value, color):
        super().__init__()
        self.setStyleSheet(f"""
            QFrame {{
                background-color: #1f1f1f;
                border-radius: 15px;
                border-left: 6px solid {color};
            }}
        """)
        layout = QVBoxLayout()
        self.title = QLabel(title)
        self.title.setStyleSheet("""
            color: #aaaaaa;
            font-size: 13px;
        """)
        self.value = QLabel(str(value))
        self.value.setStyleSheet("""
            color: white;
            font-size: 28px;
            font-weight: bold;
        """)
        layout.addWidget(self.title)
        layout.addWidget(self.value)

        self.setLayout(layout)
    def update_value(self, value):
        self.value.setText(str(value))