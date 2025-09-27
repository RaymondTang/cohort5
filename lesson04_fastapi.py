# Import standard Python libraries
from datetime import date  # For working with dates
import random  # For generating random numbers (used in sample data)
from typing import Optional, List  # For type hints - helps IDEs and makes code clearer

# Import FastAPI components
from fastapi import FastAPI, HTTPException, Depends  # Main web framework components
from sqlmodel import Session, select  # Database session and query tools
from pydantic import BaseModel  # For creating response models (data structures)

# Import our custom models and utilities from the SQLModel lesson
# These handle the database models and business logic for mooncakes and shopping carts
from lesson04_sqlmodel import (
    MoonCake,  # Database model for mooncake products
    ShoppingCart,  # Database model for shopping carts
    CartItem,  # Database model for items inside carts
    ShoppingCartManager,  # Business logic class for cart operations
    create_veg_mooncake,  # Helper function to create vegetarian mooncakes
    create_lotus_mooncake,  # Helper function to create lotus seed mooncakes
    create_database,  # Function to set up the database
    get_session  # Function to get database sessions
)

# Database setup using our existing configuration from lesson04_sqlmodel
# This creates the SQLite database and all the tables we need
engine = create_database()

# Note: We don't need separate request models because SQLModel serves as both
# database model AND API request/response model - this is one of SQLModel's benefits!

# Special response models for cart operations
# These contain computed fields (like totals) that aren't stored in the database
class CartItemResponse(BaseModel):
    """Response model for individual cart items with calculated totals"""
    id: int  # Unique identifier for this cart item
    mooncake: MoonCake  # Complete mooncake information (name, price, etc.)
    quantity: int  # How many of this mooncake are in the cart
    item_total: float  # Calculated total: price * (1 - discount) * quantity

class CartSummary(BaseModel):
    """Response model for complete cart information with all totals"""
    cart_id: int  # Which cart this summary is for
    items: List[CartItemResponse]  # List of all items in the cart
    total_items: int  # Total number of individual mooncakes in cart
    total_price: float  # Grand total price for the entire cart

# Create the main FastAPI application instance
# This is like the "main" object that handles all our web requests
app = FastAPI(
    title="MoonCake API",  # Shows up in the auto-generated documentation
    description="API for managing mooncakes and shopping cart"  # Also in docs
)

def get_db_session():
    """Get database session for dependency injection
    
    This is a 'dependency' - FastAPI will automatically call this function
    and provide the result to any endpoint that needs a database session.
    The 'yield' makes this a generator that properly closes the session afterward.
    """
    with get_session(engine) as session:
        yield session  # Provide the session to the endpoint
        # Session automatically closes when this function ends

def get_cart_manager(session: Session = Depends(get_db_session)) -> ShoppingCartManager:
    """Get shopping cart manager instance
    
    Another dependency that creates our cart manager.
    Notice how it depends on get_db_session - FastAPI handles this chain automatically!
    """
    return ShoppingCartManager(session)

@app.on_event("startup")
def on_startup():
    """This function runs once when the FastAPI server starts up
    
    We could put initialization code here, but our database tables
    are already created by the create_database() function above.
    """
    # Tables are already created by create_database()
    pass

# MOONCAKE CRUD ENDPOINTS
# CRUD = Create, Read, Update, Delete - the basic operations for any data

@app.post("/mooncakes/", response_model=MoonCake)
def create_mooncake(mooncake: MoonCake, session: Session = Depends(get_db_session)):
    """Create a new mooncake with validation based on type
    
    This endpoint accepts a POST request with mooncake data in JSON format.
    FastAPI automatically converts the JSON to a MoonCake object for us!
    """
    
    # Extract the data from the request, excluding fields we don't want to set manually
    cake_data = mooncake.dict(exclude={'id', 'type'})  # id = auto-generated, type = used to choose helper function
    
    # Use our helper functions to create the right type of mooncake
    # This ensures proper validation and default values for each type
    if mooncake.type == "veg":
        db_mooncake = create_veg_mooncake(**cake_data)  # ** unpacks the dictionary as function arguments
    elif mooncake.type == "lotus":
        db_mooncake = create_lotus_mooncake(**cake_data)
    else:
        # Return an HTTP 400 error if the type is invalid
        raise HTTPException(status_code=400, detail="Invalid type. Use 'veg' or 'lotus'")
    
    # Save the new mooncake to the database
    session.add(db_mooncake)  # Add to the session (like a shopping cart for database changes)
    session.commit()  # Actually save to the database
    session.refresh(db_mooncake)  # Get the updated version with the auto-generated ID
    return db_mooncake  # FastAPI automatically converts this to JSON for the response

