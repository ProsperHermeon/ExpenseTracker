"""
Expense Tracker Application

A Python command-line application that uses SQLite to manage personal
expenses. Users can add, view, update, and delete expenses organized
by category, and view spending summaries with aggregate functions.

This program demonstrates:
- Creating a SQLite database with multiple tables
- CRUD operations (INSERT, SELECT, UPDATE, DELETE)
- Building SQL commands in Python and processing results
- JOIN between two related tables
- Aggregate functions (SUM, COUNT)
- Parameterized queries for security
"""

import sqlite3
from datetime import datetime


# ============================================================
# DATABASE SETUP
# ============================================================

def connect_db():
    """
    Creates a connection to the SQLite database file.
    Returns the connection object.
    """
    conn = sqlite3.connect('expenses.db')
    conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key support
    return conn


def create_tables(conn):
    """
    Creates the categories and expenses tables if they don't exist.
    The expenses table has a foreign key referencing the categories table.

    Tables:
    - categories: id (PRIMARY KEY), name (UNIQUE)
    - expenses: id (PRIMARY KEY), amount, description, date, category_id (FOREIGN KEY)
    """
    cursor = conn.cursor()

    # Create categories table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    # Create expenses table with foreign key to categories
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            description TEXT NOT NULL,
            date TEXT NOT NULL,
            category_id INTEGER NOT NULL,
            FOREIGN KEY (category_id) REFERENCES categories(id)
        )
    ''')

    conn.commit()


def seed_default_categories(conn):
    """
    Inserts default categories if the categories table is empty.
    This gives users a starting point without needing to create
    categories manually before adding their first expense.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM categories")
    count = cursor.fetchone()[0]

    if count == 0:
        defaults = ['Food', 'Transport', 'Entertainment', 'Bills', 'Shopping', 'Health', 'Other']
        for cat in defaults:
            cursor.execute("INSERT INTO categories (name) VALUES (?)", (cat,))
        conn.commit()
        print("  Default categories created: " + ", ".join(defaults))


# ============================================================
# CATEGORY OPERATIONS
# ============================================================

def add_category(conn):
    """
    Prompts the user for a category name and inserts it into
    the categories table. Uses parameterized query to prevent
    SQL injection.
    """
    name = input("  Enter new category name: ").strip()
    if not name:
        print("  Error: Category name cannot be empty.\n")
        return

    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
        conn.commit()
        print(f"  Category '{name}' added successfully!\n")
    except sqlite3.IntegrityError:
        print(f"  Error: Category '{name}' already exists.\n")


def display_categories(conn):
    """
    Retrieves and displays all categories from the database.
    Returns the list of categories for use by other functions.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM categories ORDER BY name")
    categories = cursor.fetchall()

    print("\n  Available Categories:")
    print("  " + "-" * 30)
    for cat in categories:
        print(f"    {cat[0]}. {cat[1]}")
    print()

    return categories


# ============================================================
# EXPENSE CRUD OPERATIONS
# ============================================================

def add_expense(conn):
    """
    Prompts the user for expense details (amount, description,
    category) and inserts a new record into the expenses table.
    Automatically records today's date.

    Demonstrates: INSERT with parameterized query
    """
    display_categories(conn)

    try:
        category_id = int(input("  Enter category ID: "))
        amount = float(input("  Enter amount ($): "))
        description = input("  Enter description: ").strip()

        if amount <= 0:
            print("  Error: Amount must be greater than zero.\n")
            return
        if not description:
            print("  Error: Description cannot be empty.\n")
            return

        date = datetime.now().strftime("%Y-%m-%d")

        cursor = conn.cursor()
        # INSERT: Build and execute the SQL command with parameters
        cursor.execute(
            "INSERT INTO expenses (amount, description, date, category_id) VALUES (?, ?, ?, ?)",
            (amount, description, date, category_id)
        )
        conn.commit()
        print(f"  Expense of ${amount:.2f} added successfully!\n")

    except ValueError:
        print("  Error: Invalid input. Please enter valid numbers.\n")
    except sqlite3.IntegrityError:
        print("  Error: Invalid category ID.\n")


def view_expenses(conn):
    """
    Retrieves all expenses joined with their category names
    and displays them in a formatted table.

    Demonstrates: SELECT with INNER JOIN between expenses and categories
    """
    cursor = conn.cursor()

    # JOIN: Combine expenses with categories to show category name
    cursor.execute('''
        SELECT e.id, e.amount, e.description, e.date, c.name
        FROM expenses e
        INNER JOIN categories c ON e.category_id = c.id
        ORDER BY e.date DESC
    ''')

    expenses = cursor.fetchall()

    if not expenses:
        print("\n  No expenses recorded yet.\n")
        return

    # Display results in a formatted table
    print("\n  " + "=" * 70)
    print(f"  {'ID':<5} {'Amount':<12} {'Category':<15} {'Date':<12} {'Description'}")
    print("  " + "=" * 70)

    for exp in expenses:
        print(f"  {exp[0]:<5} ${exp[1]:<11.2f} {exp[4]:<15} {exp[3]:<12} {exp[2]}")

    print("  " + "=" * 70)
    print(f"  Total: {len(expenses)} expense(s)\n")


def update_expense(conn):
    """
    Allows the user to update the amount and description of
    an existing expense identified by its ID.

    Demonstrates: UPDATE with parameterized query
    """
    view_expenses(conn)

    try:
        expense_id = int(input("  Enter expense ID to update: "))

        # Check if expense exists
        cursor = conn.cursor()
        cursor.execute("SELECT id, amount, description FROM expenses WHERE id = ?", (expense_id,))
        expense = cursor.fetchone()

        if not expense:
            print("  Error: Expense not found.\n")
            return

        print(f"  Current: ${expense[1]:.2f} - {expense[2]}")
        new_amount = input("  Enter new amount (or press Enter to keep current): ").strip()
        new_description = input("  Enter new description (or press Enter to keep current): ").strip()

        # Use current values if user presses Enter
        amount = float(new_amount) if new_amount else expense[1]
        description = new_description if new_description else expense[2]

        # UPDATE: Modify the existing record
        cursor.execute(
            "UPDATE expenses SET amount = ?, description = ? WHERE id = ?",
            (amount, description, expense_id)
        )
        conn.commit()
        print("  Expense updated successfully!\n")

    except ValueError:
        print("  Error: Invalid input.\n")


def delete_expense(conn):
    """
    Deletes an expense from the database by its ID.
    Asks for confirmation before deleting.

    Demonstrates: DELETE with parameterized query
    """
    view_expenses(conn)

    try:
        expense_id = int(input("  Enter expense ID to delete: "))

        # Check if expense exists
        cursor = conn.cursor()
        cursor.execute("SELECT id, amount, description FROM expenses WHERE id = ?", (expense_id,))
        expense = cursor.fetchone()

        if not expense:
            print("  Error: Expense not found.\n")
            return

        confirm = input(f"  Delete ${expense[1]:.2f} - {expense[2]}? (y/n): ").strip().lower()
        if confirm == 'y':
            # DELETE: Remove the record from the database
            cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
            conn.commit()
            print("  Expense deleted successfully!\n")
        else:
            print("  Deletion cancelled.\n")

    except ValueError:
        print("  Error: Invalid input.\n")


# ============================================================
# AGGREGATE FUNCTIONS AND FILTERING
# ============================================================

def spending_summary(conn):
    """
    Displays a spending summary grouped by category using
    aggregate functions SUM() and COUNT().

    Demonstrates: SUM() and COUNT() aggregate functions with GROUP BY
    """
    cursor = conn.cursor()

    # AGGREGATE: Use SUM and COUNT with GROUP BY and JOIN
    cursor.execute('''
        SELECT c.name,
               SUM(e.amount) as total_spent,
               COUNT(e.id) as num_expenses
        FROM expenses e
        INNER JOIN categories c ON e.category_id = c.id
        GROUP BY c.name
        ORDER BY total_spent DESC
    ''')

    results = cursor.fetchall()

    if not results:
        print("\n  No expenses recorded yet.\n")
        return

    # Calculate grand total using another aggregate query
    cursor.execute("SELECT SUM(amount) FROM expenses")
    grand_total = cursor.fetchone()[0] or 0

    print("\n  " + "=" * 50)
    print("  Spending Summary by Category")
    print("  " + "=" * 50)
    print(f"  {'Category':<20} {'Total':<15} {'Count'}")
    print("  " + "-" * 50)

    for row in results:
        print(f"  {row[0]:<20} ${row[1]:<14.2f} {row[2]} expense(s)")

    print("  " + "-" * 50)
    print(f"  {'GRAND TOTAL':<20} ${grand_total:<14.2f}")
    print("  " + "=" * 50 + "\n")


def filter_by_category(conn):
    """
    Filters and displays expenses for a specific category.
    Uses JOIN to combine expense data with category names.

    Demonstrates: SELECT with WHERE clause and JOIN
    """
    display_categories(conn)

    try:
        category_id = int(input("  Enter category ID to filter by: "))

        cursor = conn.cursor()
        # Filtered query with JOIN
        cursor.execute('''
            SELECT e.id, e.amount, e.description, e.date, c.name
            FROM expenses e
            INNER JOIN categories c ON e.category_id = c.id
            WHERE e.category_id = ?
            ORDER BY e.date DESC
        ''', (category_id,))

        expenses = cursor.fetchall()

        if not expenses:
            print("\n  No expenses found for this category.\n")
            return

        category_name = expenses[0][4]
        print(f"\n  Expenses in '{category_name}':")
        print("  " + "-" * 60)

        for exp in expenses:
            print(f"  ID: {exp[0]} | ${exp[1]:.2f} | {exp[3]} | {exp[2]}")

        print("  " + "-" * 60)
        print(f"  Total: {len(expenses)} expense(s)\n")

    except ValueError:
        print("  Error: Invalid input.\n")


# ============================================================
# MAIN APPLICATION MENU
# ============================================================

def display_menu():
    """
    Displays the main menu options for the application.
    """
    print("  ╔══════════════════════════════════════╗")
    print("  ║     💰 Expense Tracker Menu          ║")
    print("  ╠══════════════════════════════════════╣")
    print("  ║  1. Add a new category               ║")
    print("  ║  2. Add a new expense                ║")
    print("  ║  3. View all expenses                ║")
    print("  ║  4. Update an expense                ║")
    print("  ║  5. Delete an expense                ║")
    print("  ║  6. View spending summary            ║")
    print("  ║  7. Filter expenses by category      ║")
    print("  ║  8. Exit                             ║")
    print("  ╚══════════════════════════════════════╝")


def main():
    """
    Main function that initializes the database and runs
    the application loop with menu-driven interaction.
    """
    # Initialize database connection and create tables
    conn = connect_db()
    create_tables(conn)
    seed_default_categories(conn)

    print("\n  Welcome to Expense Tracker!")
    print("  Track your spending with SQLite.\n")

    while True:
        display_menu()
        choice = input("\n  Enter your choice (1-8): ").strip()
        print()

        if choice == '1':
            add_category(conn)
        elif choice == '2':
            add_expense(conn)
        elif choice == '3':
            view_expenses(conn)
        elif choice == '4':
            update_expense(conn)
        elif choice == '5':
            delete_expense(conn)
        elif choice == '6':
            spending_summary(conn)
        elif choice == '7':
            filter_by_category(conn)
        elif choice == '8':
            print("  Goodbye! Your expenses have been saved.\n")
            conn.close()
            break
        else:
            print("  Invalid choice. Please enter a number between 1 and 8.\n")


if __name__ == "__main__":
    main()
