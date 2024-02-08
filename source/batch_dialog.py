# add_customer_dialog.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox, QInputDialog, QDateEdit
from PyQt5.QtCore import QDate
from source.data_manager import DataManager
from source.product import Product
from datetime import datetime, date
from source.product_group import ProductGroup
from source.batch import Batch

class BatchDialog(QDialog):
    def __init__(self, parent=None, batch= None):
        super().__init__(parent)

        if batch:
            self.setWindowTitle("Edit Batch")
        else:
            self.setWindowTitle("Add New Batch")

        self.data_manager = DataManager()

        self.product_label = QLabel("Product:")
        self.product_combo_box = QComboBox()

        # Fetch the list of customer names from the database based on the search term
        product_names = [product.name for product in self.data_manager.product_list]

        # Clear existing items and populate the names in the combo box
        self.product_combo_box.clear()
        self.product_combo_box.addItems(product_names)

        self.code_label = QLabel("Batch Code:")
        self.code_input = QLineEdit()

        self.vendor_label = QLabel("Vendor:")
        self.vendor_input = QLineEdit()

        self.quantity_label = QLabel("Quantity:")
        self.quantity_input = QLineEdit()

        self.purchase_price_label = QLabel("Purcahase Price:")
        self.purchase_price_input = QLineEdit()

        self.markup_price_label = QLabel("Markup:")
        self.markup_price_input = QLineEdit()

        self.sales_price_label = QLabel("Sales Price:")
        self.sales_price_input = QLineEdit()

        self.arrival_date_label = QLabel("Arrival Date:")
        self.arrival_date_selector = QDateEdit(self)
        self.arrival_date_selector.setCalendarPopup(True)  # Enable the calendar popup
        self.arrival_date_selector.setDateRange(QDate(2000, 1, 1), QDate.currentDate())  # Optional: Set a date range
        self.arrival_date_selector.setDate(QDate.currentDate())

        self.manufacturing_date_label = QLabel("Manufacturing Date:")
        self.manufacturing_date_selector = QDateEdit(self)
        self.manufacturing_date_selector.setCalendarPopup(True)  # Enable the calendar popup
        self.manufacturing_date_selector.setDateRange(QDate(2000, 1, 1), QDate.currentDate())  # Optional: Set a date range
        self.manufacturing_date_selector.setDate(QDate.currentDate())

        self.expiry_date_label = QLabel("Expiry Date:")
        self.expiry_date_selector = QDateEdit(self)
        self.expiry_date_selector.setCalendarPopup(True)  # Enable the calendar popup
        # self.expiry_date_selector.setDateRange(QDate(2000, 1, 1), QDate.currentDate())  # Optional: Set a date range
        self.expiry_date_selector.setDate(QDate.currentDate())

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.accept)

        self.close_button = QPushButton("Cancel")
        self.close_button.clicked.connect(self.close)

        layout = QVBoxLayout()
        layout.addWidget(self.product_label)
        layout.addWidget(self.product_combo_box)
        layout.addWidget(self.code_label)
        layout.addWidget(self.code_input)
        layout.addWidget(self.vendor_label)
        layout.addWidget(self.vendor_input)
        layout.addWidget(self.arrival_date_label)
        layout.addWidget(self.arrival_date_selector)
        layout.addWidget(self.manufacturing_date_label)
        layout.addWidget(self.manufacturing_date_selector)
        layout.addWidget(self.expiry_date_label)
        layout.addWidget(self.expiry_date_selector)
        layout.addWidget(self.quantity_label)
        layout.addWidget(self.quantity_input)
        layout.addWidget(self.purchase_price_label)
        layout.addWidget(self.purchase_price_input)
        # layout.addWidget(self.markup_price_label)
        # layout.addWidget(self.markup_price_input)
        layout.addWidget(self.sales_price_label)
        layout.addWidget(self.sales_price_input)
        layout.addWidget(self.save_button)
        layout.addWidget(self.close_button)

        self.setLayout(layout)

    def add_new_batch(self):
        if self.product_combo_box.currentIndex() != -1:
            product = None
            if self.product_combo_box.currentText() == self.data_manager.product_list[self.product_combo_box.currentIndex()].name:
                product = self.data_manager.product_list[self.product_combo_box.currentIndex()]
            else:
                for p in self.data_manager.product_list:
                    if p.name == str(self.product_combo_box.currentText()):
                        product = p

            code = str(self.code_input.text())
            temp_arr = self.arrival_date_selector.date()
            arrival_date = datetime(temp_arr.year(), temp_arr.month(), temp_arr.day())
            temp_manu = self.manufacturing_date_selector.date()
            manufacturing_date = datetime(temp_manu.year(), temp_manu.month(), temp_manu.day())
            temp_exp = self.expiry_date_selector.date()
            exp_time = datetime.min.time()
            temp_expiry_date = datetime(temp_exp.year(), temp_exp.month(), temp_exp.day())
            expiry_date = datetime.combine(temp_expiry_date, exp_time)
            quantity = int(self.quantity_input.text())
            purchase_price = float(self.purchase_price_input.text()) if self.purchase_price_input.text() else 0.0
            sales_price = float(self.sales_price_input.text()) if self.sales_price_input.text() else 0.0


            arrival_date_str = arrival_date.strftime('%Y-%m-%d %H:%M:%S')
            manufacturing_date_str = manufacturing_date.strftime('%Y-%m-%d %H:%M:%S')
            expiry_date_str = expiry_date.strftime('%Y-%m-%d %H:%M:%S')

            # Validate sale price greater than purchase price
            if sales_price <= purchase_price:
                # You can handle the validation error here, like showing a message box
                error_dialog = QMessageBox()
                error_dialog.setText("Sale price must be greater than purchase price.")
                error_dialog.exec_()
                return None  # Return None to indicate validation failure

            # product = Product(None, barcode, name, description, purchase_price, sales_price, 0, min_stock, max_stock, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            # query = f"INSERT INTO Batches (BatchCode, ProductID, VendorID, ArrivalDate, ManufacturingDate, ExpiryDate, Quantity, PurchasePrice, SalePrice) VALUES ('{code}', '{product.ID}', '1', {arrival_date}', '{manufacturing_date}', '{expiry_date}', '{quantity}', '{purchase_price}', '{sales_price}')"
            query = f"INSERT INTO Batches (BatchCode, ProductID, VendorID, ArrivalDate, ManufacturingDate, ExpiryDate, Quantity, PurchasePrice, SalePrice) VALUES ('{code}', '{product.ID}', '1', '{arrival_date_str}', '{manufacturing_date_str}', '{expiry_date_str}', '{quantity}', '{purchase_price}', '{sales_price}')"
            success = self.data_manager.execute_query_with_status(query)

            if success:
                batch_id = self.data_manager.fetch_new_id()
                batch = Batch(batch_id, code, arrival_date, manufacturing_date, expiry_date, quantity)
                batch.add_sale_price(sales_price)
                batch.add_purchase_price(purchase_price)

                self.data_manager.batch_list.append(batch)
                for p in self.data_manager.product_list:
                    if p.ID == product.ID:
                        p.add_batch(batch)
                        p.totalStock += batch.quantity
                        p.salesPrice = batch.sale_price

                        # Update the product details in the database
                        update_query = f"UPDATE ProductDetails SET TotalStock = {p.totalStock}, SalesPrice = {p.salesPrice} WHERE ProductID = {p.ID}"
                        success = self.data_manager.execute_query_with_status(update_query)
                        if success:
                            print("Product details updated successfully.")
                        else:
                            print("Failed to update product details.")


    def show_add_group_dialog(self):
        group_name, ok = QInputDialog.getText(self, "Add Group", "Enter Group Name:")
        if ok and group_name:
            # Add the new group to the combo box
            self.group_combo_box.addItem(group_name)

            # self.data_manager.product_groups_list.append()

    def show_add_formula_dialog(self):
        formula_name, ok = QInputDialog.getText(self, "Add Formula", "Enter Formula Name:")
        if ok and formula_name:
            # Add the new formula to the combo box
            self.formula_combo_box.addItem(formula_name)

    def show_add_manufacturer_dialog(self):
        manufacturer_name, ok = QInputDialog.getText(self, "Add Manufacturer", "Enter Manufacturer Name:")
        if ok and manufacturer_name:
            # Add the new manufacturer to the combo box
            self.manufacturer_combo_box.addItem(manufacturer_name)