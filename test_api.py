#!/usr/bin/env python3
"""
Test script for the MoonCake FastAPI endpoints

This is a comprehensive test suite that validates all API functionality.
It demonstrates how to test REST APIs using the 'requests' library.

To use this script:
1. Start the FastAPI server: python lesson04_fastapi.py
2. Run this test script: python test_api.py

The script will test all endpoints and show you the responses.
"""

# Import libraries for making HTTP requests and handling data
import requests  # For making HTTP requests to our API
import json  # For pretty-printing JSON responses
from typing import Dict, Any  # For type hints

# Base URL where our API is running
# Change this if your API runs on a different host/port
BASE_URL = "http://localhost:8000"

def print_response(title: str, response: requests.Response):
    """Helper function to print API responses in a readable format
    
    This function takes a response from an API call and displays it nicely.
    It handles both successful responses (status < 400) and errors (status >= 400).
    
    Args:
        title: A descriptive name for the test being performed
        response: The HTTP response object from requests
    """
    print(f"\n{'='*50}")
    print(f"🧪 {title}")
    print(f"{'='*50}")
    print(f"Status: {response.status_code}")  # HTTP status code (200=OK, 404=Not Found, etc.)
    
    if response.status_code < 400:  # Success responses (200-399)
        try:
            # Try to parse the response as JSON and pretty-print it
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2, default=str)}")
        except:
            # If it's not JSON, just print the raw text
            print(f"Response: {response.text}")
    else:  # Error responses (400+)
        print(f"Error: {response.text}")
    
    return response  # Return the response so it can be used by the caller

def test_root_endpoint():
    """Test the root endpoint to see API info
    
    This is typically the first test to run - it checks if the API is running
    and returns basic information about available endpoints.
    """
    # Make a GET request to the root URL
    response = requests.get(f"{BASE_URL}/")
    return print_response("ROOT ENDPOINT", response)

def test_initialize_sample_data():
    """Initialize sample data for testing
    
    This sets up the database with sample mooncakes and a cart.
    It's useful to run this at the beginning of testing to ensure
    we have known data to work with.
    """
    # Make a POST request to create sample data
    response = requests.post(f"{BASE_URL}/init-sample-data")
    return print_response("INITIALIZE SAMPLE DATA", response)

def test_list_mooncakes():
    """Test listing all mooncakes
    
    This tests the basic READ operation - getting all mooncakes from the database.
    This should return a JSON array of mooncake objects.
    """
    # Make a GET request to retrieve all mooncakes
    response = requests.get(f"{BASE_URL}/mooncakes/")
    return print_response("LIST ALL MOONCAKES", response)

def test_filter_mooncakes():
    """Test filtering mooncakes by type and vegetarian status
    
    This demonstrates how to use query parameters to filter results.
    Query parameters are added to the URL after a '?' character.
    """
    print("\n🔍 Testing mooncake filtering...")
    
    # Test filtering by vegetarian status using query parameter
    # URL becomes: /mooncakes/?is_vegetarian=true
    response = requests.get(f"{BASE_URL}/mooncakes/?is_vegetarian=true")
    print_response("FILTER VEGETARIAN MOONCAKES", response)
    
    # Test filtering by mooncake type using query parameter
    # URL becomes: /mooncakes/?mooncake_type=lotus
    response = requests.get(f"{BASE_URL}/mooncakes/?mooncake_type=lotus")
    print_response("FILTER LOTUS MOONCAKES", response)

def test_create_mooncake():
    """Test creating a new mooncake
    
    This tests the CREATE operation - sending data to create a new resource.
    We send JSON data in the request body and expect to get back the created object.
    """
    # Define the data for our new mooncake
    # This dictionary will be converted to JSON automatically by requests
    new_mooncake = {
        "name": "Special Lotus",
        "price": 15.99,
        "size": "large",
        "discount": 0.1,  # 10% discount
        "type": "lotus",
        "egg_yolks": 3
    }
    
    # Make a POST request with JSON data
    # The 'json=' parameter automatically sets the Content-Type header
    response = requests.post(f"{BASE_URL}/mooncakes/", json=new_mooncake)
    result = print_response("CREATE NEW MOONCAKE", response)
    
    # If creation was successful, return the ID of the new mooncake
    # We'll use this ID in subsequent tests
    if response.status_code == 200:
        return response.json()['id']
    return None

