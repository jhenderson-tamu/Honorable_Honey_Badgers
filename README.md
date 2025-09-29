# ================================
# Honorable Honey Badgers
# Personal Finance Application
# README File
# ================================

## Overview
The **Honorable Honey Badgers Personal Finance Application** is a modular
Python-based desktop tool for managing personal finances. It allows users
to register securely, track income and expenses, and generate interactive
reports with charts and drill-down detail.

The application is built using **ttkbootstrap** for a modern Tkinter GUI,
**pandas** for data management, and **matplotlib** for analytics and charting.

> **Recommended Python Version:** 3.10+ (tested on 3.11)

## Features
- **User Authentication**
  - Secure login and registration with password hashing (`bcrypt`)
  - Multi-user support with isolated financial data

- **Expense & Income Management**
  - Add, view, edit, and delete records
  - Categorize and filter by type and date range
  - Import/export financial data via CSV

- **Analytics Dashboard**
  - **Monthly Report** – Bar chart of monthly expenses with drill-down to details
  - **Category Report** – Pie chart of spending by category
  - **Top Categories Report** – Ranked horizontal bar chart of highest spending
  - **Cash Flow Report** – Line/stacked bar chart showing Income, Expenses, and Net Savings
  - Export all charts as PNG and tabular data as CSV

- **Account Management**
  - Change passwords, manage login history, and enforce password rules

## Project Structure

``` plaintext
Honorable_Honey_Badgers/
├── __init__.py
├── main.py                     # Application entry point
├── README.md                   # Technical Documentation
├── requirements.txt            # Dependencies
│
├── data/                       # Databases
│   ├── finance.db              # Financial Data
│   └── users.db                # User Data
│
├── Docs/                       # Documentation
│   ├── ISTM 601 - Group 8 Python (Group Contract) - Phase 1.pdf
│   ├── ISTM 601 - Group 8 User Manual - Phase 2.pdf
│   └── ISTM 601 - Group 8 Technical Manual - Phase 2.pdf
│   ├── ISTM 601 - Group 8 User Manual - Phase 3.pdf
│   └── ISTM 601 - Group 8 Technical Manual - Phase 3.pdf
│
├── gui/                        # GUI page controllers
│   ├── __init__.py
│   ├── account_pages.py        # Account management (password, history)
│   ├── auth.py                 # User authentication (register/login)
│   ├── budget_pages.py         # Budget overview & savings handling
│   ├── expense_pages.py        # Expense management (CRUD, CSV import)
│   ├── income_pages.py         # Income management (CRUD, CSV import)
│   ├── category_pages.py       # Category management (update/delete)
│   └── main_app.py             # Main navigation frame
│
├── analytics/                  # Reporting & visualization
│   ├── __init__.py
│   ├── category.py             # Expenses by category (Pie chart)
│   ├── monthly.py              # Monthly expenses (Bar chart)
│   ├── top_categories.py       # Top categories with date filter
│   └── cash_flow.py            # Cash flow (Income vs Expenses line chart)
│
└── operations/                 # Business logic & DB operations
    ├── __init__.py
    ├── database.py             # Database setup & authentication
    ├── finance_operations.py   # CRUD, CSV import/export, budget summary
    └── reports.py              # Data access helpers for analytics
```

## Installation

1.  **Clone or download the project files**

   ```bash
   git clone https://github.com/jhenderson-tamu/Honorable_Honey_Badgers.git
   cd Honorable_Honey_Badgers
   ```
2. **Create and activate a virtual environment**

   ```bash
   python -m venv .venv
   source .venv/bin/activate   # On Windows use: .venv\Scripts\activate
   ```
   
3. **Install required dependencies:**

    ``` bash
    pip install -r requirements.txt
    ```

3.  **Run the application:**

    -   **From Command Line:**

        ``` bash
        python main.py
        ```

    -   **From Python IDLE:**

        1.  Open IDLE (Python GUI)\
        2.  Go to **File → Open...** and select `main.py`\
        3.  Click **Run → Run Module** (or press **F5**) to start the
            application

## Module Descriptions

### `database.py`

-   Sets up `users.db` (user authentication, login history)\
-   Sets up `finance.db` (expenses, income, categories)\
-   Handles registration, authentication, and login history tracking

### `finance_operations.py`

-   Manages categories, expenses, and income\
-   CRUD operations (create, read, update, delete)\
-   CSV import (expenses and income)\
-   Budget summaries and calculations

### `reports.py`

-   Provides database access for analytics\
-   Expense and income retrieval by category or date range\
-   Generates monthly aggregated data for charts

### `auth.py`

-   Handles user login and registration GUI\
-   Validates credentials\
-   Starts the main app after login

### `expense_pages.py`

-   Manual expense entry form\
-   Expense import from CSV\
-   View and remove expenses\
-   Category management

### `income_pages.py`

-   Manual income entry form\
-   Income import from CSV\
-   View and remove income\
-   Income category management

### `budget_pages.py`

-   Budget overview calculations\
-   Date range selection\
-   Displays totals, income, expenses, savings

### `account_pages.py`

-   Change password interface\
-   View login history\
-   Account management options

### `category_pages.py`

-   Manage categories for both expenses and income\
-   Update, rename, or delete with reassignment handling

### `main_app.py`

-   Builds main window after login\
-   Sidebar navigation for all modules\
-   Handles logout and page switching

### `analytics/`

-   **category.py**: Expenses by category pie chart\
-   **monthly.py**: Monthly expenses bar chart\
-   **top_categories.py**: Top categories ranked by amount\
-   **cash_flow.py**: Cash flow line chart (Income vs Expenses vs Net)

### `main.py`

-   Initializes databases\
-   Starts authentication\
-   Launches main app

## Usage

### First Time Setup

1.  Run the app with `python main.py`\
2.  Register a new user\
3.  Login to access the main menu

### Expenses & Income

-   Add manually or import via CSV\
-   View or delete existing records\
-   Manage categories

### Budget Overview

-   Choose a start and end date\
-   View totals, income, expenses, and net savings

### Analytics

-   Pie chart of expenses by category\
-   Bar chart of monthly expenses\
-   Bar chart of top categories\
-   Line chart for cash flow

### CSV Import Format

Both **expense** and **income** CSV files must include:\
- `date` (YYYY-MM-DD)\
- `category` (string)\
- `amount` (numeric)\
- `description` (optional)

## Database Files

-   `users.db`: Accounts and login history\
-   `finance.db`: Expenses, income, categories

## Security Features

-   User passwords are hashed using bcrypt before storage
-   No plaintext credentials are saved in the database  
-   Isolated user data\
-   Session-based authentication

## Dependencies

-   **pandas**: Data manipulation\
-   **bcrypt**: Password hashing\
-   **ttkbootstrap**: GUI framework\
-   **matplotlib**: Charts & visualizations

## Troubleshooting

1.  **Missing imports**: Install dependencies with
    `pip install -r requirements.txt`\
2.  **Database errors**: Delete `.db` files to reset\
3.  **GUI issues**: Ensure `ttkbootstrap` is installed

## Future Enhancements

-   Recurring transactions\
-   Search and filtering\
-   Data export\
-   Backup/restore
