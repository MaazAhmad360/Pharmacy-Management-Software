# add_customer_dialog.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox, QInputDialog
from source.data_manager import DataManager
from source.product import Product
from datetime import datetime
from source.product_group import ProductGroup


class ProductDialog(QDialog):
    def __init__(self, parent=None, product= None):
        super().__init__(parent)

        if product:
            self.setWindowTitle("Edit Product")
        else:
            self.setWindowTitle("Add New Product")

        self.data_manager = DataManager()

        self.name_label = QLabel("Name:")
        self.name_input = QLineEdit()

        self.barcode_label = QLabel("Barcode:")
        self.barcode_input = QLineEdit()

        self.description_label = QLabel("Description:")
        self.description_input = QLineEdit()

        self.purchase_price_label = QLabel("Purcahase Price:")
        self.purchase_price_input = QLineEdit()

        self.markup_price_label = QLabel("Markup:")
        self.markup_price_input = QLineEdit()

        self.sales_price_label = QLabel("Sales Price:")
        self.sales_price_input = QLineEdit()

        self.min_stock_label = QLabel("Minimum Stock:")
        self.min_stock_input = QLineEdit()

        self.max_stock_label = QLabel("Maximum Stock:")
        self.max_stock_input = QLineEdit()

        self.formula_label = QLabel("Formula:")
        self.formula_combo_box = QComboBox()

        # Fetch the list of customer names from the database based on the search term
        formula_names = [formula.name for formula in self.data_manager.formulas_list]

        # Clear existing items and populate the names in the combo box
        self.formula_combo_box.clear()
        self.formula_combo_box.addItems(formula_names)

        self.manufacturer_label = QLabel("Manufacturer:")
        self.manufacturer_combo_box = QComboBox()

        # Fetch the list of customer names from the database based on the search term
        manufacturer_names = [manufacturer.name for manufacturer in self.data_manager.manufacturers_list]

        # Clear existing items and populate the names in the combo box
        self.manufacturer_combo_box.clear()
        self.manufacturer_combo_box.addItems(manufacturer_names)

        self.group_label = QLabel("Group:")
        self.group_combo_box = QComboBox()

        # Fetch the list of customer names from the database based on the search term
        group_names = [group.name for group in self.data_manager.product_groups_list]

        # Clear existing items and populate the names in the combo box
        self.group_combo_box.clear()
        self.group_combo_box.addItems(group_names)

        self.shelf_label = QLabel("Shelf Tag:")
        self.shelf_combo_box = QComboBox()

        # Fetch the list of customer names from the database based on the search term
        shelf_tags = [shelf.tag for shelf in self.data_manager.shelf_list]

        # Clear existing items and populate the names in the combo box
        self.shelf_combo_box.clear()
        self.shelf_combo_box.addItems(shelf_tags)

        # Add buttons for adding new items
        self.add_group_button = QPushButton("Add Group")
        self.add_group_button.clicked.connect(self.show_add_group_dialog)

        self.add_formula_button = QPushButton("Add Formula")
        self.add_formula_button.clicked.connect(self.show_add_formula_dialog)

        self.add_manufacturer_button = QPushButton("Add Manufacturer")
        self.add_manufacturer_button.clicked.connect(self.show_add_manufacturer_dialog)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.accept)

        self.close_button = QPushButton("Cancel")
        self.close_button.clicked.connect(self.close)

        layout = QVBoxLayout()
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.barcode_label)
        layout.addWidget(self.barcode_input)
        layout.addWidget(self.description_label)
        layout.addWidget(self.description_input)
        layout.addWidget(self.group_label)
        layout.addWidget(self.group_combo_box)
        layout.addWidget(self.add_group_button)
        layout.addWidget(self.formula_label)
        layout.addWidget(self.formula_combo_box)
        layout.addWidget(self.add_formula_button)
        layout.addWidget(self.manufacturer_label)
        layout.addWidget(self.manufacturer_combo_box)
        layout.addWidget(self.add_manufacturer_button)
        layout.addWidget(self.shelf_label)
        layout.addWidget(self.shelf_combo_box)
        layout.addWidget(self.purchase_price_label)
        layout.addWidget(self.purchase_price_input)
        # layout.addWidget(self.markup_price_label)
        # layout.addWidget(self.markup_price_input)
        layout.addWidget(self.sales_price_label)
        layout.addWidget(self.sales_price_input)
        layout.addWidget(self.min_stock_label)
        layout.addWidget(self.min_stock_input)
        layout.addWidget(self.max_stock_label)
        layout.addWidget(self.max_stock_input)
        layout.addWidget(self.save_button)
        layout.addWidget(self.close_button)

        self.setLayout(layout)

    def get_product_info(self):
        name = str(self.name_input.text())
        barcode = str(self.barcode_input.text())
        description = str(self.description_input.text())
        purchase_price = float(self.purchase_price_input.text()) if self.purchase_price_input.text() else 0.0
        sales_price = float(self.sales_price_input.text()) if self.sales_price_input.text() else 0.0
        min_stock = int(self.min_stock_input.text()) if self.min_stock_input.text() else 0
        max_stock = int(self.max_stock_input.text()) if self.max_stock_input.text() else 0

        # Validate sale price greater than purchase price
        if sales_price <= purchase_price:
            # You can handle the validation error here, like showing a message box
            error_dialog = QMessageBox()
            error_dialog.setText("Sale price must be greater than purchase price.")
            error_dialog.exec_()
            return None  # Return None to indicate validation failure

        product = Product(None, barcode, name, description, purchase_price, sales_price, 0, min_stock, max_stock, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        group_name = str(self.group_combo_box.currentText())
        group = next((group for group in self.data_manager.product_groups_list if str(group.name) == group_name), None)
        if group:
            group.total_products += 1
            product.add_product_group(group)

        formula_name = str(self.formula_combo_box.currentText())
        formula = next((formula for formula in self.data_manager.formulas_list if str(formula.name) == formula_name), None)
        if formula:
            product.add_formula(formula)

        manufacturer_name = str(self.manufacturer_combo_box.currentText())
        manufacturer = next((manufacturer for manufacturer in self.data_manager.manufacturers_list if str(manufacturer.name) == manufacturer_name), None)
        if manufacturer:
            product.add_manufacturer(manufacturer)

        shelf_tag = str(self.shelf_combo_box.currentText())
        shelf = next((shelf for shelf in self.data_manager.shelf_list if str(shelf.tag) == shelf_tag), None)
        if shelf:
            product.add_shelf(shelf)

        return product

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

"""    def get_product_info(self):
        name = str(self.name_input.text())
        barcode = str(self.barcode_input.text())
        description = str(self.description_input.text())
        purchase_price = float(self.purchase_price_input.text())
        sales_price = float(self.sales_price_input.text())
        min_stock = int(self.min_stock_input.text())
        max_stock = int(self.max_stock_input.text())

        product = Product(None, barcode, name, description if description else "", purchase_price, sales_price, 0, min_stock, max_stock, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

        group_name = str(self.group_combo_box.currentText())
        group = next((group for group in self.data_manager.product_groups_list if str(group.name) == group_name), None)
        group.total_products += 1
        product.add_product_group(group)

        formula_name = str(self.formula_combo_box.currentText())
        formula = next((formula for formula in self.data_manager.formulas_list if str(formula.name) == formula_name), None)
        product.add_formula(formula)

        manufacturer_name = str(self.manufacturer_combo_box.currentText())
        manufacturer = next((manufacturer for manufacturer in self.data_manager.manufacturers_list if str(manufacturer.name) == manufacturer_name), None)
        product.add_manufacturer(manufacturer)

        return product"""
