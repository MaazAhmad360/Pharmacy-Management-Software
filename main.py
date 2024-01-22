from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QGridLayout, QLabel, QLineEdit, QFrame, QScrollArea
from PyQt5 import uic
import pymysql
import random

class ProductWidget(QFrame):
    def __init__(self, product_name, stock, price):
        super().__init__()

        self.setMaximumSize(300, 150)  # Set the maximum size as needed
        self.setFrameStyle(QFrame.Panel | QFrame.Raised)  # Set frame style

        layout = QVBoxLayout()
        self.product_name_label = QLabel(product_name)
        self.stock_label = QLabel(f"Stock: {stock}")
        self.price_label = QLabel(f"Price: Rs {price}")
        layout.addWidget(self.product_name_label)
        layout.addWidget(self.stock_label)
        layout.addWidget(self.price_label)

        self.setLayout(layout)

class PharmacyPOSApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load the UI file
        uic.loadUi('ui/mainwindow.ui', self)

        # Connect to MySQL database
        self.conn = pymysql.connect(
            host='srv788.hstgr.io',
            user='u542694891_mumtazMS',
            password='MumtazMedicalStore.123',
            database='u542694891_pharmacyPOS',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        # Create a random table with placeholder data
        #self.create_random_table()

        self.showMaximized()  # This will make the window full screen
        self.setGeometry(0, 25, self.screen().geometry().width(), self.screen().geometry().height() - 50)

        # Set table headers
        headers = ['Product Name', 'Quantity', 'Price']
        self.set_table_headers(self.itemCartTable, headers)

        # Connect buttons to functions
        #self.btn_inventory.clicked.connect(self.open_inventory)
        #self.btn_reporting.clicked.connect(self.open_reporting)
        #self.btn_stock.clicked.connect(self.open_stock)

        # Create a ProductView grid layout
        self.productGridLayout = QGridLayout()
        self.productViewWidget = QWidget()
        self.productViewWidget.setLayout(self.productGridLayout)
        self.rightPOSCol.addWidget(self.productViewWidget)

        # Display default products
        self.display_default_products()

        # Connect the search button to the search_product function
        self.productSearchRightBtn.clicked.connect(self.search_product)

        #self.display_table("SELECT * FROM pharmacy_table")

    def set_table_headers(self, table_widget, headers):
        table_widget.setColumnCount(len(headers))
        table_widget.setHorizontalHeaderLabels(headers)

    def display_table(self, query):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()

                # Display the data in the table
                self.itemCartTable.setRowCount(len(result))
                self.itemCartTable.setColumnCount(len(result[0]))

                # headers = list(result[0].keys())
                # self.itemCartTable.setHorizontalHeaderLabels(headers)

                for i, row in enumerate(result):
                    for j, value in enumerate(row.values()):
                        item = QTableWidgetItem(str(value))
                        self.itemCartTable.setItem(i, j, item)

        except pymysql.Error as err:
            QMessageBox.critical(self, "MySQL Error", f"Error: {err}")

    def search_product(self):
        # Clear previous search results
        self.clear_product_view()

        # Get the search term from the input field
        search_term = self.productSearchRightInput.text()

        # Perform the search in the database
        if search_term:
            search_query = f"SELECT * FROM pharmacy_table WHERE product_name='{search_term}'"
            results = self.execute_query(search_query)

            # Display the search results in the product view
            self.display_search_results(results)
            # print(results.count())

    def execute_query(self, query):
        # Execute the SQL query and return the results
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query)
                return cursor.fetchall()
        except Exception as e:
            print(f"Error executing query: {e}")
            return []

    def clear_product_view(self):
        # Clear the product view layout
        for i in reversed(range(self.productGridLayout.count())):
            widget = self.productGridLayout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

    def display_default_products(self):
        # Sample data - replace this with your actual data retrieval logic
        default_query = "SELECT * FROM pharmacy_table LIMIT 20"
        default_results = self.execute_query(default_query)

        """# Create a QWidget instance
        layout = QWidget()

        # Create a QVBoxLayout instance and set it as the layout for the QWidget
        vbox_layout = QVBoxLayout(layout)

        countLabel = QLabel(str(len(default_results)))
        vbox_layout.addWidget(countLabel)

        self.productGridLayout.addWidget(layout, 0, 0)"""

        # Display the default products in the product view
        self.display_search_results(default_results)

    def search_product(self):
        # Clear previous search results
        self.clear_product_view()

        # Get the search term from the input field
        search_term = self.productSearchRightInput.text()

        # Perform the search in the database
        if search_term:
            search_query = f"SELECT * FROM pharmacy_table WHERE product_name LIKE '%{search_term}%'"

            results = self.execute_query(search_query)
            """# Create a QWidget instance
            layout = QWidget()

            # Create a QVBoxLayout instance and set it as the layout for the QWidget
            vbox_layout = QVBoxLayout(layout)

            countLabel = QLabel(str(len(results)))
            search_termLabel = QLabel(search_term)
            search_queryLabel = QLabel(search_query)
            vbox_layout.addWidget(countLabel)
            vbox_layout.addWidget(search_termLabel)
            vbox_layout.addWidget(search_queryLabel)

            self.productGridLayout.addWidget(layout, 0, 0)"""
            # Display the search results in the product view
            self.display_search_results(results)

    def display_search_results(self, results):
        try:
            # Display the search results in the product view
            row, col = 0, 0
            max_displayed_products = 20  # Set the maximum number of displayed products
            displayed_products = min(len(results), max_displayed_products)

            for i in range(displayed_products):
                product = results[i]
                product_widget = ProductWidget(product["product_name"], product["quantity"], product["price"])
                self.productGridLayout.addWidget(product_widget, row, col)

                col += 1
                if col == 2:  # Set the number of columns as needed
                    col = 0
                    row += 1

            # If there are more products, add a scrollbar
            if len(results) > max_displayed_products:
                scroll_area = QScrollArea()
                widget_container = QWidget()
                widget_container.setLayout(self.productGridLayout)
                scroll_area.setWidget(widget_container)
                scroll_area.setWidgetResizable(True)

                # Clear existing layout from rightPOSCol
                for i in reversed(range(self.rightPOSCol.count())):
                    widget = self.rightPOSCol.itemAt(i).widget()
                    if widget:
                        widget.setParent(None)

                # Add the scroll area to rightPOSCol
                self.rightPOSCol.addWidget(scroll_area)

        except Exception as e:
            print(f"Exception: {e}")

    """def display_search_results(self, results):
        try:
            # Display the search results in the product view
            row, col = 0, 0
            for product in results:
                product_widget = ProductWidget(product["product_name"], product["quantity"], product["price"])
                self.productGridLayout.addWidget(product_widget, row, col)

                col += 1
                if col == 4:  # Set the number of columns as needed
                    col = 0
                    row += 1
        except Exception as e:
            print(f"Exception: {e}")"""

if __name__ == '__main__':
    app = QApplication([])
    pos_app = PharmacyPOSApp()
    pos_app.show()
    app.exec_()
