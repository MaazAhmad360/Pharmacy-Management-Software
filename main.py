# main.py
from PyQt5.QtWidgets import QApplication
from source.pharmacy_pos_app import PharmacyPOSApp

if __name__ == '__main__':
    app = QApplication([])
    pos_app = PharmacyPOSApp()
    pos_app.show()
    app.exec_()
