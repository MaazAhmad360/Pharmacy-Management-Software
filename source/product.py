# source/product.py
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
        self.creationDate = creationDate
        self.manufacturer_id = int(manufacturer_id)

        # attributed data from other tables
        self.batches = []

    def add_batch(self, batch):
        self.batches.append(batch)