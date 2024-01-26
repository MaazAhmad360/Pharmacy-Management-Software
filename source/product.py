# source/product.py
from datetime import datetime


class Product:
    def __init__(self, ID, barcode, name, group, description, purchasePrice, salesPrice, totalStock, formula, minStock, maxStock, creationDate, manufacturer_id):
        # basic product attributes
        self.ID = int(ID)
        self.barcode = int(barcode)
        self.name = name
        self.group = group
        self.description = description
        self.purchasePrice = float(purchasePrice)
        self.salesPrice = float(salesPrice)
        self.totalStock = int(totalStock)
        self.formula = formula
        self.minStock = int(minStock)
        self.maxStock = int(maxStock)
        # self.creationDate = datetime.strptime(creationDate, "%Y-%m-%d")
        self.creationDate =creationDate
        self.manufacturer_id = int(manufacturer_id)

        # attributed data from other tables
        self.batches = []
        self.earliest_expiry_date = None

    def add_batch(self, batch):
        self.batches.append(batch)
        self.update_expiry_date()

    def update_expiry_date(self):
        self.earliest_expiry_date = min(batch.expiry_date for batch in self.batches)