@app.get("/mooncakes/", response_model=List[MoonCake])
def list_mooncakes(
    mooncake_type: Optional[str] = None,  # Query parameter: ?mooncake_type=lotus
    is_vegetarian: Optional[bool] = None,  # Query parameter: ?is_vegetarian=true
    session: Session = Depends(get_db_session)
):
    """List all mooncakes with optional filtering
    
    This endpoint supports filtering via query parameters:
    - GET /mooncakes/ - returns all mooncakes
    - GET /mooncakes/?mooncake_type=lotus - returns only lotus mooncakes
    - GET /mooncakes/?is_vegetarian=true - returns only vegetarian mooncakes
    - GET /mooncakes/?mooncake_type=veg&is_vegetarian=true - combines filters
    """
    # Start with a basic query to select all mooncakes
    statement = select(MoonCake)
    
    # Add filters if they were provided in the query parameters
    if mooncake_type:
        statement = statement.where(MoonCake.type == mooncake_type)
    if is_vegetarian is not None:  # Check 'is not None' because False is a valid value
        statement = statement.where(MoonCake.is_vegetarian == is_vegetarian)
    
    # Execute the query and get all results
    mooncakes = session.exec(statement).all()
    return mooncakes  # FastAPI converts the list to JSON automatically

@app.get("/mooncakes/{mooncake_id}", response_model=MoonCake)
def get_mooncake(mooncake_id: int, session: Session = Depends(get_db_session)):
    """Get a specific mooncake by ID
    
    This uses a path parameter: /mooncakes/123 where 123 is the mooncake_id
    FastAPI automatically extracts the ID from the URL and converts it to an integer
    """
    # Try to find the mooncake in the database
    mooncake = session.get(MoonCake, mooncake_id)
    if not mooncake:
        # Return HTTP 404 (Not Found) if the mooncake doesn't exist
        raise HTTPException(status_code=404, detail="Mooncake not found")
    return mooncake

@app.put("/mooncakes/{mooncake_id}", response_model=MoonCake)
def update_mooncake(
    mooncake_id: int, 
    mooncake_update: MoonCake, 
    session: Session = Depends(get_db_session)
):
    """Update a mooncake
    
    PUT requests are used to update existing resources.
    The client sends the complete updated mooncake data.
    """
    # First, find the existing mooncake
    mooncake = session.get(MoonCake, mooncake_id)
    if not mooncake:
        raise HTTPException(status_code=404, detail="Mooncake not found")
    
    # Get only the fields that were actually provided in the request
    # exclude_unset=True means only include fields that were explicitly set
    # We also exclude 'id' and 'type' because these shouldn't change after creation
    update_data = mooncake_update.dict(exclude_unset=True, exclude={'id', 'type'})
    
    # Update each field on the existing mooncake object
    for key, value in update_data.items():
        setattr(mooncake, key, value)  # setattr(obj, 'field_name', new_value)
    
    # Save the changes to the database
    session.add(mooncake)  # Mark as modified
    session.commit()  # Save changes
    session.refresh(mooncake)  # Get the latest version from database
    return mooncake

@app.delete("/mooncakes/{mooncake_id}")
def delete_mooncake(mooncake_id: int, session: Session = Depends(get_db_session)):
    """Delete a mooncake
    
    DELETE requests remove resources from the server.
    This will permanently remove the mooncake from the database.
    """
    # Find the mooncake to delete
    mooncake = session.get(MoonCake, mooncake_id)
    if not mooncake:
        raise HTTPException(status_code=404, detail="Mooncake not found")
    
    # Remove from database
    session.delete(mooncake)
    session.commit()  # Permanently delete from database
    
    # Return a success message (common pattern for DELETE operations)
    return {"message": "Mooncake deleted successfully"}

# SHOPPING CART ENDPOINTS
# These endpoints handle shopping cart operations like adding/removing items

@app.post("/carts/", response_model=dict)
def create_cart(cart_manager: ShoppingCartManager = Depends(get_cart_manager)):
    """Create a new shopping cart
    
    This creates an empty cart that customers can add mooncakes to.
    Returns the new cart's ID which is needed for subsequent operations.
    """
    cart = cart_manager.create_cart()  # Use our business logic class
    return {"cart_id": cart.id, "message": "Cart created successfully"}

