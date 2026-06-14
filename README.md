# Overview

As a software engineer learning database management, I built an Expense Tracker — a Python command-line application that uses SQLite to store, manage, and analyze personal expenses. Users can add expenses with categories, view all entries, update or delete records, and see spending summaries with aggregate statistics.

To use the program, run `python3 expense_tracker.py` from the project directory. The database file (expenses.db) is created automatically on first run with default categories. The menu-driven interface guides you through all available operations.

My purpose for writing this software was to learn how relational databases work from the ground up — creating tables with relationships, writing SQL queries for CRUD operations, performing JOINs across tables, and using aggregate functions to summarize data. This completes my three-module portfolio covering JavaScript, Web Apps, and now SQL databases.

[Software Demo Video](http://youtube.link.goes.here)

# Relational Database

I am using SQLite, a lightweight relational database that stores everything in a single file (expenses.db). SQLite is built into Python through the sqlite3 standard library, so no external installation is required.

The database has two tables:

- **categories** — Stores expense categories (e.g., Food, Transport, Bills). Columns: `id` (INTEGER PRIMARY KEY AUTOINCREMENT), `name` (TEXT NOT NULL UNIQUE).

- **expenses** — Stores individual expense records. Columns: `id` (INTEGER PRIMARY KEY AUTOINCREMENT), `amount` (REAL NOT NULL), `description` (TEXT NOT NULL), `date` (TEXT NOT NULL), `category_id` (INTEGER NOT NULL, FOREIGN KEY referencing categories.id).

The `category_id` column in the expenses table is a foreign key that creates a one-to-many relationship: one category can have many expenses. This relationship is used in INNER JOIN queries to display category names alongside expense data.

# Development Environment

I used Visual Studio Code as my code editor and Git for version control. The application was developed and tested on macOS using the built-in terminal.

The programming language is Python 3. The only library used is sqlite3, which is part of the Python standard library and requires no external installation.

# Useful Websites

- [Python sqlite3 Documentation](https://docs.python.org/3/library/sqlite3.html)
- [SQLite Official Documentation](https://www.sqlite.org/docs.html)
- [W3Schools SQL Tutorial](https://www.w3schools.com/sql/)
- [Wikipedia - Relational Databases](https://en.wikipedia.org/wiki/Relational_database)
- [SQLite Tutorial](https://www.sqlitetutorial.net/)

# Future Work

- Add date range filtering to view expenses within a specific time period
- Export expense data to CSV for use in spreadsheet applications
- Add a monthly budget feature that warns when spending exceeds a set limit
