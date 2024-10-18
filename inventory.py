import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
import csv

# Load environment variables from the .env file
load_dotenv()

# Establish connection to MySQL using environment variables
def create_connection():
    connection = None
    try:
        connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE")
        )
        if connection.is_connected():
            print("Connection to MySQL DB successful")
    except Error as e:
        print(f"Error: '{e}'")
    return connection


# Add a new product with user input validation and option to cancel
def add_product(connection):
    cursor = connection.cursor()
    try:
        # Loop until a valid product name is entered or the user cancels
        while True:
            name = input("Enter product name (or type 'cancel' to exit): ").strip()
            if name.lower() == 'cancel':
                print("Product addition cancelled.")
                return  # Exit the function if the user cancels
            if not name:  # Check for empty input
                print("Product name cannot be empty. Please enter a valid name.")
            else:
                break  # Exit the loop when a valid name is entered

        # Loop until a valid quantity is entered or the user cancels
        while True:
            quantity_input = input("Enter product quantity (whole number, or type 'cancel' to exit): ").strip()
            if quantity_input.lower() == 'cancel':
                print("Product addition cancelled.")
                return  # Exit the function if the user cancels
            try:
                quantity = int(quantity_input)
                if quantity < 0:
                    print("Quantity cannot be negative. Please enter a valid quantity.")
                else:
                    break  # Exit the loop when a valid quantity is entered
            except ValueError:
                print("Invalid input. Please enter a whole number for the quantity.")

        # Loop until a valid price is entered or the user cancels
        while True:
            price_input = input("Enter product price (or type 'cancel' to exit): ").strip()
            if price_input.lower() == 'cancel':
                print("Product addition cancelled.")
                return  # Exit the function if the user cancels
            try:
                price = float(price_input)
                if price < 0:
                    print("Price cannot be negative. Please enter a valid price.")
                else:
                    break  # Exit the loop when a valid price is entered
            except ValueError:
                print("Invalid input. Please enter a valid price.")

        # Insert the new product into the database
        query = "INSERT INTO products (name, quantity, price) VALUES (%s, %s, %s)"
        values = (name, quantity, price)
        cursor.execute(query, values)
        connection.commit()
        print(f"Product '{name}' added successfully")

    except ValueError as ve:
        print(f"Input error: {ve}")
    except Error as e:
        print(f"Database error: {e}")


# View all products in the products table with formatted prices and table layout
def view_products(connection):
    cursor = connection.cursor()
    try:
        query = "SELECT * FROM products"
        cursor.execute(query)
        result = cursor.fetchall()
        if len(result) == 0:
            print("No products found in the inventory.")
        else:
            print(f"\n{'ID':<5} {'Name':<25} {'Quantity':<10} {'Price':<10}")
            print("-" * 50)
            for row in result:
                product_id, name, quantity, price = row
                formatted_price = f"£{price:.2f}"
                print(f"{product_id:<5} {name:<25} {quantity:<10} {formatted_price:<10}")

    except Error as e:
        print(f"Database error: {e}")


# Update a product's details with an option to update specific fields
def update_product(connection):
    cursor = connection.cursor()
    try:
        product_id = int(input("Enter product ID to update: "))

        # Check if the product exists before proceeding
        query = "SELECT * FROM products WHERE id = %s"
        cursor.execute(query, (product_id,))
        result = cursor.fetchone()

        if result is None:
            print(f"Product with ID {product_id} does not exist.")
            return  # Exit the function if the product doesn't exist

        # Display current product details in a table format
        current_name, current_quantity, current_price = result[1], result[2], result[3]
        print(f"\nCurrent product details:")
        print(f"{'ID':<5} {'Name':<25} {'Quantity':<10} {'Price':<10}")
        print("-" * 50)
        print(f"{product_id:<5} {current_name:<25} {current_quantity:<10} £{current_price:.2f}")
        
        # Ask the user which fields to update (leave blank to skip updating that field)
        new_name = input(f"\nEnter new product name (leave blank to keep '{current_name}'): ").strip() or current_name
        try:
            new_quantity = input(f"Enter new quantity (leave blank to keep '{current_quantity}'): ").strip()
            new_quantity = int(new_quantity) if new_quantity != "" else current_quantity
        except ValueError:
            print("Invalid input for quantity. Quantity must be a whole number.")
            return

        try:
            new_price = input(f"Enter new price (leave blank to keep '£{current_price:.2f}'): ").strip()
            new_price = float(new_price) if new_price != "" else current_price
        except ValueError:
            print("Invalid input for price. Price must be a valid number.")
            return

        if new_quantity < 0 or new_price < 0:
            raise ValueError("Quantity and price must be non-negative.")

        # Update the product with new details
        query = """
        UPDATE products 
        SET name = %s, quantity = %s, price = %s 
        WHERE id = %s
        """
        values = (new_name, new_quantity, new_price, product_id)
        cursor.execute(query, values)
        connection.commit()

        print(f"\nProduct with ID {product_id} updated successfully")

    except ValueError as ve:
        print(f"Input error: {ve}")
    except Error as e:
        print(f"Database error: {e}")


