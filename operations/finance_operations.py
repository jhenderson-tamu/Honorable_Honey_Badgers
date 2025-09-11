
import sqlite3 as sql
import pandas as pd

class FinanceOperations:
    """Class to handle all finance-related database operations"""

    @staticmethod
    def load_expense_categories():
        """Load expense categories from database"""
        conn = sql.connect("data/finance.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM expense_category ORDER BY name ASC")
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows]

    @staticmethod
    def load_income_categories():
        """Load income categories from database"""
        conn = sql.connect("data/finance.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM income_category ORDER BY name ASC")
        rows = cursor.fetchall()
        conn.close()
        return [row[0] for row in rows]
    
    @staticmethod
    def add_expense_category(category_name):
        """Add new expense category"""
        try:
            conn = sql.connect("data/finance.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO expense_category (name) VALUES (?)", (category_name,))
            conn.commit()
            conn.close()
            return True, f"Category '{category_name}' added."
        except sql.IntegrityError:
            return False, f"Category '{category_name}' already exists."
    
    @staticmethod
    def add_income_category(category_name):
        """Add new income category"""
        try:
            conn = sql.connect("data/finance.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO income_category (name) VALUES (?)", (category_name,))
            conn.commit()
            conn.close()
            return True, f"Category '{category_name}' added."
        except sql.IntegrityError:
            return False, f"Category '{category_name}' already exists."
    
    @staticmethod
    def add_expense(date, description, category, amount, username):
        """Add new expense to database"""
        try:
            conn = sql.connect("data/finance.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO expenses (date, description, category, amount, username) 
                VALUES (?, ?, ?, ?, ?)""",
                           (date, description, category, amount, username))
            conn.commit()
            conn.close()
            return True, f"Expense added for {username}."
        except Exception as e:
            return False, f"Database error: {e}"
    
    @staticmethod
    def add_income(date, description, category, amount, username):
        """Add new income to database"""
        try:
            conn = sql.connect("data/finance.db")
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO income (date, description, category, amount, username)
                VALUES (?, ?, ?, ?, ?)
            """, (date, description, category, amount, username))
            conn.commit()
            conn.close()
            return True, f"Income added for {username}."
        except Exception as e:
            return False, f"Database error: {e}"
    
    @staticmethod
    def get_user_expenses(username):
        """Get all expenses for a user"""
        conn = sql.connect("data/finance.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, date, category, amount, description FROM expenses WHERE username=?", 
                       (username,))
        expenses = cursor.fetchall()
        conn.close()
        return expenses
    
    @staticmethod
    def get_user_income(username):
        """Get all income for a user"""
        conn = sql.connect("data/finance.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, date, category, amount, description FROM income WHERE username=?", 
                       (username,))
        income = cursor.fetchall()
        conn.close()
        return income
    
    @staticmethod
    def delete_expense(expense_id):
        """Delete an expense by ID"""
        try:
            conn = sql.connect("data/finance.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM expenses WHERE id=?", (expense_id,))
            conn.commit()
            conn.close()
            return True, "Expense removed successfully!"
        except Exception as e:
            return False, f"Error removing expense: {e}"
    
    @staticmethod
    def delete_income(income_id):
        """Delete an income by ID"""
        try:
            conn = sql.connect("data/finance.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM income WHERE id=?", (income_id,))
            conn.commit()
            conn.close()
            return True, "Income removed successfully!"
        except Exception as e:
            return False, f"Error removing income: {e}"
    
    @staticmethod
    def import_expenses_from_csv(filepath, username):
        """Import expenses from CSV file"""
        try:
            df = pd.read_csv(filepath)
            
            required_cols = {"date", "category", "amount"}
            if not required_cols.issubset(df.columns):
                return False, "CSV is missing required columns (date, category, amount)."
            
            conn = sql.connect("data/finance.db")
            cursor = conn.cursor()
            
            for _, row in df.iterrows():
                description = row.get("description", "")
                cursor.execute(
                    "INSERT INTO expenses (date, category, amount, description, username) VALUES (?, ?, ?, ?, ?)",
                    (row["date"], row["category"], float(row["amount"]), description, username)
                )
            
            conn.commit()
            conn.close()
            return True, "File imported successfully!"
        except Exception as e:
            return False, f"Error importing file: {e}"
    
    @staticmethod
    def import_income_from_csv(filepath, username):
        """Import income from CSV file"""
        try:
            df = pd.read_csv(filepath)
            
            required_cols = {"date", "category", "amount"}
            if not required_cols.issubset(df.columns):
                return False, "CSV is missing required columns (date, category, amount)."
            
            conn = sql.connect("data/finance.db")
            cursor = conn.cursor()
            
            for _, row in df.iterrows():
                description = row.get("description", "")
                cursor.execute(
                    "INSERT INTO income (date, category, amount, description, username) VALUES (?, ?, ?, ?, ?)",
                    (row["date"], row["category"], float(row["amount"]), description, username)
                )
            
            conn.commit()
            conn.close()
            return True, "File imported successfully!"
        except Exception as e:
            return False, f"Error importing file: {e}"
    
    @staticmethod
    def get_budget_summary(username, start_date, end_date):
        """Get budget summary for date range"""
        with sql.connect("data/finance.db") as conn:
            cursor = conn.cursor()
            
            # Get expenses
            cursor.execute("""
                SELECT COALESCE(SUM(amount), 0) 
                FROM expenses 
                WHERE username=? AND date BETWEEN ? AND ?
            """, (username, start_date, end_date))
            total_expenses = cursor.fetchone()[0]
            
            # Get income
            cursor.execute("""
                SELECT COALESCE(SUM(amount), 0) 
                FROM income 
                WHERE username=? AND date BETWEEN ? AND ?
            """, (username, start_date, end_date))
            total_income = cursor.fetchone()[0]
        
        leftover = total_income - total_expenses
        return total_expenses, total_income, leftover