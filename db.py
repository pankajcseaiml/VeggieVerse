import os
import sys
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables from .env file (if present)
load_dotenv()

# ── Connection configuration ───────────────────────────────────────────────────
# All credentials MUST be supplied via environment variables.
# Copy .env.example → .env and fill in your values.
# Never hard-code credentials here.

_REQUIRED_ENV_VARS = {
    "MYSQL_HOST":     "MySQL host (e.g. localhost)",
    "MYSQL_USER":     "MySQL username (e.g. root)",
    "MYSQL_PASSWORD": "MySQL password",
    "MYSQL_DATABASE": "MySQL database name (e.g. veg_restaurant_db)",
}


def _validate_env():
    """Raise a clear error if any required DB environment variable is missing."""
    missing = [var for var in _REQUIRED_ENV_VARS if not os.environ.get(var)]
    if missing:
        print("\n[ERROR] Missing required environment variables for database connection:")
        for var in missing:
            print(f"  {var}  — {_REQUIRED_ENV_VARS[var]}")
        print("\nCopy .env.example to .env and fill in the values.")
        print("See docs/DISASTER_RECOVERY.md for full setup instructions.\n")
        sys.exit(1)


# Validate on module import so the application fails fast and clearly.
_validate_env()


def get_connection():
    """Return a live MySQL connection or None on error."""
    try:
        connection = mysql.connector.connect(
            host=os.environ["MYSQL_HOST"],
            user=os.environ["MYSQL_USER"],
            password=os.environ["MYSQL_PASSWORD"],
            database=os.environ["MYSQL_DATABASE"],
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"[ERROR] MySQL connection failed: {e}")
    return None

def get_full_menu():
    conn = get_connection()
    if not conn: return "Database connection failed."
    
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM menu_items WHERE is_available = TRUE ORDER BY category, name")
        items = cursor.fetchall()
        
        if not items:
            return "Our menu is currently empty."
            
        menu_str = "Here is our menu:\n\n"
        current_category = ""
        for item in items:
            cat = item['category'].capitalize() if item['category'] else 'Other'
            if cat != current_category:
                menu_str += f"**{cat}**\n"
                current_category = cat
            menu_str += f"- {item['name']}: ₹{item['price']:.2f}\n"
        
        return menu_str
    except Error as e:
        return f"Error retrieving menu: {e}"
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def get_item_info(item_name):
    conn = get_connection()
    if not conn: return "Database connection failed."
    
    try:
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM menu_items WHERE name LIKE %s LIMIT 1"
        cursor.execute(query, (f"%{item_name}%",))
        item = cursor.fetchone()
        
        if item:
            return f"**{item['name']}** (₹{item['price']:.2f})\n{item['description']}"
        else:
            return f"I couldn't find '{item_name}' on our menu."
    except Error as e:
        return f"Error retrieving item info: {e}"
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def save_order(customer_name, phone, items_list, order_type='Takeaway'):
    conn = get_connection()
    if not conn: return None, "Database connection failed."
    
    try:
        cursor = conn.cursor()
        
        total_amount = 0
        order_details = []
        for item_name, quantity in items_list:
            cursor.execute("SELECT id, price FROM menu_items WHERE name LIKE %s AND is_available = TRUE LIMIT 1", (f"%{item_name}%",))
            res = cursor.fetchone()
            if res:
                item_id, price = res
                total_amount += float(price) * quantity
                order_details.append((item_id, quantity, float(price)))
            else:
                return None, f"Item '{item_name}' not available."

        query_order = """INSERT INTO orders (customer_name, customer_phone, total_amount, order_type)
                         VALUES (%s, %s, %s, %s)"""
        cursor.execute(query_order, (customer_name, phone, total_amount, order_type))
        order_id = cursor.lastrowid
        
        query_item = "INSERT INTO order_items (order_id, menu_item_id, quantity, unit_price) VALUES (%s, %s, %s, %s)"
        for detail in order_details:
            cursor.execute(query_item, (order_id, detail[0], detail[1], detail[2]))
            
        conn.commit()
        return order_id, f"Order #{order_id} placed successfully! Total: ₹{total_amount:.2f}"
    except Error as e:
        if conn: conn.rollback()
        return None, f"Error saving order: {e}"
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def save_reservation(name, phone, datetime_str, num_guests, notes=""):
    conn = get_connection()
    if not conn: return None, "Database connection failed."
    
    try:
        cursor = conn.cursor()
        query = """INSERT INTO reservations (customer_name, customer_phone, reservation_time, num_guests, special_requests)
                   VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(query, (name, phone, datetime_str, num_guests, notes))
        res_id = cursor.lastrowid
        conn.commit()
        return res_id, f"Reservation #{res_id} confirmed for {num_guests} guests on {datetime_str}."
    except Error as e:
        if conn: conn.rollback()
        return None, f"Error saving reservation: {e}"
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

def log_chat(session_id, user_msg, bot_response, intent_tag):
    conn = get_connection()
    if not conn: return
    
    try:
        cursor = conn.cursor()
        query = "INSERT INTO chat_logs (session_id, user_message, bot_response, intent_tag) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (session_id, user_msg, bot_response, intent_tag))
        conn.commit()
    except Error as e:
        print(f"Error logging chat: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
