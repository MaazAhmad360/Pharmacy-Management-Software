# source/product.py
from datetime import datetime


class Product:
    def __init__(self, ID, barcode, name, description, purchasePrice, salesPrice, totalStock, minStock, maxStock, creationDate):
        # basic product attributes
        self.ID = None
        if ID:
            self.ID = int(ID)
        self.barcode = int(barcode)
        self.name = name
        self.description = description
        self.purchasePrice = float(purchasePrice)
        self.salesPrice = float(salesPrice)
        self.totalStock = int(totalStock)
        self.minStock = int(minStock)
        self.maxStock = int(maxStock)
        # self.creationDate = datetime.strptime(creationDate, "%Y-%m-%d")
        self.creationDate = creationDate

        # attributed data from other tables
        self.shelf = None
        self.group = None
        self.manufacturer = None
        self.formula = None
        self.batches = []
        self.earliest_expiry_date = None

    def add_manufacturer(self, manufacturer):
        self.manufacturer = manufacturer

    def add_formula(self, formula):
        self.formula = formula

    def add_product_group(self, product_group):
        self.group = product_group

    def add_shelf(self, shelf):
        self.shelf = shelf

    def add_batch(self, batch):
        self.batches.append(batch)
        self.update_expiry_date()
        self.sort_batches_by_expiry_date()

    def sort_batches_by_expiry_date(self):
        self.batches.sort(key=lambda x: x.expiry_date)

    def update_expiry_date(self):
        self.earliest_expiry_date = min(batch.expiry_date for batch in self.batches)