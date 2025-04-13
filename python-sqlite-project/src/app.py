import sqlite3

def initialize_db():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
    ''')
    
    connection.commit()
    connection.close()

def insert_user(name, email):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    
    cursor.execute('''
        INSERT INTO users (name, email) VALUES (?, ?)
    ''', (name, email))
    
    connection.commit()
    connection.close()

def get_users():
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    
    connection.close()
    return users

def update_user(user_id, name, email):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    
    cursor.execute('''
        UPDATE users SET name = ?, email = ? WHERE id = ?
    ''', (name, email, user_id))
    
    connection.commit()
    connection.close()

def delete_user(user_id):
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    
    cursor.execute('''
        DELETE FROM users WHERE id = ?
    ''', (user_id,))
    
    connection.commit()
    connection.close()

if __name__ == '__main__':
    initialize_db()
    
    while True:
        print("1. Add User")
        print("2. View Users")
        print("3. Update User")
        print("4. Delete User")
        print("5. Exit")
        
        choice = input("Choose an option: ")
        
        if choice == '1':
            name = input("Enter name: ")
            email = input("Enter email: ")
            insert_user(name, email)
            print("User added.")
        elif choice == '2':
            users = get_users()
            for user in users:
                print(user)
        elif choice == '3':
            user_id = int(input("Enter user ID to update: "))
            name = input("Enter new name: ")
            email = input("Enter new email: ")
            update_user(user_id, name, email)
            print("User updated.")
        elif choice == '4':
            user_id = int(input("Enter user ID to delete: "))
            delete_user(user_id)
            print("User deleted.")
        elif choice == '5':
            break
        else:
            print("Invalid option. Please try again.")