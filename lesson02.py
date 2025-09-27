from datetime import date, timedelta
import random

# Base class for all mooncakes
class BaseMoonCake:
    # Constructor to initialize a mooncake object
    def __init__(self, name: str, price: float, size: str = 'regular'):
        self.name: str = name # Name of the mooncake
        self.size: str = size # Size of the mooncake (e.g., 'regular', 'mini')
        self.price: float = price # Base price of the mooncake
        self.is_vegetarian: bool = False # Whether the mooncake is vegetarian
        self.discount: float = 0.0 # Discount percentage (e.g., 0.10 for 10% off)
        # Expiry date is set to one year from today
        self.expiry_date: date = date.today() + timedelta(days=365)

    # String representation of the MoonCake object
    def __str__(self):
        # Format the output to show name, size, price, discount, and expiry date
        return f"{self.name} ({self.size}) - {self.price:.2f} (Discount: {self.discount:.0%}) ({self.expiry_date.isoformat()})"

# VegMoonCake inherits from BaseMoonCake, meaning it gets all the properties of BaseMoonCake
class VegMoonCake(BaseMoonCake):
    # Constructor for VegMoonCake
    def __init__(self, name: str, price: float, size: str = 'regular'):
        # Call the constructor of the parent class (BaseMoonCake)
        super().__init__(name, price, size)
        self.is_vegetarian = True # Set to True as this is a vegetarian mooncake

    # String representation for VegMoonCake, overriding the parent's __str__
    def __str__(self):
        return f"{self.name}[V] ({self.size}) - {self.price:.2f} (Discount: {self.discount:.0%}) ({self.expiry_date.isoformat()})"

# LotusSeedMoonCake also inherits from BaseMoonCake
class LotusSeedMoonCake(BaseMoonCake):
    # Constructor for LotusSeedMoonCake
    def __init__(self, name: str, price: float, egg_yolks: int, size: str = 'regular'):
        # Call the parent class constructor
        super().__init__(name, price, size)
        self.egg_yolks: int = egg_yolks # Number of egg yolks in the mooncake

    # String representation for LotusSeedMoonCake
    def __str__(self):
        return f"{self.name}[L] ({self.size}) - {self.price:.2f} (Discount: {self.discount:.0%}) ({self.expiry_date.isoformat()})"

# ShoppingCart class to manage a collection of mooncakes
class ShoppingCart:
    # Constructor for ShoppingCart
    def __init__(self):
        self.items: dict[int, BaseMoonCake] = {} # Dictionary to store mooncakes with a unique key
        self.sequence: int = 0 # Counter for unique keys when adding items

    # Method to add a mooncake to the cart
    def add(self, item: BaseMoonCake):
        self.sequence += 1 # Increment sequence for a new unique key
        self.items[self.sequence] = item # Add the mooncake to the dictionary

    # Method to remove a mooncake from the cart using its key
    def remove(self, key: int):
        if key in self.items:
            del self.items[key] # Remove item if key exists

    # String representation of the ShoppingCart
    def __str__(self):
        output = "" # Initialize an empty string for output
        # Iterate through items and append their details to the output string
        for k, v in self.items.items():
            output += f"({k}) {v.name} ({v.size}) - {v.price:.2f} (Discount: {v.discount:.0%})\n"
        return "\n"+output # Return the formatted string

    # Method to get the number of items in the cart
    def __len__(self):
        return len(self.items)

    # Method to calculate the total price of all items in the cart
    def get_total_price(self) -> float:
        total_price = 0.0 # Initialize total price
        # Sum up the price of each item, considering its discount
        for item in self.items.values():
            total_price += item.price * (1 - item.discount)
        return total_price # Return the total calculated price


# Create 5 Lotus Seed Moon Cakes with varying prices and 1 or 2 egg yolks, and assign random discounts
lotus_moon_cakes = []
for i in range(5):
    cake = LotusSeedMoonCake(f"Lotus_{i}", 10.0 + i, i % 2 + 1)
    cake.discount = random.randrange(0, 31, 5) / 100.0 # Random discount between 0% and 30% in 5% steps
    lotus_moon_cakes.append(cake)

# Create 5 Vegetarian Moon Cakes with varying prices and assign random discounts
veg_moon_cakes = []
for i in range(5):
    cake = VegMoonCake(f"Veg_{i}", 8.0 + i)
    cake.discount = random.randrange(0, 31, 5) / 100.0 # Random discount between 0% and 30% in 5% steps
    veg_moon_cakes.append(cake)

# Print details of the generated Lotus Seed Moon Cakes
print("Lotus Seed Moon Cakes:")
for cake in lotus_moon_cakes:
    print(cake)

# Print details of the generated Vegetarian Moon Cakes
print("\nVegetarian Moon Cakes:")
for cake in veg_moon_cakes:
    print(cake)


# Create a new shopping cart instance
cart = ShoppingCart()

print("\nShopping Cart Activities:")

# Add items to the cart
cart.add(lotus_moon_cakes[0]) # Add the first lotus mooncake
print(f"Added {lotus_moon_cakes[0].name}. Cart: {cart}")

cart.add(veg_moon_cakes[1]) # Add the second vegetarian mooncake
print(f"Added {veg_moon_cakes[1].name}. Cart: {cart}")

cart.add(lotus_moon_cakes[2]) # Add the third lotus mooncake
print(f"Added {lotus_moon_cakes[2].name}. Cart: {cart}")

# Remove an item from the cart
cart.remove(1) # Remove the item with key 1 (which was Lotus_0)
print(f"Removed item with key 1. Cart: {cart}")

# Add more items to the cart
cart.add(veg_moon_cakes[0]) # Add the first vegetarian mooncake
print(f"Added {veg_moon_cakes[0].name}. Cart: {cart}")

cart.add(lotus_moon_cakes[4]) # Add the fifth lotus mooncake
print(f"Added {lotus_moon_cakes[4].name}. Cart: {cart}")

# Print the final number of items in the cart
print(f"\nFinal cart size: {len(cart)}")
# Print the final contents of the cart
print(f"Final cart contents: {cart}")

# Print the total price of all items in the cart, formatted to two decimal places
print(f"\nTotal price of items in cart: {cart.get_total_price():.2f}")