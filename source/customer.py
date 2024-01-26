# source/customer.py
class Customer:
    def __init__(self, ID, name, address, contact):
        self.ID = int(ID)
        self.name = name
        self.address = address
        self.contact = int(contact)
