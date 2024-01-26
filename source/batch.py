# source/batch.py
class Batch:
    def __init__(self, ID, batch_code, arrival_date, manufacturing_date, expiry_date, quantity):
        self.ID = int(ID)
        self.batch_code = batch_code
        self.arrival_date = arrival_date
        self.manufacturing_date = manufacturing_date
        self.expiry_date = expiry_date
        self.quantity = int(quantity)
        self.vendor = None

    def add_vendor(self, vendor):
        self.vendor = vendor