# Delete a product with defensive error handling, validation, and option to cancel
def delete_product(connection):
    cursor = connection.cursor()
    try:
        # Loop until a valid product ID is entered or the user cancels
        while True:
            product_id_input = input("Enter product ID to delete (or type 'cancel' to exit): ").strip()
            if product_id_input.lower() == 'cancel':
                print("Product deletion cancelled.")
                return  # Exit the function if the user cancels
            try:
                product_id = int(product_id_input)
                break  # Exit the loop when a valid product ID is entered
            except ValueError:
                print("Invalid input. Please enter a valid product ID.")

        # Check if the product exists before attempting to delete
        query = "DELETE FROM products WHERE id = %s"
        cursor.execute(query, (product_id,))
        connection.commit()

        if cursor.rowcount == 0:
            print(f"Product with ID {product_id} not found.")
        else:
            print(f"Product with ID {product_id} deleted successfully")

    except Error as e:
        print(f"Database error: {e}")


# Search for a product by name with formatted output and input validation
def search_product(connection):
    cursor = connection.cursor()
    try:
        # Loop until a valid name is entered or the user cancels
        while True:
            name = input("Enter product name to search (or type 'cancel' to exit): ").strip()
            if name.lower() == 'cancel':
                print("Search cancelled.")
                return  # Exit the function if the user cancels
            if not name:  # Check for empty input
                print("Product name cannot be empty. Please enter a valid name.")
            else:
                break  # Exit the loop when a valid name is entered

        query = "SELECT * FROM products WHERE name LIKE %s"
        cursor.execute(query, ('%' + name + '%',))
        result = cursor.fetchall()
        
        if len(result) == 0:
            print(f"No products found with name '{name}'.")
        else:
            print(f"\nProducts matching '{name}':\n")
            print(f"{'ID':<5} {'Name':<25} {'Quantity':<10} {'Price':<10}")
            print("-" * 50)
            for row in result:
                product_id, name, quantity, price = row
                formatted_price = f"£{price:.2f}"
                # Optionally truncate long product names for better layout
                name_display = (name[:22] + '...') if len(name) > 25 else name
                print(f"{product_id:<5} {name_display:<25} {quantity:<10} {formatted_price:<10}")

    except Error as e:
        print(f"Database error: {e}")


# Export products to a CSV file with formatted prices
def export_to_csv(connection):
    cursor = connection.cursor()
    try:
        query = "SELECT * FROM products"
        cursor.execute(query)
        result = cursor.fetchall()
        with open("inventory.csv", mode='w', newline='') as file:
            writer = csv.writer(file)
            # Optional: Improved column names
            writer.writerow(["Product ID", "Name", "Quantity", "Price (GBP)"])
            for row in result:
                product_id, name, quantity, price = row
                # Format price with £ symbol
                formatted_price = f"£{price:.2f}"
                writer.writerow([product_id, name, quantity, formatted_price])
        print("Inventory exported to 'inventory.csv' successfully.")

    except Error as e:
        print(f"Database error: {e}")