@app.post("/carts/{cart_id}/add/{mooncake_id}")
def add_to_cart(
    cart_id: int,  # Path parameter: which cart to add to
    mooncake_id: int,  # Path parameter: which mooncake to add
    quantity: int = 1,  # Query parameter: how many to add (defaults to 1)
    cart_manager: ShoppingCartManager = Depends(get_cart_manager)
):
    """Add a mooncake to the shopping cart
    
    Example usage: POST /carts/1/add/5?quantity=3
    This adds 3 units of mooncake #5 to cart #1
    """
    # Validate that both the mooncake and cart exist before proceeding
    mooncake = cart_manager.session.get(MoonCake, mooncake_id)
    if not mooncake:
        raise HTTPException(status_code=404, detail="Mooncake not found")
    
    cart = cart_manager.session.get(ShoppingCart, cart_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    # Use our business logic to add the item to the cart
    cart_manager.add_to_cart(cart_id, mooncake_id, quantity)
    return {"message": f"Added {quantity} x {mooncake.name} to cart {cart_id}"}

@app.get("/carts/{cart_id}", response_model=CartSummary)
def get_cart(cart_id: int, cart_manager: ShoppingCartManager = Depends(get_cart_manager)):
    """Get shopping cart contents with total price calculation
    
    This returns a complete summary of the cart including:
    - All items in the cart with their details
    - Individual item totals (with discounts applied)
    - Overall cart totals
    """
    # Validate that the cart exists
    cart = cart_manager.session.get(ShoppingCart, cart_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    # Get cart data using our business logic methods
    cart_items = cart_manager.get_cart_items(cart_id)  # All items in the cart
    total_price = cart_manager.get_cart_total(cart_id)  # Grand total with discounts
    total_items = cart_manager.get_cart_size(cart_id)  # Total quantity of all items
    
    # Build the detailed response with full mooncake information
    items_response = []
    for cart_item in cart_items:
        # Get the full mooncake details for each cart item
        mooncake = cart_manager.session.get(MoonCake, cart_item.mooncake_id)
        if mooncake:
            # Calculate the total for this specific item (price * discount * quantity)
            item_total = mooncake.price * (1 - mooncake.discount) * cart_item.quantity
            items_response.append(CartItemResponse(
                id=cart_item.id,
                mooncake=mooncake,  # Include complete mooncake information
                quantity=cart_item.quantity,
                item_total=item_total
            ))
    
    # Return the complete cart summary
    return CartSummary(
        cart_id=cart_id,
        items=items_response,
        total_items=total_items,
        total_price=total_price
    )

@app.get("/carts/{cart_id}/total")
def get_cart_total(cart_id: int, cart_manager: ShoppingCartManager = Depends(get_cart_manager)):
    """Get cart total price (with discounts applied)
    
    This is a simpler endpoint that just returns the total price,
    useful when you don't need the full cart details.
    """
    # Validate that the cart exists
    cart = cart_manager.session.get(ShoppingCart, cart_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    # Get the total price with all discounts applied
    total_price = cart_manager.get_cart_total(cart_id)
    return {"cart_id": cart_id, "total_price": round(total_price, 2)}  # Round to 2 decimal places

@app.delete("/carts/{cart_id}/items/{mooncake_id}")
def remove_from_cart(
    cart_id: int, 
    mooncake_id: int, 
    cart_manager: ShoppingCartManager = Depends(get_cart_manager)
):
    """Remove a mooncake from the shopping cart
    
    This completely removes all quantities of the specified mooncake from the cart.
    Example: DELETE /carts/1/items/5 removes all of mooncake #5 from cart #1
    """
    # Validate that the cart exists
    cart = cart_manager.session.get(ShoppingCart, cart_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    # Use business logic to remove the item from the cart
    cart_manager.remove_from_cart(cart_id, mooncake_id)
    return {"message": f"Removed mooncake {mooncake_id} from cart {cart_id}"}

@app.get("/carts/", response_model=List[dict])
def list_carts(session: Session = Depends(get_db_session)):
    """List all shopping carts
    
    This is useful for administrative purposes to see all carts in the system.
    Returns basic information about each cart (ID and creation time).
    """
    carts = session.exec(select(ShoppingCart)).all()
    # Return a simplified view of each cart
    return [{"cart_id": cart.id, "created_at": cart.created_at} for cart in carts]

# UTILITY ENDPOINTS
# These are helper endpoints for testing and demonstration

@app.post("/init-sample-data")
def initialize_sample_data(session: Session = Depends(get_db_session)):
    """Initialize sample data for testing and demonstration
    
    This endpoint clears all existing data and creates fresh sample mooncakes and a cart.
    Useful for resetting the database to a known state for testing.
    """
    
    # Clear all existing data (in the right order to avoid foreign key conflicts)
    # First remove cart items (they reference both carts and mooncakes)
    existing_cart_items = session.exec(select(CartItem)).all()
    for item in existing_cart_items:
        session.delete(item)
    
    # Then remove carts
    existing_carts = session.exec(select(ShoppingCart)).all()
    for cart in existing_carts:
        session.delete(cart)
    
    # Finally remove mooncakes
    existing_mooncakes = session.exec(select(MoonCake)).all()
    for cake in existing_mooncakes:
        session.delete(cake)
    
    session.commit()  # Save the deletions
    
    # Create 5 Lotus Seed mooncakes with varying properties
    lotus_cakes = []
    for i in range(5):
        cake_data = {
            "name": f"Lotus_{i}",  # Names like Lotus_0, Lotus_1, etc.
            "price": 10.0 + i,  # Prices from $10 to $14
            "egg_yolks": i % 2 + 1,  # Alternates between 1 and 2 egg yolks
            "discount": random.randrange(0, 31, 5) / 100.0  # Random discount 0%, 5%, 10%, ..., 30%
        }
        cake = create_lotus_mooncake(**cake_data)  # Use our helper function
        session.add(cake)
        lotus_cakes.append(cake)
    
    # Create 5 Vegetarian mooncakes with varying properties
    veg_cakes = []
    for i in range(5):
        cake_data = {
            "name": f"Veg_{i}",  # Names like Veg_0, Veg_1, etc.
            "price": 8.0 + i,  # Prices from $8 to $12 (cheaper than lotus)
            "discount": random.randrange(0, 31, 5) / 100.0  # Random discount
        }
        cake = create_veg_mooncake(**cake_data)  # Use our helper function
        session.add(cake)
        veg_cakes.append(cake)
    
    session.commit()  # Save all the new mooncakes to the database
    
    # Create a sample shopping cart and add some items to demonstrate functionality
    cart_manager = ShoppingCartManager(session)
    sample_cart = cart_manager.create_cart()
    
    # Add a variety of items to the sample cart if we have mooncakes
    if lotus_cakes and veg_cakes:
        cart_manager.add_to_cart(sample_cart.id, lotus_cakes[0].id)  # Add first lotus cake
        cart_manager.add_to_cart(sample_cart.id, veg_cakes[1].id)   # Add second veg cake
        cart_manager.add_to_cart(sample_cart.id, lotus_cakes[2].id) # Add third lotus cake
    
    # Return summary of what was created
    return {
        "message": "Sample data initialized",
        "lotus_cakes": len(lotus_cakes),
        "veg_cakes": len(veg_cakes),
        "sample_cart_id": sample_cart.id
    }

# ROOT ENDPOINT - API Documentation
@app.get("/")
def root():
    """Root endpoint that provides API documentation and usage guide
    
    This is what users see when they visit the base URL of our API.
    It provides a helpful overview of available endpoints and how to use them.
    """
    return {
        "message": "MoonCake API - Built with FastAPI and SQLModel",
        "endpoints": {
            "mooncakes": "/mooncakes/ (CRUD operations)",
            "create_cart": "/carts/ (POST)",
            "list_carts": "/carts/ (GET)",
            "cart_operations": "/carts/{cart_id}",
            "add_to_cart": "/carts/{cart_id}/add/{mooncake_id}",
            "docs": "/docs",  # FastAPI auto-generates interactive documentation
            "init_sample_data": "/init-sample-data"
        },
        "workflow": [
            "1. POST /init-sample-data to create sample mooncakes",
            "2. POST /carts/ to create a cart",
            "3. POST /carts/{cart_id}/add/{mooncake_id} to add items",
            "4. GET /carts/{cart_id} to view cart with totals"
        ]
    }

# This block runs when the script is executed directly (not imported)
if __name__ == "__main__":
    try:
        # Try to start the development server using uvicorn
        import uvicorn
        # host="0.0.0.0" makes the server accessible from other machines on the network
        # port=8000 is the default port for development
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except ImportError:
        # If uvicorn isn't installed, provide helpful instructions
        print("Uvicorn not installed. Install with: pip install uvicorn")
        print("Or run with: uvicorn lesson04.fastapi:app --reload")
        print("The --reload flag automatically restarts the server when code changes")
