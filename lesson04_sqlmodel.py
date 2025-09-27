from datetime import date, timedelta, datetime
import random
from sqlmodel import SQLModel, Field, Session, create_engine, select
from typing import Optional

# Database configuration - choose one option
# Option 1: SQLite (file-based database)
DATABASE_URL_SQLITE = "sqlite:///./mooncakes.db"

# Option 2: PostgreSQL (replace with your actual connection string)
DATABASE_URL_POSTGRES = "postgresql://user:password@localhost:5432/mooncakes_db"

# Choose which database to use
DATABASE_URL = DATABASE_URL_SQLITE  # Change to DATABASE_URL_POSTGRES for PostgreSQL

# Base class for all mooncakes - this stores all mooncake types in one table
# Using SQLModel for automatic validation, serialization, and database integration
class MoonCake(SQLModel, table=True):
    # Primary key for database
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Type field to distinguish between different mooncake types
    type: str = Field(..., description="Type of mooncake (veg, lotus, etc.)")
    
    # These are the fields (attributes) that every mooncake will have
    name: str = Field(..., description="The name of the mooncake")
    price: float = Field(..., gt=0, description="Price must be greater than 0")
    size: str = Field(default='regular', description="Size of the mooncake")
    is_vegetarian: bool = Field(default=False, description="Whether the mooncake is vegetarian")
    discount: float = Field(default=0.0, ge=0.0, le=1.0, description="Discount percentage")
    expiry_date: date = Field(default_factory=lambda: date.today() + timedelta(days=365), description="Expiry date")
    
    # Field specific to lotus seed mooncakes (will be None for other types)
    egg_yolks: Optional[int] = Field(default=None, ge=0, le=10, description="Number of egg yolks (lotus seed only)")

# ShoppingCart class to manage a collection of mooncakes in the database
class ShoppingCart(SQLModel, table=True):
    # Primary key for database
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Timestamp when the cart was created
    created_at: datetime = Field(default_factory=datetime.now, description="When the cart was created")

# CartItem class to represent items in a shopping cart (junction table)
class CartItem(SQLModel, table=True):
    # Primary key for database
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # Foreign key to shopping cart
    cart_id: int = Field(foreign_key="shoppingcart.id", description="ID of the shopping cart")
    
    # Foreign key to mooncake
    mooncake_id: int = Field(foreign_key="mooncake.id", description="ID of the mooncake")
    
    # Quantity of this mooncake in the cart
    quantity: int = Field(default=1, ge=1, description="Quantity of this mooncake in the cart")
    
    # Timestamp when the item was added to cart
    added_at: datetime = Field(default_factory=datetime.now, description="When the item was added to cart")

# Helper functions to create specific mooncake types
def create_veg_mooncake(**data) -> MoonCake:
    """Create a vegetarian mooncake"""
    data['type'] = 'veg'
    data['is_vegetarian'] = True
    data.pop('egg_yolks', None)  # Remove egg_yolks if provided
    return MoonCake(**data)

def create_lotus_mooncake(**data) -> MoonCake:
    """Create a lotus seed mooncake"""
    data['type'] = 'lotus'
    data.setdefault('egg_yolks', 1)  # Default to 1 egg yolk
    return MoonCake(**data)

# Database setup and session management
def create_database():
    """Create the database and all tables"""
    engine = create_engine(DATABASE_URL, echo=True)  # echo=True shows SQL queries
    SQLModel.metadata.create_all(engine)
    return engine

def get_session(engine):
    """Get a database session"""
    return Session(engine)

