# Personal Finance Application - Modular Version

A comprehensive personal finance management application built with
Python and ttkbootstrap GUI framework.\
This modular version breaks down the original monolithic code into
organized, maintainable modules.

> **Recommended Python Version:** 3.10+ (tested on 3.11)

## Features

-   **User Authentication**: Secure user registration and login with
    password hashing\
-   **Expense Management**: Add, view, edit, and delete expenses with
    categories\
-   **Income Tracking**: Manage income sources with categorization\
-   **Budget Overview**: Calculate budget summaries for custom date
    ranges\
-   **Analytics**: Interactive charts for understanding expense and
    income trends\
-   **CSV Import/Export**: Import financial data from CSV files\
-   **Account Management**: Change passwords and view login history\
-   **Multi-user Support**: Each user has their own isolated financial
    data

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

2.  **Install required dependencies:**

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

-   Passwords hashed with bcrypt\
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
