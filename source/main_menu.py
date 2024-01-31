"""import sys
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton
from PyQt5.QtGui import QIcon

class SlidingMenu(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()

        self.button_icon = QIcon("../assets/cross.png")  # Replace with your icon file

        # Create a button with icon only for both states
        self.button = QPushButton(self.button_icon, "")
        self.button.setCheckable(True)
        self.button.setIconSize(self.button.sizeHint())  # Set the icon size to match the button size
        self.button.setStyleSheet("text-align: left;")

        # Initially hide the button text
        self.button.setChecked(True)
        self.collapse_btn = False
        self.button.clicked.connect(self.toggle_button_text)
        # self.button.setLayoutDirection(Qt.lef)

        self.layout.addWidget(self.button)

        self.setLayout(self.layout)

        padding = 10  # Adjust the padding as needed
        self.collapsed_width = self.button.sizeHint().width() + padding # Set the width of the collapsed menu
        self.expanded_width = 200  # Set the width of the expanded menu

        self.setFixedWidth(self.collapsed_width)  # Set the initial width of the menu

    def toggle_button_text(self):
        if self.collapse_btn:
            self.button.setIcon(self.button_icon)
            self.button.setText("")
        else:
            self.button.setIcon(self.button_icon)
            self.button.setText("Options")
"""