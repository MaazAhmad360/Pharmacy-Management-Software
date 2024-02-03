from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QGridLayout, QLabel, QLineEdit, QSpinBox, QFrame, \
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
        self.product_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.product_table.verticalHeader().setSectionResizeMode(QHeaderView.Stretch)

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
        self.product_table.setItem(row_position, 3, QTableWidgetItem(row_data.group))
        self.product_table.setItem(row_position, 4, QTableWidgetItem(row_data.description))
        self.product_table.setItem(row_position, 5, QTableWidgetItem(str(row_data.purchasePrice)))
        self.product_table.setItem(row_position, 6, QTableWidgetItem(str(row_data.salesPrice)))
        self.product_table.setItem(row_position, 7, QTableWidgetItem(str(row_data.totalStock)))
        self.product_table.setItem(row_position, 8, QTableWidgetItem(row_data.formula))
        self.product_table.setItem(row_position, 9, QTableWidgetItem(row_data.formula))