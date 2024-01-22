from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QGridLayout, QLabel, QLineEdit, QFrame, QScrollArea, QSpinBox
from PyQt5 import uic
from PyQt5.QtCore import Qt, pyqtSignal
import pymysql
import random

class ProductWidget(QFrame):
    clicked = pyqtSignal(str, int, float)

    def __init__(self, product_name, stock, price):
        super().__init__()

        self.setMaximumSize(300, 150)  # Set the maximum size as needed
        self.setFrameStyle(QFrame.Panel | QFrame.Raised)  # Set frame style

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
        # Connect the click event to the custom slot
        #self.clicked.connect(self.on_click)

    def on_add_to_cart(self):
        self.clicked.emit(
            self.product_name_label.text(),
            int(self.stock_label.text().split(":")[-1].strip()),
            float(self.price_label.text().split(":")[-1].strip().split()[1])
        )

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

        self.cart_items = {} # Dictionary to store items in the cart with their quantities
        # Connect buttons to functions
        #self.btn_inventory.clicked.connect(self.open_inventory)
        #self.btn_reporting.clicked.connect(self.open_reporting)
        #self.btn_stock.clicked.connect(self.open_stock)

        # Get references to the labels
        self.total_items_count_label = self.findChild(QLabel, 'totalItemsCountLabel')
        self.discount_input = self.findChild(QLineEdit, 'discountInput')
        self.cash_return_count_label = self.findChild(QLabel, 'netPriceCountLabel')
        self.price_count_label = self.findChild(QLabel, 'priceCountLabel')

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

    def add_to_cart(self, name, stock, price):
        # Check if the item is already in the cart
        if name in self.cart_items:
            # If yes, increment the quantity
            self.cart_items[name]['quantity'] += 1
        else:
            # If not, add it to the cart with quantity 1
            self.cart_items[name] = {'quantity': 1, 'price': price}

        # Update the cart table
        self.update_cart_table()

        # Update the total price labels
        self.update_total_price_labels()

    def update_cart_table(self):
        # Clear the cart table
        self.itemCartTable.setRowCount(0)

        # Populate the cart table with items, quantities, and price
        for product, details in self.cart_items.items():
            row_position = self.itemCartTable.rowCount()
            self.itemCartTable.insertRow(row_position)

            # Set the product name
            self.itemCartTable.setItem(row_position, 0, QTableWidgetItem(product))

            # Create a spin box for the quantity
            quantity_spinbox = QSpinBox()
            quantity_spinbox.setMinimum(1)  # Set the minimum value for the spin box
            quantity_spinbox.setValue(details['quantity'])  # Set the initial value
            quantity_spinbox.valueChanged.connect(self.update_quantity_in_cart)  # Connect the signal for value change

            # Set the spin box as the widget for the quantity column
            self.itemCartTable.setCellWidget(row_position, 1, quantity_spinbox)

            # Set the price
            self.itemCartTable.setItem(row_position, 2, QTableWidgetItem(str(details['price'])))

    def update_quantity_in_cart(self):
        # Update the quantity in the cart_items dictionary when the spin box value changes
        for row in range(self.itemCartTable.rowCount()):
            product_name = self.itemCartTable.item(row, 0).text()
            quantity = self.itemCartTable.cellWidget(row, 1).value()
            self.cart_items[product_name]['quantity'] = quantity

            # Update the cart table
            self.update_cart_table()

            # Update the total price labels
            self.update_total_price_labels()

    """def add_product_to_cart(self, name, price):
            try:
                if name in self.cart_items:
                    # If yes, increment the quantity
                    self.cart_items[name]['quantity'] += 1
                else:
                    row_position = self.itemCartTable.rowCount()
                    self.itemCartTable.insertRow(row_position)
                    self.itemCartTable.setItem(row_position, 0, QTableWidgetItem(name))
                    self.itemCartTable.setItem(row_position, 1, QTableWidgetItem(str(1)))
                    self.itemCartTable.setItem(row_position, 2, QTableWidgetItem(str(price)))

            except pymysql.Error as err:
                QMessageBox.critical(self, "MySQL Error", f"Error: {err}")"""

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
            for product in results:
                product_widget = ProductWidget(product["product_name"], product["quantity"], product["price"])
                product_widget.clicked.connect(self.add_to_cart)
                self.productGridLayout.addWidget(product_widget, row, col)

                col += 1
                if col == 4:  # Set the number of columns as needed
                    col = 0
                    row += 1
        except Exception as e:
            print(f"Exception: {e}")

    def update_total_price_labels(self):
        #total_items = sum(item['quantity'] for item in self.cart_items.values())
        total_items = len(self.cart_items)
        total_price = sum(item['quantity'] * item['price'] for item in self.cart_items.values())
        discount = float(self.discount_input.text()) if self.discount_input.text() else 0.0
        cash_return = total_price - discount  # Example calculation, update as needed

        # Update the labels with the calculated values
        self.total_items_count_label.setText(str(total_items))
        self.cash_return_count_label.setText(f"Rs {cash_return:.2f}")
        self.price_count_label.setText(f"Rs {total_price:.2f}")

if __name__ == '__main__':
    app = QApplication([])
    pos_app = PharmacyPOSApp()
    pos_app.show()
    app.exec_()
