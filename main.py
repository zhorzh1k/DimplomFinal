import sys
from PyQt5.QtWidgets import QApplication
from ui.dashboard import WasteApp

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = WasteApp()
    window.show()

    sys.exit(app.exec_())