import sys
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton

class SlidingMenu(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()

        self.button1 = QPushButton("Option 1")
        self.button2 = QPushButton("Option 2")

        self.layout.addWidget(self.button1)
        self.layout.addWidget(self.button2)

        self.setLayout(self.layout)

        self.setFixedWidth(200)  # Set the initial width of the menu

        # Initially hide the menu
        self.setGeometry(QRect(-self.width(), 0, self.width(), self.height()))