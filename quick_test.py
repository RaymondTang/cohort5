#!/usr/bin/env python3
"""
Quick test runner for the MoonCake API

This script demonstrates a simple workflow with the API in a beginner-friendly way.
Unlike test_api.py which does comprehensive testing, this script shows a typical
user workflow: creating data, browsing products, building a cart, and checking totals.

Perfect for:
- First-time users who want to see the API in action
- Demonstrations and learning
- Quick verification that the API is working

To use:
1. Start the FastAPI server: python lesson04_fastapi.py
2. Run this demo: python quick_test.py
"""

# Import libraries we need
import requests  # For making HTTP requests to our API
import json  # For handling JSON data (not used much here, but good to have)
import time  # For potential delays (not used in this simple version)

# The base URL where our API is running
BASE_URL = "http://localhost:8000"

def quick_demo():
    """Run a quick demonstration of the API functionality
    
    This function demonstrates a realistic user journey through the API:
    1. Check that everything is working
    2. Set up some sample data
    3. Browse available products
    4. Create a shopping cart and add items
    5. Check the final totals
    6. Create a custom product
    """
    
    print("🌙 MoonCake API Quick Demo")
    print("=" * 40)
    
    try:
        # Step 1: Verify the API is running and accessible
        print("1. Checking API status...")
        response = requests.get(f"{BASE_URL}/")
        if response.status_code != 200:
            raise Exception("API not responding")
        print("   ✅ API is running!")
        
        # Step 2: Set up sample data for our demo
        print("\n2. Initializing sample data...")
        response = requests.post(f"{BASE_URL}/init-sample-data")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Created {data['lotus_cakes']} lotus cakes and {data['veg_cakes']} veg cakes")
            print(f"   📦 Sample cart created: {data['sample_cart_id']}")
        
        # Step 3: Browse the available products (like a customer would)
        print("\n3. Available mooncakes:")
        response = requests.get(f"{BASE_URL}/mooncakes/")
        mooncakes = response.json()
        # Show just the first few mooncakes to keep output manageable
        for cake in mooncakes[:3]:  # Show first 3
            print(f"   🥮 {cake['name']} - ${cake['price']:.2f} ({cake['type']}, discount: {cake['discount']*100:.0f}%)")
        print(f"   ... and {len(mooncakes)-3} more!")
        
        # Step 4: Simulate a customer creating a cart and adding items
        print("\n4. Creating new cart and adding items...")
        cart_response = requests.post(f"{BASE_URL}/carts/")
        cart_id = cart_response.json()['cart_id']
        print(f"   📝 Created cart {cart_id}")
        
        # Add some items to cart (simulating customer choices)
        if len(mooncakes) >= 2:
            # Add 2 of the first mooncake
            requests.post(f"{BASE_URL}/carts/{cart_id}/add/{mooncakes[0]['id']}?quantity=2")
            # Add 1 of the second mooncake
            requests.post(f"{BASE_URL}/carts/{cart_id}/add/{mooncakes[1]['id']}?quantity=1")
            print(f"   ➕ Added 2x {mooncakes[0]['name']} and 1x {mooncakes[1]['name']}")
        
        # Step 5: Display the cart summary with pricing (like a checkout page)
        print("\n5. Cart summary:")
        response = requests.get(f"{BASE_URL}/carts/{cart_id}")
        cart_data = response.json()
        print(f"   🛒 Cart {cart_id} contains {cart_data['total_items']} items")
        print(f"   💰 Total price: ${cart_data['total_price']:.2f}")
        
        # Show detailed breakdown of each item in the cart
        for item in cart_data['items']:
            cake = item['mooncake']
            print(f"     - {item['quantity']}x {cake['name']} @ ${cake['price']:.2f} each (${item['item_total']:.2f})")
        
        # Step 6: Demonstrate creating a new product (premium mooncake)
        print("\n6. Creating custom mooncake...")
        custom_cake = {
            "name": "Royal Golden Lotus",
            "price": 25.99,  # Premium pricing
            "size": "large",
            "discount": 0.0,  # No discount for new premium product
            "type": "lotus",
            "egg_yolks": 4  # Extra luxurious with 4 egg yolks
        }
        response = requests.post(f"{BASE_URL}/mooncakes/", json=custom_cake)
        if response.status_code == 200:
            new_cake = response.json()
            print(f"   🆕 Created: {new_cake['name']} (ID: {new_cake['id']})")
        
        print("\n" + "=" * 40)
        print("✅ Quick demo completed successfully!")
        print("🌐 Visit http://localhost:8000/docs for interactive API documentation")
        print("🧪 Run 'python test_api.py' for comprehensive testing")
        
    except requests.exceptions.ConnectionError:
        # This happens when the API server isn't running
        print("❌ Cannot connect to API server!")
        print("Please start the server first:")
        print("   python lesson04_fastapi.py")
        print("   OR")
        print("   uvicorn lesson04_fastapi:app --reload")
    except Exception as e:
        # Catch any other unexpected errors
        print(f"❌ Error: {e}")

# This block runs when the script is executed directly (not imported)
if __name__ == "__main__":
    quick_demo()
