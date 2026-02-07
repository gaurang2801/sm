"""
Database operations for the Buying & Selling Dashboard Application.
"""

import sqlite3
import pandas as pd
from datetime import datetime
from contextlib import contextmanager
from typing import Optional
import streamlit as st

from config import CONFIG
from logger_setup import logger


@contextmanager
def get_db_connection():
    """
    Context manager for database connections with proper error handling.
    
    Yields:
        sqlite3.Connection: Database connection object
        
    Raises:
        sqlite3.Error: If database connection fails
    """
    conn = None
    try:
        conn = sqlite3.connect(CONFIG.DB_PATH, timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        yield conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        raise
    finally:
        if conn:
            conn.close()


def init_database() -> bool:
    """
    Initialize SQLite database with required tables and indexes.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            
            # Create transactions table
            c.execute('''CREATE TABLE IF NOT EXISTS transactions
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          transaction_type TEXT NOT NULL CHECK(transaction_type IN ('BUY', 'SELL')),
                          buyer_name TEXT,
                          seller_name TEXT,
                          item_name TEXT NOT NULL,
                          quantity_kg REAL NOT NULL CHECK(quantity_kg > 0),
                          price_per_unit REAL NOT NULL CHECK(price_per_unit > 0),
                          base_amount REAL NOT NULL CHECK(base_amount >= 0),
                          mandi_charge REAL DEFAULT 0 CHECK(mandi_charge >= 0),
                          tractor_rent REAL DEFAULT 0 CHECK(tractor_rent >= 0),
                          muddat REAL DEFAULT 0 CHECK(muddat >= 0),
                          cash_discount REAL DEFAULT 0 CHECK(cash_discount >= 0),
                          labour_charge REAL DEFAULT 0 CHECK(labour_charge >= 0),
                          transport_charge REAL DEFAULT 0 CHECK(transport_charge >= 0),
                          total_amount REAL NOT NULL CHECK(total_amount >= 0),
                          amount_paid REAL DEFAULT 0 CHECK(amount_paid >= 0),
                          transaction_date TEXT NOT NULL,
                          notes TEXT,
                          status TEXT NOT NULL DEFAULT 'PENDING' CHECK(status IN ('PENDING', 'SOLD', 'COMPLETED')),
                          created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                          updated_at TEXT DEFAULT CURRENT_TIMESTAMP)''')
            
            # Create indexes for better query performance
            c.execute('''CREATE INDEX IF NOT EXISTS idx_transaction_type 
                         ON transactions(transaction_type)''')
            c.execute('''CREATE INDEX IF NOT EXISTS idx_status 
                         ON transactions(status)''')
            c.execute('''CREATE INDEX IF NOT EXISTS idx_buyer_name 
                         ON transactions(buyer_name)''')
            c.execute('''CREATE INDEX IF NOT EXISTS idx_seller_name 
                         ON transactions(seller_name)''')
            c.execute('''CREATE INDEX IF NOT EXISTS idx_item_name 
                         ON transactions(item_name)''')
            c.execute('''CREATE INDEX IF NOT EXISTS idx_transaction_date 
                         ON transactions(transaction_date)''')
            
            # Add missing columns for backward compatibility
            columns_to_add = [
                ('buyer_name', 'TEXT'),
                ('seller_name', 'TEXT'),
                ('amount_paid', 'REAL DEFAULT 0'),
                ('created_at', 'TEXT DEFAULT CURRENT_TIMESTAMP'),
                ('updated_at', 'TEXT DEFAULT CURRENT_TIMESTAMP')
            ]
            
            for col_name, col_def in columns_to_add:
                try:
                    c.execute(f'ALTER TABLE transactions ADD COLUMN {col_name} {col_def}')
                    logger.info(f"Added column {col_name} to transactions table")
                except sqlite3.OperationalError:
                    pass  # Column already exists
            
            conn.commit()
            logger.info("Database initialized successfully")
            return True
            
    except sqlite3.Error as e:
        logger.error(f"Database initialization failed: {e}")
        st.error(f"Database initialization failed: {e}")
        return False


def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize DataFrame types and fill missing values safely."""
    if df.empty:
        return df
    normalized = df.copy()
    numeric_cols = normalized.select_dtypes(include=["number"]).columns
    object_cols = normalized.select_dtypes(include=["object"]).columns
    if len(numeric_cols) > 0:
        normalized[numeric_cols] = normalized[numeric_cols].fillna(0)
    if len(object_cols) > 0:
        normalized[object_cols] = normalized[object_cols].fillna("")
    return normalized


def get_all_transactions() -> pd.DataFrame:
    """
    Retrieve all transactions from the database.
    
    Returns:
        DataFrame containing all transactions, or empty DataFrame if error
    """
    try:
        with get_db_connection() as conn:
            df = pd.read_sql_query(
                "SELECT * FROM transactions ORDER BY id DESC", 
                conn
            )
            return normalize_dataframe(df)
    except Exception as e:
        logger.error(f"Error retrieving all transactions: {e}")
        return pd.DataFrame()


def get_pending_transactions() -> pd.DataFrame:
    """
    Retrieve pending (bought but not sold) transactions.
    
    Returns:
        DataFrame containing pending transactions, or empty DataFrame if error
    """
    try:
        with get_db_connection() as conn:
            df = pd.read_sql_query(
                "SELECT * FROM transactions WHERE status = 'PENDING' ORDER BY id DESC", 
                conn
            )
            return normalize_dataframe(df)
    except Exception as e:
        logger.error(f"Error retrieving pending transactions: {e}")
        return pd.DataFrame()


def get_transaction_by_id(transaction_id: int) -> pd.DataFrame:
    """
    Retrieve a specific transaction by ID.
    
    Args:
        transaction_id: The ID of the transaction to retrieve
        
    Returns:
        DataFrame containing the transaction, or empty DataFrame if not found
    """
    try:
        with get_db_connection() as conn:
            df = pd.read_sql_query(
                "SELECT * FROM transactions WHERE id = ?", 
                conn, 
                params=(transaction_id,)
            )
            return normalize_dataframe(df)
    except Exception as e:
        logger.error(f"Error retrieving transaction {transaction_id}: {e}")
        return pd.DataFrame()


def delete_transaction(transaction_id: int) -> bool:
    """
    Delete a transaction from the database.
    
    Args:
        transaction_id: The ID of the transaction to delete
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('DELETE FROM transactions WHERE id = ?', (transaction_id,))
            conn.commit()
            
            if c.rowcount > 0:
                logger.info(f"Deleted transaction ID {transaction_id}")
                return True
            else:
                logger.warning(f"Transaction ID {transaction_id} not found for deletion")
                return False
                
    except sqlite3.Error as e:
        logger.error(f"Error deleting transaction {transaction_id}: {e}")
        st.error(f"Database error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error deleting transaction: {e}")
        st.error(f"An unexpected error occurred: {e}")
        return False
