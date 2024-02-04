# source/product_group.py
class ProductGroup:
    def __init__(self, ID, name, total_products):
        self.ID = int(ID)
        self.name = name
        self.total_products = int(total_products)