# source/product_widget.py
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton, QSpinBox
from PyQt5.QtCore import pyqtSignal

class ProductWidget(QFrame):
    clicked = pyqtSignal(str, int, float)

    def __init__(self, product_name, stock, price):
        super().__init__()

        self.setMaximumSize(200, 125)
        self.setMinimumSize(200, 125)
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setStyleSheet("background-color: rgb(255, 255, 255);")

        layout = QVBoxLayout()
        self.product_name_label = QLabel(product_name)
        self.stock_label = QLabel(f"Stock: {stock}")
        self.price_label = QLabel(f"Price: Rs {price}")
        self.add_to_cart_button = QPushButton("+ Add to Cart")
        self.add_to_cart_button.clicked.connect(self.on_add_to_cart)

        layout.addWidget(self.product_name_label)
        layout.addWidget(self.stock_label)
        layout.addWidget(self.price_label)
        layout.addWidget(self.add_to_cart_button)

        self.setLayout(layout)

    def on_add_to_cart(self):
        self.clicked.emit(
            self.product_name_label.text(),
            int(self.stock_label.text().split(":")[-1].strip()),
            float(self.price_label.text().split(":")[-1].strip().split()[1])
        )