def test_get_mooncake(mooncake_id: int):
    """Test getting a specific mooncake by ID
    
    This tests retrieving a single resource using its unique identifier.
    The ID is passed as a path parameter in the URL.
    
    Args:
        mooncake_id: The ID of the mooncake to retrieve
    """
    # Make a GET request with the ID in the URL path
    response = requests.get(f"{BASE_URL}/mooncakes/{mooncake_id}")
    return print_response(f"GET MOONCAKE {mooncake_id}", response)

def test_update_mooncake(mooncake_id: int):
    """Test updating a mooncake
    
    This tests the UPDATE operation using PUT method.
    We send the complete updated data for the resource.
    
    Args:
        mooncake_id: The ID of the mooncake to update
    """
    # Define the updated data for the mooncake
    update_data = {
        "name": "Updated Special Lotus",  # Changed name
        "price": 18.99,  # Increased price
        "size": "large",
        "discount": 0.15,  # Increased discount to 15%
        "type": "lotus",  # Required field but won't actually change
        "egg_yolks": 2  # Reduced egg yolks
    }
    
    # Make a PUT request with the updated data
    response = requests.put(f"{BASE_URL}/mooncakes/{mooncake_id}", json=update_data)
    return print_response(f"UPDATE MOONCAKE {mooncake_id}", response)

def test_cart_operations():
    """Test complete cart workflow
    
    This function tests the entire shopping cart workflow:
    1. Create a new cart
    2. Add multiple items to the cart
    3. View cart contents and totals
    4. Remove an item from the cart
    5. View the updated cart
    
    This demonstrates how different API endpoints work together.
    """
    print("\n🛒 Testing cart operations...")
    
    # Step 1: Create a new shopping cart
    response = requests.post(f"{BASE_URL}/carts/")
    cart_result = print_response("CREATE CART", response)
    
    # Check if cart creation was successful
    if response.status_code != 200:
        print("❌ Cart creation failed, stopping cart tests")
        return None
        
    # Extract the cart ID from the response - we'll need this for subsequent operations
    cart_id = response.json()['cart_id']
    
    # Step 2: Get available mooncakes so we can add some to the cart
    mooncakes_response = requests.get(f"{BASE_URL}/mooncakes/")
    if mooncakes_response.status_code == 200:
        mooncakes = mooncakes_response.json()
        
        # Make sure we have enough mooncakes to test with
        if len(mooncakes) >= 3:
            # Add first mooncake to cart with quantity 2
            # Note: quantity is passed as a query parameter (?quantity=2)
            response = requests.post(f"{BASE_URL}/carts/{cart_id}/add/{mooncakes[0]['id']}?quantity=2")
            print_response("ADD MOONCAKE 1 TO CART", response)
            
            # Add second mooncake to cart with quantity 1
            response = requests.post(f"{BASE_URL}/carts/{cart_id}/add/{mooncakes[1]['id']}?quantity=1")
            print_response("ADD MOONCAKE 2 TO CART", response)
            
            # Add third mooncake to cart with quantity 3
            response = requests.post(f"{BASE_URL}/carts/{cart_id}/add/{mooncakes[2]['id']}?quantity=3")
            print_response("ADD MOONCAKE 3 TO CART", response)
    
    # Step 3: View the complete cart contents with all details
    response = requests.get(f"{BASE_URL}/carts/{cart_id}")
    print_response("VIEW CART CONTENTS", response)
    
    # Step 4: Get just the cart total (simpler endpoint)
    response = requests.get(f"{BASE_URL}/carts/{cart_id}/total")
    print_response("GET CART TOTAL", response)
    
    # Step 5: Remove an item from the cart (testing DELETE operation)
    if 'mooncakes' in locals() and len(mooncakes) > 0:
        # Remove the first mooncake we added
        response = requests.delete(f"{BASE_URL}/carts/{cart_id}/items/{mooncakes[0]['id']}")
        print_response("REMOVE ITEM FROM CART", response)
        
        # Step 6: View cart after removal to see the updated contents
        response = requests.get(f"{BASE_URL}/carts/{cart_id}")
        print_response("CART AFTER REMOVAL", response)
    
    return cart_id  # Return cart ID in case other tests need it

