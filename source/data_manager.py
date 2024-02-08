# data_manager.py
import pymysql
from source.globals import *
from source.database_helper import connect_to_database, execute_query
from source.product import Product
from source.vendor import Vendor
from source.manufacturer import Manufacturer
from source.formula import Formula
from source.batch import Batch
from source.customer import Customer
from source.product_group import ProductGroup
from source.shelf import Shelf


class DataManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataManager, cls).__new__(cls)
            # # Initialize your data lists here
            cls._instance.formulas_list = []
            cls._instance.product_groups_list = []
            cls._instance.manufacturers_list = []
            cls._instance.product_list = []
            cls._instance.customer_list = []
            cls._instance.vendor_list = []
            cls._instance.batch_list = []
            cls._instance.shelf_list = []
            cls._instance.conn = connect_to_database()
            cls._instance.initialize_data()
        return cls._instance

    def initialize_data(self):
        # Your existing initialization code goes here
        all_manufacturers = self.fetch_all(MANUFACTURERS_TABLE)
        # self.manufacturers_list = []
        for manufacturer in all_manufacturers:
            self.manufacturers_list.append(Manufacturer(manufacturer["ManufacturerID"], manufacturer["Name"]))

        # initializing manufacturers in a list
        all_formulas = self.fetch_all(FORMULAS_TABLE)
        # self.formulas_list = []
        for formula in all_formulas:
            self.formulas_list.append(Formula(formula["FormulaID"], formula["Name"]))

        all_shelf = self.fetch_all(SHELF_TABLE)
        # self.formulas_list = []
        for shelf in all_shelf:
            self.shelf_list.append(Shelf(shelf["ShelfID"], shelf["ShelfTag"]))

        # initializing manufacturers in a list
        all_product_group = self.fetch_all(PRODUCT_GROUPS_TABLE)
        # self.product_groups_list = []
        for product_group in all_product_group:
            self.product_groups_list.append(
                ProductGroup(product_group["GroupID"], product_group["Name"], product_group["TotalProducts"]))

        # initializing all products in a list
        all_products = self.fetch_all(PRODUCT_TABLE)  # loading all products in memory
        # self.product_list = []
        for product in all_products:
            self.product_list.append(
                Product(product["ProductID"], product["Barcode"], product["Name"],
                        product["Description"], product["PurchasePrice"], product["SalesPrice"],
                        product["TotalStock"], product["MinStock"], product["MaxStock"],
                        product["CreationDate"]))

            for manufacturer in self.manufacturers_list:  # associating the manufacturer with the appropriate product
                if product["ManufacturerID"] == manufacturer.ID:  # add a manufacturer if it referenced in Product
                    self.product_list[-1].add_manufacturer(manufacturer)

            for formula in self.formulas_list:  # associating the formula with the appropriate product
                if product["FormulaID"] == formula.ID:  # add a formula if it referenced in Product
                    self.product_list[-1].add_formula(formula)

            for product_group in self.product_groups_list:  # associating the formula with the appropriate product
                if product["ProductGroupID"] == product_group.ID:  # add a formula if it referenced in Product
                    self.product_list[-1].add_product_group(product_group)

            for shelf in self.shelf_list:
                if product["ShelfID"] == shelf.ID:
                    self.product_list[-1].add_shelf(shelf)

        # initialing all vendors in a list
        all_vendors = self.fetch_all(VENDORS_TABLE)
        # self.vendor_list = []
        for vendor in all_vendors:
            self.vendor_list.append(Vendor(vendor["VendorID"], vendor["Name"], vendor["Address"], vendor["City"], ))

        # initializing all batches in a list
        all_batches = self.fetch_all(BATCHES_TABLE)  # loading all batches in memory
        # self.batch_list = []
        for batch in all_batches:
            self.batch_list.append(
                Batch(batch["BatchID"], batch["BatchCode"], batch["ArrivalDate"], batch["ManufacturingDate"],
                      batch["ExpiryDate"], batch["Quantity"]))

            self.batch_list[-1].add_vendor(
                next((vendor for vendor in self.vendor_list if int(batch["VendorID"]) == vendor.ID),
                     None))  # find the matching vendorID from the vendorlist and reference it in the batch instance - same purpose as the one commented below
            """for vendor in self.vendor_list:  # referencing the appropriate vendor through ID
                if int(batch["VendorID"]) is vendor.ID:
                    self.batch_list[-1].add_vendor(vendor)"""

            for product in self.product_list:  # associating the batch with the appropriate product
                if int(batch["ProductID"]) == product.ID:
                    product.add_batch(self.batch_list[-1])

        all_customers = self.fetch_all(CUSTOMERS_TABLE)
        # self.customer_list = []
        for customer in all_customers:
            self.customer_list.append(
                Customer(customer["CustomerID"], customer["Name"], customer["Address"], customer["Contact"]))

    def fetch_all(self, table):
        # Fetch all products from the database
        query = f"SELECT * FROM {table}"
        return self.execute_query(query)

    def execute_query(self, query):
        return execute_query(query, self.conn)

    def execute_modification_query(self, query):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query)
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error executing modification query: {e}")
            return False

    def fetch_new_id(self):
        query_sales_id = "SELECT LAST_INSERT_ID() AS NewEntry"
        result = execute_query(query_sales_id, self.conn)
        return result[0]['NewEntry']

    def execute_query_with_status(self, query):
        try:
            with self.conn.cursor() as cursor:
                cursor.execute(query)
                self.conn.commit()  # Commit the changes
                return True, cursor.fetchall()
        except pymysql.Error as e:
            # Attempt to reconnect if the error indicates a lost connection
            if e.args[0] == 2006:
                print("Reconnecting to the database...")
                self.conn.ping(reconnect=True)
                return self.execute_query_with_status(query)  # Retry the query
            else:
                print(f"Error executing query: {e}")
                return False, []