import sqlite3

def create_database():
    conn = sqlite3.connect('bookings.db')
    cursor = conn.cursor()
    
    # Create a table for bookings
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date TEXT NOT NULL,
            room TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_database()