def test_list_carts():
    """Test listing all carts
    
    This shows all carts in the system - useful for administration
    or debugging to see what carts have been created.
    """
    response = requests.get(f"{BASE_URL}/carts/")
    return print_response("LIST ALL CARTS", response)

def test_delete_mooncake(mooncake_id: int):
    """Test deleting a mooncake
    
    This tests the DELETE operation - permanently removing a resource.
    We test this last since we don't want to delete mooncakes that
    other tests might need.
    
    Args:
        mooncake_id: The ID of the mooncake to delete
    """
    response = requests.delete(f"{BASE_URL}/mooncakes/{mooncake_id}")
    return print_response(f"DELETE MOONCAKE {mooncake_id}", response)

def test_error_cases():
    """Test error handling
    
    It's important to test how your API handles invalid requests.
    Good APIs return appropriate HTTP status codes and helpful error messages.
    
    Common error scenarios to test:
    - 404 (Not Found): Requesting resources that don't exist
    - 400 (Bad Request): Sending invalid data
    - 422 (Validation Error): Data that fails validation rules
    """
    print("\n❌ Testing error cases...")
    
    # Test 404 error: Try to get a mooncake that doesn't exist
    # Using a very high ID that's unlikely to exist
    response = requests.get(f"{BASE_URL}/mooncakes/999999")
    print_response("GET NON-EXISTENT MOONCAKE", response)
    
    # Test 400/422 error: Try to create a mooncake with invalid data
    invalid_mooncake = {
        "name": "Invalid",
        "price": -5,  # Negative price should be invalid
        "type": "invalid_type"  # Type should only be 'veg' or 'lotus'
    }
    response = requests.post(f"{BASE_URL}/mooncakes/", json=invalid_mooncake)
    print_response("CREATE INVALID MOONCAKE", response)
    
    # Test 404 error: Try to add to a cart that doesn't exist
    response = requests.post(f"{BASE_URL}/carts/999999/add/1")
    print_response("ADD TO NON-EXISTENT CART", response)

def run_full_test_suite():
    """Run the complete test suite
    
    This function orchestrates all the individual test functions in a logical order:
    1. Basic connectivity and setup
    2. CRUD operations for mooncakes
    3. Shopping cart workflow
    4. Error handling
    5. Cleanup
    
    This demonstrates a complete API testing workflow.
    """
    print("🚀 Starting MoonCake API Test Suite")
    print("Make sure the FastAPI server is running on http://localhost:8000")
    
    try:
        # Phase 1: Basic connectivity and data setup
        test_root_endpoint()  # Check if API is running
        test_initialize_sample_data()  # Set up test data
        
        # Phase 2: Test basic mooncake operations
        test_list_mooncakes()  # Read all mooncakes
        test_filter_mooncakes()  # Test filtering capabilities
        
        # Phase 3: Test full CRUD (Create, Read, Update, Delete) cycle
        new_mooncake_id = test_create_mooncake()  # Create
        if new_mooncake_id:
            test_get_mooncake(new_mooncake_id)  # Read (specific item)
            test_update_mooncake(new_mooncake_id)  # Update
        
        # Phase 4: Test shopping cart workflow
        cart_id = test_cart_operations()  # Complete cart workflow
        test_list_carts()  # View all carts
        
        # Phase 5: Test error handling
        test_error_cases()  # How does API handle bad requests?
        
        # Phase 6: Cleanup - delete the test mooncake we created
        if new_mooncake_id:
            test_delete_mooncake(new_mooncake_id)  # Delete
        
        print(f"\n{'='*50}")
        print("✅ Test suite completed!")
        print("Check the responses above to verify everything works correctly.")
        print("Look for status codes like 200 (OK) for successful operations")
        print("and 404 (Not Found) or 400 (Bad Request) for expected errors.")
        print(f"{'='*50}")
        
    except requests.exceptions.ConnectionError:
        # This happens when the API server isn't running
        print("❌ Could not connect to the API server!")
        print("Make sure to start the FastAPI server first:")
        print("   python lesson04_fastapi.py")
        print("   OR")
        print("   uvicorn lesson04_fastapi:app --reload")

# This block runs when the script is executed directly
if __name__ == "__main__":
    # Run all the tests when this script is executed
    run_full_test_suite()
