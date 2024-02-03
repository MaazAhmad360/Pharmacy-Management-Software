# pharmacy_pos_app.py
from source.globals import *
import datetime
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QGridLayout, QLabel, QLineEdit, QSpinBox, QFrame, \
    QPushButton, QTableWidgetItem, QComboBox, QCompleter, QDialog, QMessageBox, QScrollArea, QStackedWidget
from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal, QTimer, Qt, QEvent, QPropertyAnimation, QRect
import pymysql
from source.product_widget import ProductWidget
from source.database_helper import connect_to_database, execute_query, execute_query_with_status
from source.add_customer_dialog import AddCustomerDialog
from source.product import Product
from source.batch import Batch
from source.vendor import Vendor
from source.customer import Customer
from source.main_header_widget import MainHeader
#from source.main_menu import SlidingMenu
from source.product_page import ProductPage
from source.helper import Helper


# TODO: Add to Cart only if Batch Present
# TODO: No Payment on empty cart
# TODO: Customer Validation Before Payment
# TODO: Add Menu Animation (Currently Commented init_menu())
# TODO: Change element names: PointOfSalesPage
class PharmacyPOSApp(QMainWindow):
    def __init__(self):
        super().__init__()

        # Connect to MySQL database
        self.conn = connect_to_database()

        # Create a random table with placeholder data
        # self.create_random_table()

        self.cart_items = {}  # Dictionary to store items in the cart with their quantities

        # initializing all products in a list
        all_products = self.fetch_all(PRODUCT_TABLE) # loading all products in memory
        self.product_list = []
        for product in all_products:
            self.product_list.append(Product(product["ProductID"], product["Barcode"], product["Name"], product["ProductGroup"], product["Description"], product["PurchasePrice"], product["SalesPrice"], product["TotalStock"], product["Formula"], product["MinStock"], product["MaxStock"], product["CreationDate"], product["ManufacturerID"]))

        # initialing all vendors in a list
        all_vendors = self.fetch_all(VENDORS_TABLE)
        self.vendor_list = []
        for vendor in all_vendors:
            self.vendor_list.append(Vendor(vendor["VendorID"], vendor["Name"], vendor["Address"], vendor["City"],))

        # initializing all batches in a list
        all_batches = self.fetch_all(BATCHES_TABLE)  # loading all batches in memory
        self.batch_list = []
        for batch in all_batches:
            self.batch_list.append(Batch(batch["BatchID"], batch["BatchCode"], batch["ArrivalDate"], batch["ManufacturingDate"], batch["ExpiryDate"], batch["Quantity"]))

            self.batch_list[-1].add_vendor(next((vendor for vendor in self.vendor_list if int(batch["VendorID"]) == vendor.ID), None))  # find the matching vendorID from the vendorlist and reference it in the batch instance - same purpose as the one commented below
            """for vendor in self.vendor_list:  # referencing the appropriate vendor through ID
                if int(batch["VendorID"]) is vendor.ID:
                    self.batch_list[-1].add_vendor(vendor)"""

            for product in self.product_list:  # associating the batch with the appropriate product
                if int(batch["ProductID"]) is product.ID:
                    product.add_batch(self.batch_list[-1])

        all_customers = self.fetch_all(CUSTOMERS_TABLE)
        self.customer_list = []
        for customer in all_customers:
            self.customer_list.append(Customer(customer["CustomerID"], customer["Name"], customer["Address"], customer["Contact"]))

        self.init_ui()

        # self.display_table("SELECT * FROM pharmacy_table")

    def init_ui(self):
        # Load the UI file
        uic.loadUi('ui/mainwindow.ui', self)

        # self.init_menu()
        self.init_menu()

        self.init_cart()

        self.init_product_grid()

        self.init_customer()

        self.init_product_page()

        self.showMaximized()  # This will make the window full screen
        self.setGeometry(0, 25, self.screen().geometry().width(), self.screen().geometry().height() - 50)

    def init_product_page(self):
        self.product_page_widget = ProductPage(self.product_list)
        self.product_layout.addWidget(self.product_page_widget)

    def init_menu(self):
        self.main_stacked_widget = self.findChild(QStackedWidget, 'mainWindowStackedWidget')
        self.product_page = self.findChild(QWidget, 'product_page')
        self.dashboard_page = self.findChild(QWidget, 'dashboard_page')
        self.home_page = self.findChild(QWidget, 'pointOfSalePage')

        self.dashboard_btn = self.findChild(QPushButton, 'menu_dashboard_btn')
        self.product_btn = self.findChild(QPushButton, 'menu_product_btn')
        self.home_btn = self.findChild(QPushButton, 'menu_home_btn')

        self.dashboard_btn.clicked.connect(self.switch_dashboard_page)
        self.product_btn.clicked.connect(self.switch_product_page)
        self.home_btn.clicked.connect(self.switch_home_page)

        """self.dashbaord_icon = QIcon("assets/cross.svg")
        self.inventory_icon = QIcon("assets/cross.svg")

        # Create a button with icon only for both states
        self.dashboard_btn = QPushButton(self.dashbaord_icon, "")
        self.inventory_btn = QPushButton(self.inventory_icon, "")
        self.dashboard_btn.setCheckable(True)
        self.inventory_btn.setCheckable(True)
        self.dashboard_btn.setIconSize(self.dashboard_btn.sizeHint())  # Set the icon size to match the button size
        self.inventory_btn.setIconSize(self.inventory_btn.sizeHint())  # Set the icon size to match the button size
        self.dashboard_btn.setStyleSheet("text-align: left;")
        self.inventory_btn.setStyleSheet("text-align: left;")

        # Initially hide the button text
        self.dashboard_btn.setChecked(True)
        self.inventory_btn.setChecked(True)
        self.collapse_btn = False
        self.dashboard_btn.clicked.connect(self.toggle_button_text)
        self.inventory_btn.clicked.connect(self.toggle_button_text)

        padding = 10  # Adjust the padding as needed
        self.collapsed_width = self.dashboard_btn.sizeHint().width() + padding  # Set the width of the collapsed menu
        self.expanded_width = 200  # Set the width of the expanded menu

        self.menu_hidden = True

        self.push_btn.clicked.connect(self.toggle_menu)

        self.hide_menu()"""

        # self.button.setLayoutDirection(Qt.lef)
        """def init_menu(self):
        self.menu = SlidingMenu()
        self.menu_width = self.menu.width()
        self.menu_hidden = True

        self.inventory_btn.clicked.connect(self.toggle_menu)

        self.hide_menu()

        self.gridLayout.addWidget(self.menu, 0, 0)"""

    def init_customer(self):
        # Get reference to widgets
        self.customerComboBox = self.findChild(QComboBox, 'customerSelect')
        self.addCustomerButton = self.findChild(QPushButton, 'addCustomerBtn')


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

    def init_product_grid(self):
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

    def init_cart(self):
        self.clearBtn.clicked.connect(self.remove_all_from_cart)
        self.payBtn.clicked.connect(self.cart_checkout)

        # Set table headers
        headers = ['ID', 'Barcode', 'Product Name', 'Formula', 'Batch Code', 'Expiry Date', 'Quantity', 'Unit Rate',
                   'Net Price', 'Remove']
        Helper.set_table_headers(self.itemCartTable, headers)

        # Get references to the labels
        self.total_items_count_label = self.findChild(QLabel, 'totalItemsCountLabel')
        self.discount_input = self.findChild(QLineEdit, 'discountInput')
        self.cash_return_count_label = self.findChild(QLabel, 'netPriceCountLabel')
        self.price_count_label = self.findChild(QLabel, 'priceCountLabel')

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

    def execute_query(self, query):
        return execute_query(query, self.conn)

    def resizeEvent(self, event):
        # Override the resize event to update the product grid layout when the window is resized
        super().resizeEvent(event)
        self.update_product_grid_layout()

    def switch_dashboard_page(self):
        if not (self.main_stacked_widget.currentWidget() == self.dashboard_page):
            self.main_stacked_widget.setCurrentWidget(self.dashboard_page)

    def switch_product_page(self):
        if not (self.main_stacked_widget.currentWidget() == self.product_page):
            self.main_stacked_widget.setCurrentWidget(self.product_page)

    def switch_home_page(self):
        if not (self.main_stacked_widget.currentWidget() == self.home_page):
            self.main_stacked_widget.setCurrentWidget(self.home_page)

    def toggle_button_text(self):
        if self.collapse_btn:
            self.dashboard_btn.setIcon(self.dashbaord_icon)
            self.dashboard_btn.setText("")
            self.inventory_btn.setIcon(self.inventory_icon)
            self.inventory_btn.setText("")
        else:
            self.dashboard_btn.setIcon(self.dashbaord_icon)
            self.dashboard_btn.setText("Dashboard")
            self.inventory_btn.setIcon(self.inventory_icon)
            self.inventory_btn.setText("Inventory")

    def toggle_menu(self):
        if self.menu_hidden:
            self.show_menu()
        else:
            self.hide_menu()
        self.toggle_button_text()

    def show_menu(self):
        self.menu_animation = QPropertyAnimation(self.main_menu_widget, b"minimumWidth")
        self.menu_animation.setDuration(300)
        self.menu_animation.setStartValue(self.collapsed_width)
        self.menu_animation.setEndValue(self.expanded_width)
        self.menu_animation.start()

        # Toggle the button text and icon
        self.dashboard_btn.setChecked(False)
        self.inventory_btn.setChecked(False)
        self.collapse_btn = False
        self.menu_hidden = False

    def hide_menu(self):
        self.menu_animation = QPropertyAnimation(self.main_menu_widget, b"minimumWidth")
        self.menu_animation.setDuration(300)
        self.menu_animation.setStartValue(self.expanded_width)
        self.menu_animation.setEndValue(self.collapsed_width)
        self.menu_animation.start()

        # Toggle the button text and icon
        self.dashboard_btn.setChecked(True)
        self.inventory_btn.setChecked(True)
        self.collapse_btn = True

        self.menu_hidden = True

    def fetch_all(self, table):
        # Fetch all products from the database
        query = f"SELECT * FROM {table}"
        return self.execute_query(query)

    def get_expiry_date_for_batch(self, product_id, batch_code):
        for product in self.product_list:
            if product_id == product.ID:
                if product.batches:
                    for batch in product.batches:
                        if batch_code == batch.batch_code:
                            return batch.expiry_date

    def get_batch_id(self, product_id, batch_code):
        for product in self.product_list:
            if product_id == product.ID:
                if product.batches:
                    for batch in product.batches:
                        if batch_code == batch.batch_code:
                            return batch.ID

    def add_to_cart(self, product):
        # Check if the item is already in the cart
        if product.ID in self.cart_items:
            # If yes, increment the quantity
            self.cart_items[product.ID]['quantity'] += 1
            self.cart_items[product.ID]['netPrice'] += self.cart_items[product.ID]['price']
        else:
            # If not, add it to the cart with quantity 1
            self.cart_items[product.ID] = {'barcode': product.barcode, 'name': product.name, 'formula': product.formula, 'batches': product.batches, 'quantity': 1, 'price': product.salesPrice, 'netPrice': product.salesPrice}

        # Update the cart table
        self.update_cart_table()

        # Update the total price labels
        self.update_total_price_labels()

        # print(self.cart_items)

    def update_cart_table(self):
        # Clear the cart table
        self.itemCartTable.setRowCount(0)

        # Populate the cart table with items, quantities, and price
        for productID, details in self.cart_items.items():
            row_position = self.itemCartTable.rowCount()
            self.itemCartTable.insertRow(row_position)

            # Add remove button (cross icon)
            remove_button = QPushButton()
            remove_button.setIcon(QIcon('assets/cross.svg'))  # Replace with the path to your cross icon
            remove_button.clicked.connect(lambda _, row=row_position: self.remove_from_cart(row))

            # Set button properties to make it look flush
            remove_button.setStyleSheet("background-color: transparent; border: none;")

            # Set the remove button as the widget for the remove column
            self.itemCartTable.setCellWidget(row_position, 9, remove_button)

            # Set the product name
            self.itemCartTable.setItem(row_position, 0, QTableWidgetItem(str(productID)))
            self.itemCartTable.setItem(row_position, 1, QTableWidgetItem(str(details['barcode'])))
            self.itemCartTable.setItem(row_position, 2, QTableWidgetItem(details['name']))
            self.itemCartTable.setItem(row_position, 3, QTableWidgetItem(details['formula']))

            # Create a Combo Box for Batch Code
            batch_code_combo_box = QComboBox()

            # Add batch codes to the combo box
            for batch in details['batches']:
                # batch_code_combo_box.addItem(batch['batchCode'])
                batch_code_combo_box.addItem(batch.batch_code)

            # Set the current index of the combo box based on the selected batch code
            selected_batch_code = details.get('selectedBatchCode', '')
            if selected_batch_code:
                index = batch_code_combo_box.findText(selected_batch_code) # retrieving the index of the selected batch Code
            else:
                index = 0
            batch_code_combo_box.setCurrentIndex(index)
            details['selectedBatchID'] = details['batches'][index].ID

            if batch_code_combo_box.currentText():  # add expiry date if batch exists
                self.itemCartTable.setItem(row_position, 5, QTableWidgetItem(str(details["batches"][index].expiry_date)))

            # Connect the combo box signal to update the expiry date
            batch_code_combo_box.currentIndexChanged.connect(lambda _, row=row_position: self.update_expiry_date(row))

            # Update the 'selectedBatchCode' in the details dictionary
            details['selectedBatchCode'] = batch_code_combo_box.currentText()

            # Set the combo box as the widget for the batch code column
            self.itemCartTable.setCellWidget(row_position, 4, batch_code_combo_box)

            # Create a spin box for the quantity
            quantity_spinbox = QSpinBox()
            quantity_spinbox.setMinimum(1)  # Set the minimum value for the spin box
            quantity_spinbox.setValue(details['quantity'])  # Set the initial value
            quantity_spinbox.valueChanged.connect(self.update_quantity_in_cart)  # Connect the signal for value change

            # Set the spin box as the widget for the quantity column
            self.itemCartTable.setCellWidget(row_position, 6, quantity_spinbox)

            # Set the price
            self.itemCartTable.setItem(row_position, 7, QTableWidgetItem(str(details['price'])))

            totalPrice = "%.2f" % (details['quantity'] * details['price'])
            self.itemCartTable.setItem(row_position, 8, QTableWidgetItem(str(f"Rs {totalPrice}")))

    def update_expiry_date(self, row):
        # Get the selected batch code from the combo box
        batch_code_combo_box = self.itemCartTable.cellWidget(row, 4)
        selected_batch_code = batch_code_combo_box.currentText()

        product_id = int(self.itemCartTable.item(row, 0).text())

        # Get the expiry date based on the selected batch code
        # (You need to implement the logic to fetch the expiry date)
        expiry_date = self.get_expiry_date_for_batch(product_id, selected_batch_code)


        # Update the expiry date column in the cart table
        self.itemCartTable.setItem(row, 5, QTableWidgetItem(str(expiry_date)))

    def update_quantity_in_cart(self):
        # Update the quantity in the cart_items dictionary when the spin box value changes
        for row in range(self.itemCartTable.rowCount()):
            productID = int(self.itemCartTable.item(row, 0).text())
            quantity = self.itemCartTable.cellWidget(row, 6).value()
            price = self.itemCartTable.item(row, 7).text()

            totalPrice = "%.2f" % (quantity * float(price))
            self.itemCartTable.setItem(row, 8, QTableWidgetItem(str(f"Rs {totalPrice}")))
            self.cart_items[productID]['quantity'] = quantity
            self.cart_items[productID]['netPrice'] = totalPrice

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
        itemID = int(self.itemCartTable.item(row, 0).text())
        del self.cart_items[itemID]
        self.update_cart_table()
        self.update_total_price_labels()

    def remove_all_from_cart(self):
        for i in range(len(self.cart_items)):
            itemID = int(self.itemCartTable.item(i, 0).text())
            del self.cart_items[itemID]
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

    def cart_checkout(self):
        if self.cart_items:
            if self.customerComboBox.currentIndex != -1:
                customer_name = self.customerComboBox.currentText()
                customer_id = self.find_customer_id(customer_name)
                total_price = float(self.cash_return_count_label.text().split()[-1])
                total_items = int(self.total_items_count_label.text())
                current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                query = f"INSERT INTO Sales (CustomerID, SaleDate, TotalPrice, TotalItems) VALUES ({customer_id}, '{current_date}', {total_price}, {total_items})"
                checkout_success = execute_query_with_status(query, self.conn)

                successDialog = QMessageBox()
                if checkout_success:
                    sales_id = self.fetch_new_sale_id()
                    self.update_sale_details(sales_id)
                    self.remove_all_from_cart()
                    successDialog.setText("Payment Success")

                else:
                    successDialog.setText("Payment Failed")
                successDialog.exec_()

    def fetch_new_sale_id(self):
        query_sales_id = "SELECT LAST_INSERT_ID() AS NewSalesID"
        result = execute_query(query_sales_id, self.conn)
        return result[0]['NewSalesID']

    def update_sale_details(self, sale_id):
        # Iterate through the cart items and insert into SaleItems table
        # i = 0
        for product_id, details in self.cart_items.items():
            quantity = details['quantity']
            sales_price = details['price']
            net_price = details['netPrice']
            batch_id = details['selectedBatchID']

            # Insert statement for each item in the sale
            sale_item_query = f"INSERT INTO SaleDetails (SaleID, BatchID, ProductID, QuantitySold, SalePrice, NetPrice) " \
                              f"VALUES ({sale_id}, {batch_id}, {product_id}, {quantity}, {sales_price}, {net_price})"

            # Execute the sale_item_query
            execute_query_with_status(sale_item_query, self.conn)
            # cursor.execute(sale_item_query)

    def find_customer_id(self, name):
        if name:
            for customer in self.customer_list:
                if name == customer.name:
                    return customer.ID

    def clear_product_view(self):
        # Clear the product view layout
        for i in reversed(range(self.productGridLayout.count())):
            widget = self.productGridLayout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

    def display_default_products(self):
        # Sample data - replace this with your actual data retrieval logic
        # default_query = "SELECT * FROM pharmacy_table LIMIT 20"
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
        self.display_search_results(self.product_list)

    def start_product_search_timer(self):
        # Start the timer when text is changed
        self.product_search_timer.start(300)  # Adjust the delay (milliseconds) as needed

    def delayed_search_product(self):
        # Called when the timer times out (user has stopped typing)
        self.search_product_dynamic()

    def update_product_grid_layout(self):
        # Calculate the number of columns based on the available width
        # available_width = self.productViewWidget.width()
        available_width = self.product_scroll_area.viewport().width()
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
        results = [product for product in self.product_list if search_term.lower() in product.name.lower()]
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
                product_widget = ProductWidget(product)
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

    def fetch_customer_names(self, customer_list):
        customer_names = [customer.name for customer in customer_list]
        return customer_names

        """# Define the base query to fetch customer names
        # base_query = "SELECT DISTINCT Name FROM Customers"

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
            return []"""

    def populate_customer_names(self, search_term=None):
        all_customers = self.fetch_all(CUSTOMERS_TABLE)
        self.customer_list = []
        for customer in all_customers:
            self.customer_list.append(
                Customer(customer["CustomerID"], customer["Name"], customer["Address"], customer["Contact"]))

        # Fetch the list of customer names from the database based on the search term
        customer_names = self.fetch_customer_names(self.customer_list)

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
