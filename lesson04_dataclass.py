from datetime import date, timedelta
import random
from dataclasses import dataclass

# Base class for all mooncakes - this is like a template that defines what all mooncakes have
# The @dataclass decorator automatically creates methods like __init__, __repr__, and __eq__
@dataclass
class BaseMoonCake:
    # These are the fields (attributes) that every mooncake will have
    name: str                    # Required: the name of the mooncake
    price: float                 # Required: how much it costs
    size: str = 'regular'        # Optional: size defaults to 'regular' if not specified
    is_vegetarian: bool = False  # Optional: defaults to False (not vegetarian)
    discount: float = 0.0        # Optional: discount percentage (0.0 = no discount, 0.1 = 10% off)
    expiry_date: date = date.today() + timedelta(days=365)  # Optional: expires in 1 year from today

# VegMoonCake inherits from BaseMoonCake - it gets all the same fields as BaseMoonCake
# This means VegMoonCake has: name, price, size, is_vegetarian, discount, expiry_date
@dataclass
class VegMoonCake(BaseMoonCake):
    # We override the is_vegetarian field to always be True for vegetarian mooncakes
    is_vegetarian: bool = True  # This overrides the parent class default of False

# LotusSeedMoonCake also inherits from BaseMoonCake - it gets all BaseMoonCake fields
# Plus it adds its own special field for egg yolks
@dataclass
class LotusSeedMoonCake(BaseMoonCake):
    # This is a new field that only LotusSeedMoonCake has
    egg_yolks: int = 1  # How many egg yolks are in this mooncake (defaults to 1)


# ShoppingCart class to manage a collection of mooncakes
# This is a regular class (not a dataclass) because it has complex methods
class ShoppingCart:
    # Constructor - runs when we create a new ShoppingCart
    def __init__(self):
        # Dictionary to store mooncakes: key = unique number, value = mooncake object
        self.items: dict[int, BaseMoonCake] = {}
        # Counter to create unique keys when adding items (starts at 0)
        self.sequence: int = 0

    # Method to add a mooncake to the cart
    def add(self, item: BaseMoonCake):
        self.sequence += 1  # Get the next unique number (1, 2, 3, etc.)
        self.items[self.sequence] = item  # Store the mooncake with this unique number as the key

    # Method to remove a mooncake from the cart using its key
    def remove(self, key: int):
        if key in self.items:  # Check if this key exists in our dictionary
            del self.items[key]  # Remove the mooncake with this key

    # String representation of the ShoppingCart - this is what gets printed
    def __str__(self):
        output = ""  # Start with an empty string
        # Go through each item in the cart and add its details to our output string
        for k, v in self.items.items():  # k = key (number), v = value (mooncake object)
            # Format: (key) name (size) - price (discount percentage)
            output += f"({k}) {v.name} ({v.size}) - {v.price:.2f} (Discount: {v.discount:.0%})\n"
        return "\n" + output  # Return the formatted string with a newline at the start

    # Method to get the number of items in the cart
    # This allows us to use len(cart) to get the number of items
    def __len__(self):
        return len(self.items)  # Return the number of items in our dictionary

    # Method to calculate the total price of all items in the cart
    def get_total_price(self) -> float:
        total_price = 0.0  # Start with zero
        # Go through each mooncake in the cart
        for item in self.items.values():  # Get all the mooncake objects
            # Calculate price after discount: original_price * (1 - discount_percentage)
            # Example: $10 with 20% discount = $10 * (1 - 0.2) = $10 * 0.8 = $8
            total_price += item.price * (1 - item.discount)
        return total_price  # Return the final total


# Create 5 Lotus Seed Moon Cakes with varying prices and 1 or 2 egg yolks, and assign random discounts
lotus_moon_cakes = []  # Empty list to store our mooncakes
for i in range(5):  # Loop 5 times (i = 0, 1, 2, 3, 4)
    # Create a dictionary with all the data for this mooncake
    cake_data = {
        "name": f"Lotus_{i}",  # Name will be "Lotus_0", "Lotus_1", etc.
        "price": 10.0 + i,     # Price will be 10.0, 11.0, 12.0, 13.0, 14.0
        "egg_yolks": i % 2 + 1,  # Will be 1 or 2 egg yolks (alternating)
        "discount": random.randrange(0, 31, 5) / 100.0  # Random discount: 0%, 5%, 10%, 15%, 20%, 25%, or 30%
    }
    # Create the mooncake object using the dictionary data
    # The ** unpacks the dictionary into keyword arguments
    cake = LotusSeedMoonCake(**cake_data)
    lotus_moon_cakes.append(cake)  # Add this mooncake to our list

# Create 5 Vegetarian Moon Cakes with varying prices and assign random discounts
veg_moon_cakes = []  # Empty list to store our vegetarian mooncakes
for i in range(5):  # Loop 5 times (i = 0, 1, 2, 3, 4)
    # Create a dictionary with all the data for this vegetarian mooncake
    cake_data = {
        "name": f"Veg_{i}",  # Name will be "Veg_0", "Veg_1", etc.
        "price": 8.0 + i,    # Price will be 8.0, 9.0, 10.0, 11.0, 12.0
        "discount": random.randrange(0, 31, 5) / 100.0  # Random discount: 0%, 5%, 10%, 15%, 20%, 25%, or 30%
    }
    # Create the vegetarian mooncake object using the dictionary data
    # The ** unpacks the dictionary into keyword arguments
    cake = VegMoonCake(**cake_data)
    veg_moon_cakes.append(cake)  # Add this mooncake to our list

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