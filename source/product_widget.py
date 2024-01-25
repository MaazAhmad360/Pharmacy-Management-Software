# source/product_widget.py
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton, QSpinBox
from PyQt5.QtCore import pyqtSignal
from source.product import Product

class ProductWidget(QFrame):
    clicked = pyqtSignal(Product)

    def __init__(self, product):
        super().__init__()

        self.setMaximumSize(200, 125)
        self.setMinimumSize(200, 125)
        self.setFrameStyle(QFrame.Box | QFrame.Raised)
        self.setStyleSheet("background-color: rgb(255, 255, 255);")

        self.product = product  # saving the product in the widget to emit as signal

        layout = QVBoxLayout()
        self.product_name_label = QLabel(product.name)
        self.stock_label = QLabel(f"Stock: {product.totalStock}")
        self.price_label = QLabel(f"Price: Rs {product.salesPrice}")
        self.add_to_cart_button = QPushButton("+ Add to Cart")
        self.add_to_cart_button.clicked.connect(self.on_add_to_cart)

        layout.addWidget(self.product_name_label)
        layout.addWidget(self.stock_label)
        layout.addWidget(self.price_label)
        layout.addWidget(self.add_to_cart_button)

        self.setLayout(layout)

    def on_add_to_cart(self):
        self.clicked.emit(
            self.product
        )
