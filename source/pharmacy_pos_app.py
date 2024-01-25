# pharmacy_pos_app.py
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QGridLayout, QLabel, QLineEdit, QSpinBox, QFrame, \
    QPushButton, QTableWidgetItem, QComboBox, QCompleter, QDialog, QMessageBox, QScrollArea
from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal, QTimer, Qt, QEvent
import pymysql
from source.product_widget import ProductWidget
from source.database_helper import connect_to_database, execute_query, execute_query_with_status
from source.add_customer_dialog import AddCustomerDialog


class PharmacyPOSApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load the UI file
        uic.loadUi('ui/mainwindow.ui', self)

        # Connect to MySQL database
        self.conn = connect_to_database()

        # Create a random table with placeholder data
        # self.create_random_table()

        # Set table headers
        headers = ['Product Name', 'Quantity', 'Unit Rate', 'Net Price', 'Remove']
        self.set_table_headers(self.itemCartTable, headers)

        self.cart_items = {}  # Dictionary to store items in the cart with their quantities

        # Get reference to widgets
        self.customerComboBox = self.findChild(QComboBox, 'customerSelect')
        self.addCustomerButton = self.findChild(QPushButton, 'addCustomerBtn')

        # Get references to the labels
        self.total_items_count_label = self.findChild(QLabel, 'totalItemsCountLabel')
        self.discount_input = self.findChild(QLineEdit, 'discountInput')
        self.cash_return_count_label = self.findChild(QLabel, 'netPriceCountLabel')
        self.price_count_label = self.findChild(QLabel, 'priceCountLabel')

        self.product_scroll_area = QScrollArea()
        self.product_scroll_area.setWidgetResizable(True)

        # Create a ProductView grid layout
        self.productGridLayout = QGridLayout()
        self.productViewWidget = QWidget()
        self.productViewWidget.setLayout(self.productGridLayout)
        #self.rightPOSCol.addWidget(self.productViewWidget)

        # Set the product view widget as the content of the scroll area
        self.product_scroll_area.setWidget(self.productViewWidget)
        self.rightPOSCol.addWidget(self.product_scroll_area)

        # self.productGridLayout = QGridLayout()
        # self.productViewWidget = QScrollArea()
        # self.productViewWidget.setLayout(self.productGridLayout)
        # self.rightPOSCol.addWidget(self.productViewWidget)

        self.all_products = self.fetch_all_products() # loading all products in memory
        # Display default products
        self.display_default_products()

        # Create a QTimer for dynamic product search
        # self.product_search_timer = QTimer()
        # self.product_search_timer.timeout.connect(self.delayed_search_product)

        # Connect the search button to the search_product function
        self.productSearchRightBtn.clicked.connect(self.search_product)

        # Connect the text changed signal to the search_product_dynamic function
        self.productSearchRightInput.textChanged.connect(self.search_product_dynamic)
        self.productSearchRightInput.setPlaceholderText("Search Products")

        # Connect the text changed signal to start the timer
        # self.productSearchRightInput.textChanged.connect(self.start_product_search_timer)

        # Set up customerComboBox settings
        self.customerComboBox.setEditable(True)
        self.customerComboBox.setPlaceholderText("Select Customer")  # when the combo box is uneditable
        self.customerComboBox.lineEdit().setPlaceholderText("Select Customer")  # when the combo bos is editable
        self.customerComboBox.installEventFilter(self)
        self.customerListModel = self.customerComboBox.model()
        self.customerComboBox.clearFocus()
        # self.customerComboBox.currentTextChanged.connect(self.start_customer_search_timer)
        # self.customerComboBox.editTextChanged.connect(self.start_customer_search_timer)
        # self.customerComboBox.currentTextChanged.connect(self.search_customers_dynamic)
        # self.customerComboBox.editTextChanged.connect(self.search_customers_dynamic)

        # Connect the QPushButton click event to the add_customer function
        self.addCustomerButton.clicked.connect(self.add_customer)

        # Populate the customer names in the combo box
        self.populate_customer_names()

        # Set the initial completion model
        self.customerSearchCompleter = QCompleter()
        self.customerSearchCompleter.setCaseSensitivity(Qt.CaseInsensitive)
        self.customerSearchCompleter.setFilterMode(Qt.MatchContains)
        self.customerSearchCompleter.setModel(self.customerComboBox.model())
        self.customerComboBox.setCompleter(self.customerSearchCompleter)

        self.showMaximized()  # This will make the window full screen
        self.setGeometry(0, 25, self.screen().geometry().width(), self.screen().geometry().height() - 50)
        # self.display_table("SELECT * FROM pharmacy_table")

    def eventFilter(self, source, event):
        if event.type() == QEvent.FocusIn and source is self.customerComboBox:
            if self.customerComboBox.hasFocus() and self.customerComboBox.currentText() == "":
                self.customerSearchCompleter.setCompletionPrefix("")
                self.customerSearchCompleter.complete()
                # self.customerComboBox.completer().complete()
                # self.customerComboBox.showPopup()

        elif event.type() == QEvent.KeyPress:
            # Intercept key events, specifically looking for the Enter key press
            key_event = event
            if source == self.customerComboBox:
                if key_event.key() == Qt.Key_Enter or key_event.key() == Qt.Key_Return:
                    current_text = self.customerComboBox.currentText()
                    completer_model = self.customerSearchCompleter.model()

                    # Check if the current text is not in the model list
                    # Check if the current text exactly matches one of the existing items
                    if current_text in [self.customerListModel.item(i).text() for i in range(self.customerListModel.rowCount())]:
                        self.comboBox.completer().setCompletionPrefix(current_text)
                    # if current_text and current_text not in self.get_string_list(completer_model):
                    elif current_text and current_text not in self.get_string_list(completer_model):
                        # Prevent the completer from adding the current text
                        self.customerSearchCompleter.setCompletionPrefix("")
                        self.add_customer(str(current_text))
                        return True  # Event handled, don't propagate further

        return super().eventFilter(source, event)

    def resizeEvent(self, event):
        # Override the resize event to update the product grid layout when the window is resized
        super().resizeEvent(event)
        self.update_product_grid_layout()

    def execute_query(self, query):
        return execute_query(query, self.conn)

    def set_table_headers(self, table_widget, headers):
        table_widget.setColumnCount(len(headers))
        table_widget.setHorizontalHeaderLabels(headers)

    def add_to_cart(self, name, stock, price):
        # Check if the item is already in the cart
        if name in self.cart_items:
            # If yes, increment the quantity
            self.cart_items[name]['quantity'] += 1
            self.cart_items[name]['netPrice'] += self.cart_items[name]['price']
        else:
            # If not, add it to the cart with quantity 1
            self.cart_items[name] = {'quantity': 1, 'price': price, 'netPrice': price}

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

            # Add remove button (cross icon)
            remove_button = QPushButton()
            remove_button.setIcon(QIcon('assets/cross.svg'))  # Replace with the path to your cross icon
            remove_button.clicked.connect(lambda _, row=row_position: self.remove_from_cart(row))

            # Set button properties to make it look flush
            remove_button.setStyleSheet("background-color: transparent; border: none;")

            # Set the remove button as the widget for the remove column
            self.itemCartTable.setCellWidget(row_position, 4, remove_button)

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

            totalPrice = details['quantity'] * details['price']
            self.itemCartTable.setItem(row_position, 3, QTableWidgetItem(str(f"Rs {totalPrice}")))

    def update_quantity_in_cart(self):
        # Update the quantity in the cart_items dictionary when the spin box value changes
        for row in range(self.itemCartTable.rowCount()):
            product_name = self.itemCartTable.item(row, 0).text()
            quantity = self.itemCartTable.cellWidget(row, 1).value()
            price = self.itemCartTable.item(row, 2).text()

            totalPrice = quantity * float(price)
            self.itemCartTable.setItem(row, 3, QTableWidgetItem(str(f"Rs {totalPrice}")))
            self.cart_items[product_name]['quantity'] = quantity
            self.cart_items[product_name]['netPrice'] = totalPrice

            # Update the cart table
            # self.update_cart_table()

            # Update the total price labels
            self.update_total_price_labels()

    def update_total_price_labels(self):
        # total_items = sum(item['quantity'] for item in self.cart_items.values())
        total_items = len(self.cart_items)
        total_price = sum(item['quantity'] * item['price'] for item in self.cart_items.values())
        discount = float(self.discount_input.text()) if self.discount_input.text() else 0.0
        cash_return = total_price - discount  # Example calculation, update as needed

        # Update the labels with the calculated values
        self.total_items_count_label.setText(str(total_items))
        self.cash_return_count_label.setText(f"Rs {cash_return:.2f}")
        self.price_count_label.setText(f"Rs {total_price:.2f}")

    def remove_from_cart(self, row):
        item_name = self.itemCartTable.item(row, 0).text()
        del self.cart_items[item_name]
        self.update_cart_table()
        self.update_total_price_labels()

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

    def clear_product_view(self):
        # Clear the product view layout
        for i in reversed(range(self.productGridLayout.count())):
            widget = self.productGridLayout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

    def display_default_products(self):
        # Sample data - replace this with your actual data retrieval logic
        default_query = "SELECT * FROM pharmacy_table LIMIT 20"
        # default_results = self.execute_query(default_query)

        """# Create a QWidget instance
        layout = QWidget()

        # Create a QVBoxLayout instance and set it as the layout for the QWidget
        vbox_layout = QVBoxLayout(layout)

        countLabel = QLabel(str(len(default_results)))
        vbox_layout.addWidget(countLabel)

        self.productGridLayout.addWidget(layout, 0, 0)"""

        # Display the default products in the product view
        # self.display_search_results(default_results)
        self.display_search_results(self.all_products)

    def start_product_search_timer(self):
        # Start the timer when text is changed
        self.product_search_timer.start(300)  # Adjust the delay (milliseconds) as needed

    def delayed_search_product(self):
        # Called when the timer times out (user has stopped typing)
        self.search_product_dynamic()

    def fetch_all_products(self):
        # Fetch all products from the database
        query = "SELECT * FROM pharmacy_table"
        return self.execute_query(query)

    def update_product_grid_layout(self):
        # Calculate the number of columns based on the available width
        available_width = self.productViewWidget.width()
        column_width = 200  # Adjust the column width as needed
        num_columns = max(1, available_width // column_width)

        # Clear the existing layout
        for i in reversed(range(self.productGridLayout.count())):
            widget = self.productGridLayout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Add widgets to the layout based on the new number of columns
        row, col = 0, 0
        for product_widget in self.product_widgets:
            self.productGridLayout.addWidget(product_widget, row, col)

            col += 1
            if col == num_columns:
                col = 0
                row += 1

    def search_product_locally(self, search_term):
        # Perform a local search on the already fetched products
        results = [product for product in self.all_products if search_term.lower() in product["product_name"].lower()]
        return results

    def search_product(self):
        # Clear previous search results
        self.clear_product_view()

        # Get the search term from the input field
        search_term = self.productSearchRightInput.text()

        # Perform the search in the database
        if search_term:
            # search_query = f"SELECT * FROM pharmacy_table WHERE product_name LIKE '%{search_term}%'"

            # results = self.execute_query(search_query)
            results = self.search_product_locally(search_term)

            # Display the search results in the product view
            self.display_search_results(results)
        else:
            # If search term is empty, display default products
            self.display_default_products()

    def search_product_dynamic(self):
        # Clear previous search results
        self.clear_product_view()

        # Get the search term from the input field
        search_term = self.productSearchRightInput.text()

        # Perform the search in the database
        if search_term:
            # search_query = f"SELECT * FROM pharmacy_table WHERE product_name LIKE '%{search_term}%'"
            # results = self.execute_query(search_query)
            results = self.search_product_locally(search_term)

            # Display the search results in the product view
            self.display_search_results(results)
        else:
            # If search term is empty, display default products
            self.display_default_products()

    def display_search_results(self, results):
        try:
            # Clear the product grid layout
            self.clear_product_view()

            # Store product widgets in a list
            self.product_widgets = []

            # Display the search results in the product view
            for product in results:
                product_widget = ProductWidget(product["product_name"], product["quantity"], product["price"])
                product_widget.clicked.connect(self.add_to_cart)
                self.product_widgets.append(product_widget)

            # Update the product grid layout
            self.update_product_grid_layout()
        except Exception as e:
            print(f"Exception: {e}")

    """def display_search_results(self, results):
        try:
            # Display the search results in the product view
            row, col = 0, 0
            for product in results:
                product_widget = ProductWidget(product["product_name"], product["quantity"], product["price"])
                product_widget.clicked.connect(self.add_to_cart)
                self.productGridLayout.addWidget(product_widget, row, col)

                col += 1
                if col == self.productGridLayout.columnCount():  # Set the number of columns as needed
                    col = 0
                    row += 1
        except Exception as e:
            print(f"Exception: {e}")"""

    def fetch_customer_names(self, search_term=None):
        # Define the base query to fetch customer names
        base_query = "SELECT DISTINCT Name FROM Customers"

        # If a search term is provided, add it to the query
        if search_term:
            base_query += f" WHERE Name LIKE '%{search_term}%'"

        try:
            with self.conn.cursor() as cursor:
                cursor.execute(base_query)
                result = cursor.fetchall()

                # Extract customer names from the result
                customer_names = [customer['Name'] for customer in result]

                return customer_names
        except pymysql.Error as e:
            print(f"Error fetching customer names: {e}")
            return []

    def populate_customer_names(self, search_term=None):
        # Fetch the list of customer names from the database based on the search term
        customer_names = self.fetch_customer_names(search_term)

        # Clear existing items and populate the names in the combo box
        self.customerComboBox.clear()
        self.customerComboBox.addItems(customer_names)

    def search_customers(self):
        # Get the search term from the input field
        search_term = self.customerSearchInput.text()

        # Perform the search in the database and populate customer names
        self.populate_customer_names(search_term)

    def get_string_list(self, model):
        string_list = []
        for row in range(model.rowCount()):
            item = model.item(row)
            if item is not None:
                string_list.append(item.text())
        return string_list

    def add_customer(self, name):
        try:
            # Create an instance of the AddCustomerDialog
            dialog = AddCustomerDialog(self)

            if name:
                dialog.name_input.insert(name)
            # Execute the dialog and get the result
            result = dialog.exec_()

            # Check if the user clicked the "Add" button
            if result == QDialog.Accepted:
                name, address, contact = dialog.get_customer_info()

                # Add the customer to the database (you need to implement this function)
                self.add_customer_to_database(name, address, contact)

                # Update the customer combo box with the new customer
                self.populate_customer_names()

        except Exception as e:
            print(f"Error adding customer: {e}")
            # Handle the error appropriately (e.g., show an error message to the user)

    def add_customer_to_database(self, name, address, contact):
        query = f"INSERT INTO Customers (Name, Address, Contact) VALUES ('{name}', '{address}', '{contact}')"
        success, result = execute_query_with_status(query, self.conn)

        successDialog = QMessageBox()
        if success:
            successDialog.setText("Customer Added Successfuly")
            # print("Customer added successfully!")
        else:
            successDialog.setText("Failed To Add Customer")

        successDialog.exec_()
        return result

    """def add_customer_to_database(self, name, address, contact):
        # Implement the code to add the customer to the database
        # query = f"INSERT INTO 'Customers' ('Name', 'Address', 'Contact') VALUES ('{name}', '{address}', '{contact}')"
        query = f"INSERT INTO Customers (Name, Address, Contact) VALUES ('{name}', '{address}', '{contact}')"
        # query = f"INSERT INTO `Customers`(`Name`, `Address`, `Contact`) VALUES ('{name}','{address}','{contact}')"
        self.execute_query(query)"""

    """def start_customer_search_timer(self):
        # Start the timer when text is changed
        self.customer_search_timer.start(300)  # Adjust the delay (milliseconds) as needed

    def delayed_search_customer(self):
        # Called when the timer times out (user has stopped typing)
        self.search_customers_dynamic()"""

    """def search_customers_dynamic(self):
        # Get the search term from the input field
        search_term = self.customerComboBox.currentText()

        # Perform the search in the database
        if search_term:
            self.populate_customer_names(search_term)
            self.customerComboBox.showPopup()
            #results = self.execute_query(search_query)

            # Display the search results in the product view
            #self.display_search_results(results)
        else:
            # If search term is empty, display default products
            self.populate_customer_names()"""

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

    """def search_product(self):
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
        else:
            # If search term is empty, display default products
           self.display_default_products()"""
