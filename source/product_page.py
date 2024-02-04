from PyQt5.QtWidgets import QWidget, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5 import uic
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

        # Allow dynamic resizing of columns
        self.product_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.populate_table()

    def populate_table(self):
        # Clear existing rows in the table
        self.product_table.setRowCount(0)

        for row_data in self.product_list:
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