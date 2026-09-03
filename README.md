# Inventory Management System

A web-based Inventory Management System built using Python Flask, SQLite, HTML, and CSS.

## Project Overview

This project helps manage products, stock, suppliers, and inventory transactions through a simple web interface.

Users can log in securely and manage inventory from a centralized dashboard.

## Features

- User Login and Logout
- Password Hashing
- Dashboard
- Product Management
- Add Products
- Edit Products
- Delete Products
- Inventory Management
- Stock In
- Stock Out
- Stock Validation
- Stock Transaction History
- Supplier Management
- Low Stock Alerts
- Inventory Search
- Reports
- Responsive User Interface

## Technologies Used

- Python
- Flask
- Flask-SQLAlchemy
- SQLite
- HTML5
- CSS3
- Jinja2
- Werkzeug

## Project Structure

```text
InventoryManagementSystem
│
├── app.py
├── models.py
├── create_user.py
├── requirements.txt
├── README.md
│
├── instance
│   └── inventory.db
│
├── static
│   └── style.css
│
└── templates
    ├── home.html
    ├── login.html
    ├── dashboard.html
    ├── inventory.html
    ├── add_product.html
    ├── edit_product.html
    ├── stock.html
    ├── suppliers.html
    ├── stock_history.html
    └── reports.html