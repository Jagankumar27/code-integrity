class Inventory:
    def __init__(self):
        self.items = {}

    def add(self, name, qty):
        self.items[name] = self.items.get(name, 0) + qty

    def remove(self, name, qty):
        if name not in self.items or self.items[name] < qty:
            raise ValueError("not enough stock")
        self.items[name] -= qty

    def report(self):
        for name, qty in sorted(self.items.items()):
            print(f"{name}: {qty}")

inv = Inventory()
inv.add("pen", 10)
inv.remove("pen", 3)
inv.report()
