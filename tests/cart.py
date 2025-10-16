class Cart:
    def __init__(self):
        self.items = []

    def add_item(self, name, price, quantity=1):
        self.items.append({"name": name, "price": price, "quantity": quantity})

    def total_items(self):
        return sum(item["quantity"] for item in self.items)

    def total_price(self):
        return sum(item["price"] * item["quantity"] for item in self.items)
