import db
import math

conn = db.get_connection()
if conn:
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, price FROM menu_items")
    items = cursor.fetchall()
    
    for item in items:
        # If the price is still small (like < 20), assume it's in dollars and convert
        if item['price'] < 50:
            # Multiply by approx 80 and round to nearest 10 for clean INR prices
            new_price = round((float(item['price']) * 80) / 10) * 10
            # A few manual adjustments for clean numbers as in the schema
            if new_price < 50: new_price = 50
            cursor.execute("UPDATE menu_items SET price = %s WHERE id = %s", (new_price, item['id']))
            print(f"Updated item {item['id']} to {new_price} INR")
            
    conn.commit()
    cursor.close()
    conn.close()
    print("All prices have been updated to Rupees in the database!")
else:
    print("Could not connect to database.")
