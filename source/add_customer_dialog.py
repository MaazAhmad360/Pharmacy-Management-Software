# add_customer_dialog.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton


class AddCustomerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Customer")

        self.name_label = QLabel("Name:")
        self.name_input = QLineEdit()

        self.address_label = QLabel("Address:")
        self.address_input = QLineEdit()

        self.contact_label = QLabel("Contact Number:")
        self.contact_input = QLineEdit()

        self.add_button = QPushButton("Add")
        self.add_button.clicked.connect(self.accept)

        layout = QVBoxLayout()
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.address_label)
        layout.addWidget(self.address_input)
        layout.addWidget(self.contact_label)
        layout.addWidget(self.contact_input)
        layout.addWidget(self.add_button)

        self.setLayout(layout)

    def get_customer_info(self):
        name = str(self.name_input.text())
        address = str(self.address_input.text())
        contact = int(self.contact_input.text())
        return name, address, contact
