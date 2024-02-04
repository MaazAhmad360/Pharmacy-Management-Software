from PyQt5.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QGridLayout, QPushButton, QVBoxLayout
from PyQt5 import uic
from PyQt5.QtGui import QIcon
from source.helper import Helper
from source.data_manager import DataManager

class ProductWindow(QWidget):
    def __init__(self, product=None):
        super().__init__()

        self.product = product

        self.setWindowTitle("Product Details")
        self.setGeometry(800, 100, 400, 400)  # Adjust the geometry as needed

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Add your widgets for product details here
        # For example:
        # barcode_label = QLabel("Barcode:")
        # barcode_edit = QLineEdit()
        # layout.addWidget(barcode_label)
        # layout.addWidget(barcode_edit)

        # Add "Save" and "Cancel" buttons
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Cancel")

        save_button.clicked.connect(self.save_product)
        cancel_button.clicked.connect(self.close)

        layout.addWidget(save_button)
        layout.addWidget(cancel_button)

        self.setLayout(layout)

    def save_product(self):
        # Add logic to save/update the product details to the database
        # You can access the product details using self.product

        # After saving, you might want to refresh the main product table
        # You can emit a signal or call a method in the main window to achieve this

        self.close()

class ProductPage(QWidget):
    def __init__(self):
        super().__init__()

        # Load the UI file
        self.header = None
        uic.loadUi('ui/product-page.ui', self)

        self.data_manager = DataManager()

        self.init_header()

        self.init_table()

    def init_header(self):
        self.header_layout = self.findChild(QGridLayout, 'product_header_layout')


        self.new_product_btn = QPushButton("New Product")
        self.edit_product_btn = QPushButton("Edit Product")
        self.delete_product_btn = QPushButton("Delete Product")
        self.new_group_btn = QPushButton("New Group")
        self.edit_group_btn = QPushButton("Edit Group")
        self.delete_group_btn = QPushButton("Delete Group")

        self.header_layout.addWidget(self.new_group_btn, 0, 0)
        self.header_layout.addWidget(self.edit_group_btn, 0, 1)
        self.header_layout.addWidget(self.delete_group_btn, 0, 2)
        self.header_layout.addWidget(self.new_product_btn, 1, 0)
        self.header_layout.addWidget(self.edit_product_btn, 1, 1)
        self.header_layout.addWidget(self.delete_product_btn, 1, 2)

        self.new_product_btn.clicked.connect(self.show_new_product_window)

        # self.refresh_btn = QPushButton("Refresh")
        # self.header = ProductHeader(self.product_header_widget, self.header_layout)

    def init_table(self):
        self.product_table = self.findChild(QTableWidget, 'product_table_widget')
        headers = ["ProductID", "Barcode", "Name", "ProductGroup", "Description", "PurchasePrice", "SalesPrice",
                   "TotalStock", "Formula", "MinStock", "MaxStock", "CreationDate", "ManufacturerID"]
        Helper.set_table_headers(self.product_table, headers)

        # Allow dynamic resizing of columns
        self.product_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.populate_table()

        # Disable editing for the entire table
        self.product_table.setEditTriggers(QTableWidget.NoEditTriggers)

        # Set the selection behavior to select entire rows
        self.product_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        # Hide the vertical header (row numbers)
        self.product_table.verticalHeader().setVisible(False)

    def populate_table(self):
        # Clear existing rows in the table
        self.product_table.setRowCount(0)

        for row_data in self.data_manager.product_list:
            self.add_row_to_table(row_data)

    def add_row_to_table(self, row_data):
        row_position = self.product_table.rowCount()
        self.product_table.insertRow(row_position)

        # Populate the table with data
        self.populate_table_row(row_position, row_data)

    def populate_table_row(self, row_position, row_data):
        # Define a mapping between column indices and attribute names in row_data
        column_mapping = {
            0: 'ID', 1: 'barcode', 2: 'name', 3: 'group.name', 4: 'description',
            5: 'purchasePrice', 6: 'salesPrice', 7: 'totalStock', 8: 'formula.name',
            9: 'manufacturer.name'
        }

        for column, attribute in column_mapping.items():
            attribute_names = attribute.split('.')
            value = row_data
            for attr_name in attribute_names:
                value = getattr(value, attr_name, None)
                if value is None:
                    break

            if value is not None:
                self.product_table.setItem(row_position, column, QTableWidgetItem(str(value)))

    def show_new_product_window(self):
        product_window = ProductWindow()
        product_window.show()
"""from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QGridLayout, QLabel, QLineEdit, QSpinBox, QFrame, \
    QPushButton, QTableWidgetItem, QComboBox, QCompleter, QDialog, QMessageBox, QScrollArea, QHeaderView, QTableWidget
from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal, QTimer, Qt, QEvent, QPropertyAnimation, QRect
from source.database_helper import execute_query
from source.globals import PRODUCT_TABLE
from source.helper import Helper

class ProductPage(QWidget):
    def __init__(self, product_list):
        super().__init__()

        # Load the UI file
        uic.loadUi('ui/product-page.ui', self)

        self.product_list = product_list

        self.init_table()

    def init_table(self):
        self.product_table = self.findChild(QTableWidget, 'product_table_widget')
        headers = ["ProductID", "Barcode", "Name", "ProductGroup", "Description", "PurchasePrice", "SalesPrice",
                   "TotalStock", "Formula", "MinStock", "MaxStock", "CreationDate", "ManufacturerID"]
        Helper.set_table_headers(self.product_table, headers)

        # Set the table to stretch columns and rows
        # self.product_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.product_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.populate_table()

    def populate_table(self):
        # Clear existing rows in the table
        self.product_table.setRowCount(0)

        # Replace this with your actual MySQL query
        # query = f"SELECT * FROM {PRODUCT_TABLE}"
        # result = execute_query(query, self.conn)

        for row_data in self.product_list:
            self.add_row_to_table(row_data)

    def add_row_to_table(self, row_data):
        row_position = self.product_table.rowCount()
        self.product_table.insertRow(row_position)

        self.product_table.setItem(row_position, 0, QTableWidgetItem(str(row_data.ID)))
        self.product_table.setItem(row_position, 1, QTableWidgetItem(str(row_data.barcode)))
        self.product_table.setItem(row_position, 2, QTableWidgetItem(row_data.name))

        if row_data.group:
            self.product_table.setItem(row_position, 3, QTableWidgetItem(str(row_data.group.name)))
        self.product_table.setItem(row_position, 4, QTableWidgetItem(row_data.description))
        self.product_table.setItem(row_position, 5, QTableWidgetItem(str(row_data.purchasePrice)))
        self.product_table.setItem(row_position, 6, QTableWidgetItem(str(row_data.salesPrice)))
        self.product_table.setItem(row_position, 7, QTableWidgetItem(str(row_data.totalStock)))

        if row_data.formula:
            self.product_table.setItem(row_position, 8, QTableWidgetItem(str(row_data.formula.name)))
        if row_data.manufacturer:
            self.product_table.setItem(row_position, 9, QTableWidgetItem(row_data.manufacturer.name))"""