# source/main_header_widget.py
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QSpinBox
from PyQt5.QtCore import pyqtSignal
class MainHeader(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QHBoxLayout()

        self.dashboard_btn = QPushButton()
        self.inventory_btn = QPushButton()

        self.dashboard_btn.setText("Dashboard")
        self.inventory_btn.setText("Inventory")

        self.layout.addWidget(self.dashboard_btn)
        self.layout.addWidget(self.inventory_btn)


        self.setLayout(self.layout)
