"""
Database operations for the Buying & Selling Dashboard Application.
Uses PostgreSQL (Supabase) for cloud persistence.
"""

import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
import pandas as pd
from datetime import datetime
from contextlib import contextmanager
from typing import Optional
import streamlit as st
import os

from config import CONFIG
from logger_setup import logger


def get_database_url() -> str:
    """Get database URL from Streamlit secrets or environment."""
    # Try Streamlit secrets first (for cloud deployment)
    if hasattr(st, 'secrets') and 'DATABASE_URL' in st.secrets:
        return st.secrets['DATABASE_URL']
    # Fall back to environment variable
    return os.environ.get('DATABASE_URL', '')


@contextmanager
def get_db_connection():
    """
    Context manager for PostgreSQL database connections.
    
    Yields:
        psycopg2.connection: Database connection object
        
    Raises:
        psycopg2.Error: If database connection fails
    """
    conn = None
    try:
        database_url = get_database_url()
        if not database_url:
            raise Exception("DATABASE_URL not configured. Please set it in Streamlit secrets.")
        
        conn = psycopg2.connect(database_url, cursor_factory=RealDictCursor)
        yield conn
    except psycopg2.Error as e:
        logger.error(f"Database connection error: {e}")
        raise
    finally:
        if conn:
            conn.close()


def init_database() -> bool:
    """
    Initialize PostgreSQL database with required tables and indexes.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            
            # Create transactions table (PostgreSQL syntax)
            c.execute('''CREATE TABLE IF NOT EXISTS transactions (
                id SERIAL PRIMARY KEY,
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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')
            
            # Create indexes for better query performance
            c.execute('CREATE INDEX IF NOT EXISTS idx_transaction_type ON transactions(transaction_type)')
            c.execute('CREATE INDEX IF NOT EXISTS idx_status ON transactions(status)')
            c.execute('CREATE INDEX IF NOT EXISTS idx_buyer_name ON transactions(buyer_name)')
            c.execute('CREATE INDEX IF NOT EXISTS idx_seller_name ON transactions(seller_name)')
            c.execute('CREATE INDEX IF NOT EXISTS idx_item_name ON transactions(item_name)')
            c.execute('CREATE INDEX IF NOT EXISTS idx_transaction_date ON transactions(transaction_date)')
            
            conn.commit()
            logger.info("Database initialized successfully")
            return True
            
    except psycopg2.Error as e:
        logger.error(f"Database initialization failed: {e}")
        st.error(f"Database initialization failed: {e}")
        return False
    except Exception as e:
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
                "SELECT * FROM transactions WHERE id = %s", 
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
            c.execute('DELETE FROM transactions WHERE id = %s', (transaction_id,))
            conn.commit()
            
            if c.rowcount > 0:
                logger.info(f"Deleted transaction ID {transaction_id}")
                return True
            else:
                logger.warning(f"Transaction ID {transaction_id} not found for deletion")
                return False
                
    except psycopg2.Error as e:
        logger.error(f"Error deleting transaction {transaction_id}: {e}")
        st.error(f"Database error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error deleting transaction: {e}")
        st.error(f"An unexpected error occurred: {e}")
        return False