# Shopping cart operations (database-based)
class ShoppingCartManager:
    """Manager class for shopping cart operations using database"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create_cart(self) -> ShoppingCart:
        """Create a new shopping cart"""
        cart = ShoppingCart()
        self.session.add(cart)
        self.session.commit()
        self.session.refresh(cart)
        return cart
    
    def add_to_cart(self, cart_id: int, mooncake_id: int, quantity: int = 1):
        """Add a mooncake to the cart"""
        # Check if item already exists in cart
        existing_item = self.session.exec(
            select(CartItem).where(
                CartItem.cart_id == cart_id,
                CartItem.mooncake_id == mooncake_id
            )
        ).first()
        
        if existing_item:
            # Update quantity if item already exists
            existing_item.quantity += quantity
        else:
            # Create new cart item
            cart_item = CartItem(
                cart_id=cart_id,
                mooncake_id=mooncake_id,
                quantity=quantity
            )
            self.session.add(cart_item)
        
        self.session.commit()
    
    def remove_from_cart(self, cart_id: int, mooncake_id: int):
        """Remove a mooncake from the cart"""
        cart_item = self.session.exec(
            select(CartItem).where(
                CartItem.cart_id == cart_id,
                CartItem.mooncake_id == mooncake_id
            )
        ).first()
        
        if cart_item:
            self.session.delete(cart_item)
            self.session.commit()
    
    def get_cart_items(self, cart_id: int):
        """Get all items in a cart with mooncake details"""
        return self.session.exec(
            select(CartItem).where(CartItem.cart_id == cart_id)
        ).all()
    
    def get_cart_total(self, cart_id: int) -> float:
        """Calculate the total price of all items in the cart"""
        cart_items = self.get_cart_items(cart_id)
        total_price = 0.0
        
        for item in cart_items:
            # Get the mooncake details
            mooncake = self.session.get(MoonCake, item.mooncake_id)
            if mooncake:
                # Calculate price after discount: original_price * (1 - discount_percentage) * quantity
                item_total = mooncake.price * (1 - mooncake.discount) * item.quantity
                total_price += item_total
        
        return total_price
    
    def get_cart_size(self, cart_id: int) -> int:
        """Get the number of items in the cart"""
        cart_items = self.get_cart_items(cart_id)
        return sum(item.quantity for item in cart_items)
    
    def display_cart(self, cart_id: int) -> str:
        """Get a string representation of the cart contents"""
        cart_items = self.get_cart_items(cart_id)
        output = ""
        
        for item in cart_items:
            # Get the mooncake details
            mooncake = self.session.get(MoonCake, item.mooncake_id)
            if mooncake:
                # Format: (item_id) name (size) - price (discount percentage) x quantity
                output += f"({item.id}) {mooncake.name} ({mooncake.size}) - {mooncake.price:.2f} (Discount: {mooncake.discount:.0%}) x {item.quantity}\n"
        
        return "\n" + output if output else "\n(Empty cart)"

# Create database and session
engine = create_database()
session = get_session(engine)
cart_manager = ShoppingCartManager(session)

# Create 5 Lotus Seed Moon Cakes with varying prices and 1 or 2 egg yolks, and assign random discounts
print("Creating Lotus Seed Moon Cakes in database...")
lotus_moon_cakes = []
for i in range(5):
    # Create a dictionary with all the data for this mooncake
    cake_data = {
        "name": f"Lotus_{i}",
        "price": 10.0 + i,
        "egg_yolks": i % 2 + 1,  # Will be 1 or 2 egg yolks (alternating)
        "discount": random.randrange(0, 31, 5) / 100.0
    }
    # Create the mooncake object using the helper function
    cake = create_lotus_mooncake(**cake_data)
    session.add(cake)
    session.commit()
    session.refresh(cake)
    lotus_moon_cakes.append(cake)

# Create 5 Vegetarian Moon Cakes with varying prices and assign random discounts
print("Creating Vegetarian Moon Cakes in database...")
veg_moon_cakes = []
for i in range(5):
    # Create a dictionary with all the data for this vegetarian mooncake
    cake_data = {
        "name": f"Veg_{i}",
        "price": 8.0 + i,
        "discount": random.randrange(0, 31, 5) / 100.0
    }
    # Create the vegetarian mooncake object using the helper function
    cake = create_veg_mooncake(**cake_data)
    session.add(cake)
    session.commit()
    session.refresh(cake)
    veg_moon_cakes.append(cake)

# Print details of the generated Lotus Seed Moon Cakes
print("\nLotus Seed Moon Cakes:")
for cake in lotus_moon_cakes:
    print(f"ID: {cake.id}, Name: {cake.name}, Type: {cake.type}, Price: {cake.price:.2f}, Egg Yolks: {cake.egg_yolks}, Discount: {cake.discount:.0%}")

# Print details of the generated Vegetarian Moon Cakes
print("\nVegetarian Moon Cakes:")
for cake in veg_moon_cakes:
    print(f"ID: {cake.id}, Name: {cake.name}, Type: {cake.type}, Price: {cake.price:.2f}, Vegetarian: {cake.is_vegetarian}, Discount: {cake.discount:.0%}")

# Create a new shopping cart instance in the database
cart = cart_manager.create_cart()
print(f"\nCreated shopping cart with ID: {cart.id}")

print("\nShopping Cart Activities:")

# Add items to the cart
cart_manager.add_to_cart(cart.id, lotus_moon_cakes[0].id)
print(f"Added {lotus_moon_cakes[0].name}. Cart: {cart_manager.display_cart(cart.id)}")

cart_manager.add_to_cart(cart.id, veg_moon_cakes[1].id)
print(f"Added {veg_moon_cakes[1].name}. Cart: {cart_manager.display_cart(cart.id)}")

cart_manager.add_to_cart(cart.id, lotus_moon_cakes[2].id)
print(f"Added {lotus_moon_cakes[2].name}. Cart: {cart_manager.display_cart(cart.id)}")

# Remove an item from the cart
cart_manager.remove_from_cart(cart.id, lotus_moon_cakes[0].id)
print(f"Removed {lotus_moon_cakes[0].name}. Cart: {cart_manager.display_cart(cart.id)}")

# Add more items to the cart
cart_manager.add_to_cart(cart.id, veg_moon_cakes[0].id)
print(f"Added {veg_moon_cakes[0].name}. Cart: {cart_manager.display_cart(cart.id)}")

cart_manager.add_to_cart(cart.id, lotus_moon_cakes[4].id)
print(f"Added {lotus_moon_cakes[4].name}. Cart: {cart_manager.display_cart(cart.id)}")

# Print the final number of items in the cart
print(f"\nFinal cart size: {cart_manager.get_cart_size(cart.id)}")
# Print the final contents of the cart
print(f"Final cart contents: {cart_manager.display_cart(cart.id)}")

# Print the total price of all items in the cart, formatted to two decimal places
print(f"\nTotal price of items in cart: {cart_manager.get_cart_total(cart.id):.2f}")

# Demonstrate SQLModel validation
print("\n=== SQLModel Validation Demo ===")

# Show model validation
print("Model validation example:")
try:
    # This will work fine
    valid_cake = create_lotus_mooncake(name="Test", price=15.0, egg_yolks=2)
    print(f"Valid cake created: {valid_cake.name}")
    
    # This will raise a validation error
    invalid_cake = create_lotus_mooncake(name="Test", price=-5.0, egg_yolks=15)
except Exception as e:
    print(f"Validation error (as expected): {e}")

# Demonstrate database queries
print("\n=== Database Query Demo ===")

# Query all mooncakes
all_mooncakes = session.exec(select(MoonCake)).all()
print(f"Total mooncakes in database: {len(all_mooncakes)}")

# Query vegetarian mooncakes only
veg_mooncakes = session.exec(select(MoonCake).where(MoonCake.is_vegetarian == True)).all()
print(f"Vegetarian mooncakes: {len(veg_mooncakes)}")

# Query mooncakes with discount > 10%
discounted_mooncakes = session.exec(select(MoonCake).where(MoonCake.discount > 0.1)).all()
print(f"Mooncakes with >10% discount: {len(discounted_mooncakes)}")

# Query lotus seed mooncakes
lotus_mooncakes = session.exec(select(MoonCake).where(MoonCake.type == 'lotus')).all()
print(f"Lotus seed mooncakes: {len(lotus_mooncakes)}")

# Close the session
session.close()