# Restock products (increase quantity) with validation and option to cancel
def restock_product(connection):
    cursor = connection.cursor()
    try:
        # Loop until a valid product ID is entered or the user cancels
        while True:
            product_id_input = input("Enter product ID to restock (or type 'cancel' to exit): ").strip()
            if product_id_input.lower() == 'cancel':
                print("Restocking cancelled.")
                return  # Exit the function if the user cancels
            try:
                product_id = int(product_id_input)
                break  # Exit the loop when a valid product ID is entered
            except ValueError:
                print("Invalid input. Please enter a valid product ID.")

        # Loop until a valid restock quantity is entered or the user cancels
        while True:
            restock_quantity_input = input("Enter quantity to add (or type 'cancel' to exit): ").strip()
            if restock_quantity_input.lower() == 'cancel':
                print("Restocking cancelled.")
                return  # Exit the function if the user cancels
            try:
                restock_quantity = int(restock_quantity_input)
                if restock_quantity < 0:
                    print("Quantity must be non-negative. Please enter a valid quantity.")
                else:
                    break  # Exit the loop when a valid quantity is entered
            except ValueError:
                print("Invalid input. Please enter a valid quantity.")

        # Update the quantity in the database
        query = "UPDATE products SET quantity = quantity + %s WHERE id = %s"
        cursor.execute(query, (restock_quantity, product_id))
        connection.commit()

        if cursor.rowcount == 0:
            print(f"Product with ID {product_id} does not exist.")
        else:
            print(f"Product with ID {product_id} restocked by {restock_quantity} successfully")

    except Error as e:
        print(f"Database error: {e}")


# View products running low on stock with input validation and option to cancel
def view_low_stock(connection):
    cursor = connection.cursor()
    try:
        # Loop until a valid low-stock threshold is entered or the user cancels
        while True:
            low_stock_threshold_input = input("Enter the threshold for low stock (or type 'cancel' to exit): ").strip()
            if low_stock_threshold_input.lower() == 'cancel':
                print("Low-stock viewing cancelled.")
                return  # Exit the function if the user cancels
            try:
                low_stock_threshold = int(low_stock_threshold_input)
                if low_stock_threshold < 0:
                    print("Threshold must be a non-negative number. Please enter a valid number.")
                else:
                    break  # Exit the loop when a valid threshold is entered
            except ValueError:
                print("Invalid input. Please enter a valid number.")

        query = "SELECT * FROM products WHERE quantity < %s"
        cursor.execute(query, (low_stock_threshold,))
        result = cursor.fetchall()

        if len(result) == 0:
            print(f"No products found with stock less than {low_stock_threshold}.")
        else:
            print(f"\nProducts with stock less than {low_stock_threshold}:\n")
            print(f"{'ID':<5} {'Name':<25} {'Quantity':<10} {'Price':<10}")
            print("-" * 50)
            for row in result:
                product_id, name, quantity, price = row
                formatted_price = f"£{price:.2f}"
                print(f"{product_id:<5} {name:<25} {quantity:<10} {formatted_price:<10}")

    except Error as e:
        print(f"Database error: {e}")


# Display CLI menu
def display_menu():
    print("\n--- Inventory Management ---")
    print("1. Add a product")
    print("2. View all products")
    print("3. Update a product")
    print("4. Delete a product")
    print("5. Search for a product by name")
    print("6. Export inventory to CSV")
    print("7. Restock a product")
    print("8. View low-stock products")
    print("9. Exit")


# Main function to run the CLI
if __name__ == "__main__":
    conn = create_connection()
    if conn is not None:
        while True:
            display_menu()
            try:
                choice = int(input("\nChoose an option (1-9): "))

                if choice == 1:
                    add_product(conn)
                elif choice == 2:
                    view_products(conn)
                elif choice == 3:
                    update_product(conn)
                elif choice == 4:
                    delete_product(conn)
                elif choice == 5:
                    search_product(conn)
                elif choice == 6:
                    export_to_csv(conn)
                elif choice == 7:
                    restock_product(conn)
                elif choice == 8:
                    view_low_stock(conn)
                elif choice == 9:
                    print("Exiting the program. Goodbye!")
                    break
                else:
                    print("Invalid option. Please choose between 1 and 9.")
            except ValueError:
                print("Invalid input. Please enter a number.")

