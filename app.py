"""
Buying & Selling Dashboard Application
A professional Streamlit application for managing buying and selling transactions
with comprehensive error handling, input validation, and edge case management.

Author: Your Name
Version: 2.0.0
"""

import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os
import logging
from typing import Optional, Tuple, List, Dict, Any, Union
from contextlib import contextmanager
from dataclasses import dataclass
import re
import json

# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class AppConfig:
    """Application configuration settings"""
    DB_PATH: str = "transactions.db"
    APP_TITLE: str = "Buying & Selling Dashboard"
    PAGE_LAYOUT: str = "wide"
    
    # Transaction rates and percentages
    MANDI_CHARGE_RATE: float = 0.015  # 1.5%
    MUDDAT_RATE: float = 0.015  # 1.5%
    CASH_DISCOUNT_RATE: float = 0.04  # 4%
    TRACTOR_RENT_PER_QUINTAL: float = 15.0
    LABOUR_CHARGE_PER_QUINTAL: float = 60.0
    TRANSPORT_CHARGE_PER_QUINTAL: float = 280.0
    
    # Validation limits
    MAX_QUANTITY: float = 10000.0  # Maximum quantity in quintals
    MAX_PRICE: float = 1000000.0  # Maximum price per unit
    MAX_AMOUNT: float = 100000000.0  # Maximum total amount
    MIN_QUANTITY: float = 0.01  # Minimum quantity
    MIN_PRICE: float = 0.01  # Minimum price
    
    # Text validation
    MAX_NAME_LENGTH: int = 100
    MAX_ITEM_NAME_LENGTH: int = 100
    MAX_NOTES_LENGTH: int = 500

# Initialize configuration
CONFIG = AppConfig()

# =============================================================================
# CUSTOM CSS STYLING
# =============================================================================

def inject_custom_css() -> None:
    """Inject custom CSS for professional styling."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Source+Sans+3:wght@400;500;600&display=swap');

    :root {
        --bg: #f6f7fb;
        --bg-accent: #eef1ff;
        --card: #ffffff;
        --text: #1f2937;
        --text-muted: #6b7280;
        --primary: #3b82f6;
        --primary-dark: #2563eb;
        --success: #16a34a;
        --warning: #f59e0b;
        --danger: #ef4444;
        --border: #e5e7eb;
        --shadow: 0 10px 25px rgba(31, 41, 55, 0.08);
        --radius: 12px;
        --font-body: "Source Sans 3", system-ui, -apple-system, Segoe UI, sans-serif;
        --font-display: "Space Grotesk", system-ui, -apple-system, Segoe UI, sans-serif;
    }

    /* Global Styles */
    .stApp {
        background: radial-gradient(1200px 600px at 10% 0%, var(--bg-accent), transparent),
                    radial-gradient(1200px 600px at 90% 0%, #e8f7ff, transparent),
                    var(--bg);
        font-family: var(--font-body);
        color: var(--text);
    }
    
    /* Main Container */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    
    /* Header Styles */
    h1 {
        color: var(--text);
        font-weight: 700;
        font-size: 2.2rem;
        font-family: var(--font-display);
        text-align: center;
        margin-bottom: 1.5rem;
    }
    
    h2 {
        color: var(--text);
        font-weight: 700;
        font-size: 1.6rem;
        font-family: var(--font-display);
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid var(--border);
        padding-bottom: 0.5rem;
    }
    
    h3 {
        color: var(--text);
        font-weight: 600;
        font-size: 1.3rem;
        font-family: var(--font-display);
        margin-top: 1rem;
        margin-bottom: 0.75rem;
    }
    
    /* Metric Cards */
    [data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 600;
        color: #2c3e50;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 0.95rem;
        font-weight: 500;
        color: #6c757d;
    }
    
    [data-testid="stMetricDelta"] {
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    /* Buttons */
    .stButton > button {
        background-color: var(--primary);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.6rem 1.2rem;
        font-weight: 500;
        font-size: 0.95rem;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
    }
    
    .stButton > button:hover {
        background-color: var(--primary-dark);
        box-shadow: 0 4px 8px rgba(0,0,0,0.12);
    }
    
    .stButton > button:active {
        transform: translateY(1px);
    }
    
    /* Form Inputs */
    .stTextInput > div > div > input,
    .stNumberInput > div > div > input,
    .stTextArea > div > div > textarea {
        border-radius: 6px;
        border: 1px solid var(--border);
        padding: 0.6rem;
        font-size: 0.95rem;
        transition: all 0.2s ease;
        background-color: white;
    }
    
    .stTextInput > div > div > input:focus,
    .stNumberInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary);
        box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.1);
        outline: none;
    }
    
    /* Select Box */
    .stSelectbox > div > div > select {
        border-radius: 6px;
        border: 1px solid var(--border);
        padding: 0.6rem;
        font-size: 0.95rem;
        background-color: white;
    }
    
    /* Dataframe */
    .dataframe {
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
    }
    
    [data-testid="stDataFrame"] {
        border-radius: 8px;
        overflow: hidden;
    }
    
    /* Info Messages */
    .stInfo {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
        border-radius: 6px;
        padding: 1rem 1.25rem;
    }
    
    /* Success Messages */
    .stSuccess {
        background-color: #e8f5e9;
        border-left: 4px solid #4caf50;
        border-radius: 6px;
        padding: 1rem 1.25rem;
    }
    
    /* Warning Messages */
    .stWarning {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
        border-radius: 6px;
        padding: 1rem 1.25rem;
    }
    
    /* Error Messages */
    .stError {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        border-radius: 6px;
        padding: 1rem 1.25rem;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0f172a;
    }
    
    [data-testid="stSidebar"] > div:first-child {
        background-color: #0f172a;
    }
    
    [data-testid="stSidebar"] .css-1d391kg {
        color: #ecf0f1;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 2.8rem;
        border-radius: 6px 6px 0 0;
        padding: 0 1.25rem;
        font-weight: 500;
        font-size: 0.95rem;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #f8f9fa;
        border-radius: 6px;
        padding: 0.6rem 1rem;
        font-weight: 500;
        border: 1px solid #e9ecef;
    }
    
    /* Divider */
    hr {
        border: none;
        height: 1px;
        background-color: #e9ecef;
        margin: 2rem 0;
    }
    
    /* Download Button */
    .stDownloadButton > button {
        background-color: #16a34a;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.6rem 1.2rem;
        font-weight: 500;
        font-size: 0.95rem;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.08);
    }
    
    .stDownloadButton > button:hover {
        background-color: #15803d;
        box-shadow: 0 4px 8px rgba(0,0,0,0.12);
    }
    
    /* Progress Bar */
    .stProgress > div > div > div {
        background-color: var(--primary);
    }
    
    /* Chart Container */
    [data-testid="stVerticalBlock"] > [style*="flex-direction: column"] > [data-testid="stVerticalBlock"] {
        background: var(--card);
        border-radius: var(--radius);
        padding: 1.25rem;
        box-shadow: var(--shadow);
        border: 1px solid var(--border);
    }
    
    /* Card Container */
    .card {
        background: var(--card);
        border-radius: var(--radius);
        padding: 1.25rem;
        box-shadow: var(--shadow);
        margin-bottom: 1rem;
        border: 1px solid var(--border);
    }
    
    /* Status Badges */
    .status-badge {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    .status-pending {
        background-color: #fff3cd;
        color: #856404;
    }
    
    .status-completed {
        background-color: #d4edda;
        color: #155724;
    }
    
    .status-sold {
        background-color: #d1ecf1;
        color: #0c5460;
    }
    </style>
    """, unsafe_allow_html=True)

# =============================================================================
# LOGGING SETUP
# =============================================================================

def setup_logging() -> logging.Logger:
    """Configure application logging"""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    
    # Create logs directory if it doesn't exist
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
    
    # File handler
    log_file = os.path.join(logs_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logging()

# =============================================================================
# DATABASE CONTEXT MANAGER
# =============================================================================

@contextmanager
def get_db_connection() -> sqlite3.Connection:
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
        conn.row_factory = sqlite3.Row  # Enable row factory for better data access
        conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign keys
        conn.execute("PRAGMA journal_mode = WAL")  # Enable WAL mode for better concurrency
        yield conn
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        raise
    finally:
        if conn:
            conn.close()

# =============================================================================
# INPUT VALIDATION FUNCTIONS
# =============================================================================

NAME_ALLOWED_PATTERN = re.compile(r"^[\w .,'&/()\-]+$", re.UNICODE)
ITEM_ALLOWED_PATTERN = re.compile(r"^[\w .,'&/()\-+%]+$", re.UNICODE)

def normalize_text(value: str) -> str:
    """Normalize text by trimming and collapsing whitespace."""
    if not value:
        return ""
    return re.sub(r"\s+", " ", value).strip()

def validate_text_field(
    value: str,
    field_name: str,
    max_length: int,
    pattern: Optional[re.Pattern] = None
) -> Tuple[bool, Optional[str]]:
    """
    Validate a text field with length and optional pattern constraints.
    """
    if not value or not value.strip():
        return False, f"{field_name} cannot be empty"

    if len(value) > max_length:
        return False, f"{field_name} exceeds maximum length of {max_length} characters"

    if re.search(r"[<>]", value):
        return False, f"{field_name} contains invalid characters"

    if pattern and not pattern.match(value):
        return False, f"{field_name} contains unsupported characters"

    return True, None

def validate_name(name: str, field_name: str = "Name") -> Tuple[bool, Optional[str]]:
    """Validate a person/organization name field."""
    name = normalize_text(name)
    return validate_text_field(name, field_name, CONFIG.MAX_NAME_LENGTH, NAME_ALLOWED_PATTERN)

def validate_item_name(name: str) -> Tuple[bool, Optional[str]]:
    """Validate an item name field."""
    name = normalize_text(name)
    return validate_text_field(name, "Item Name", CONFIG.MAX_ITEM_NAME_LENGTH, ITEM_ALLOWED_PATTERN)

def validate_numeric_value(
    value: float,
    min_val: float,
    max_val: float,
    field_name: str = "Value"
) -> Tuple[bool, Optional[str]]:
    """
    Validate a numeric value.
    
    Args:
        value: The value to validate
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        field_name: Name of the field for error messages
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if pd.isna(value):
        return False, f"{field_name} cannot be empty"
    
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return False, f"{field_name} must be a number"
    
    if value < min_val:
        return False, f"{field_name} must be at least {min_val}"
    
    if value > max_val:
        return False, f"{field_name} cannot exceed {max_val}"
    
    return True, None

def validate_notes(notes: str) -> Tuple[bool, Optional[str]]:
    """
    Validate notes field.
    
    Args:
        notes: The notes to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not notes:
        return True, None  # Notes are optional
    
    if len(notes) > CONFIG.MAX_NOTES_LENGTH:
        return False, f"Notes exceed maximum length of {CONFIG.MAX_NOTES_LENGTH} characters"
    
    # Disallow HTML/script injection characters
    if re.search(r"[<>]", notes):
        return False, "Notes contain invalid characters"
    
    return True, None

def sanitize_string(input_str: str) -> str:
    """
    Sanitize a string input by removing potentially harmful characters.
    
    Args:
        input_str: The string to sanitize
        
    Returns:
        Sanitized string
    """
    if not input_str:
        return ""
    
    # Remove potentially dangerous characters and normalize whitespace
    sanitized = re.sub(r"[<>]", "", input_str)
    return normalize_text(sanitized)

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

# =============================================================================
# DATABASE INITIALIZATION
# =============================================================================

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
                    # Column already exists
                    pass
            
            conn.commit()
            logger.info("Database initialized successfully")
            return True
            
    except sqlite3.Error as e:
        logger.error(f"Database initialization failed: {e}")
        st.error(f"Database initialization failed: {e}")
        return False

# =============================================================================
# TRANSACTION FUNCTIONS
# =============================================================================

def add_buying_transaction(
    buyer_name: str,
    item_name: str,
    quantity_quintal: float,
    price_per_unit: float,
    mandi_charge: float,
    tractor_rent: float,
    muddat: float,
    total_amount: float,
    amount_paid: float = 0.0,
    notes: str = ""
) -> Optional[int]:
    """
    Add a buying transaction to the database.
    
    Args:
        buyer_name: Name of the buyer
        item_name: Name of the item
        quantity_quintal: Quantity in quintals
        price_per_unit: Price per quintal
        mandi_charge: Mandi charge amount
        tractor_rent: Tractor rent amount
        muddat: Muddat amount
        total_amount: Total amount
        amount_paid: Amount already paid
        notes: Additional notes
        
    Returns:
        Transaction ID if successful, None otherwise
    """
    try:
        # Validate inputs
        is_valid, error_msg = validate_name(buyer_name, "Buyer Name")
        if not is_valid:
            st.error(error_msg)
            return None
        
        is_valid, error_msg = validate_item_name(item_name)
        if not is_valid:
            st.error(error_msg)
            return None
        
        is_valid, error_msg = validate_numeric_value(
            quantity_quintal, CONFIG.MIN_QUANTITY, CONFIG.MAX_QUANTITY, "Quantity"
        )
        if not is_valid:
            st.error(error_msg)
            return None
        
        is_valid, error_msg = validate_numeric_value(
            price_per_unit, CONFIG.MIN_PRICE, CONFIG.MAX_PRICE, "Price per Unit"
        )
        if not is_valid:
            st.error(error_msg)
            return None
        
        is_valid, error_msg = validate_numeric_value(
            amount_paid, 0, CONFIG.MAX_AMOUNT, "Amount Paid"
        )
        if not is_valid:
            st.error(error_msg)
            return None
        
        is_valid, error_msg = validate_notes(notes)
        if not is_valid:
            st.error(error_msg)
            return None
        
        # Sanitize inputs
        buyer_name = sanitize_string(buyer_name)
        item_name = sanitize_string(item_name)
        notes = sanitize_string(notes)
        
        # Calculate base amount
        base_amount = price_per_unit * quantity_quintal
        transaction_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if amount_paid > total_amount:
            st.error("Amount Paid cannot exceed total amount")
            return None
        
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO transactions 
                         (transaction_type, buyer_name, seller_name, item_name, quantity_kg, 
                          price_per_unit, base_amount, mandi_charge, tractor_rent, muddat, 
                          cash_discount, labour_charge, transport_charge, total_amount, 
                          amount_paid, transaction_date, notes, status)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      ('BUY', buyer_name, None, item_name, quantity_quintal, price_per_unit, 
                       base_amount, mandi_charge, tractor_rent, muddat, 0, 0, 0,
                       total_amount, amount_paid, transaction_date, notes, 'PENDING'))
            
            conn.commit()
            transaction_id = c.lastrowid
            logger.info(f"Added buying transaction ID {transaction_id} for buyer {buyer_name}")
            return transaction_id
            
    except sqlite3.Error as e:
        logger.error(f"Error adding buying transaction: {e}")
        st.error(f"Database error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error adding buying transaction: {e}")
        st.error(f"An unexpected error occurred: {e}")
        return None

def add_selling_transaction(
    seller_name: str,
    item_name: str,
    quantity_quintal: float,
    price_per_unit: float,
    cash_discount: float,
    labour_charge: float,
    transport_charge: float,
    total_amount: float,
    amount_paid: float = 0.0,
    buy_transaction_id: Optional[int] = None,
    notes: str = ""
) -> Optional[int]:
    """
    Add a selling transaction to the database.
    
    Args:
        seller_name: Name of the seller
        item_name: Name of the item
        quantity_quintal: Quantity in quintals
        price_per_unit: Selling price per quintal
        cash_discount: Cash discount amount
        labour_charge: Labour charge amount
        transport_charge: Transport charge amount
        total_amount: Total amount
        amount_paid: Amount already received
        buy_transaction_id: Optional linked buying transaction ID
        notes: Additional notes
        
    Returns:
        Transaction ID if successful, None otherwise
    """
    try:
        # Validate inputs
        is_valid, error_msg = validate_name(seller_name, "Seller Name")
        if not is_valid:
            st.error(error_msg)
            return None
        
        is_valid, error_msg = validate_item_name(item_name)
        if not is_valid:
            st.error(error_msg)
            return None
        
        is_valid, error_msg = validate_numeric_value(
            quantity_quintal, CONFIG.MIN_QUANTITY, CONFIG.MAX_QUANTITY, "Quantity"
        )
        if not is_valid:
            st.error(error_msg)
            return None
        
        is_valid, error_msg = validate_numeric_value(
            price_per_unit, CONFIG.MIN_PRICE, CONFIG.MAX_PRICE, "Price per Unit"
        )
        if not is_valid:
            st.error(error_msg)
            return None
        
        is_valid, error_msg = validate_numeric_value(
            amount_paid, 0, CONFIG.MAX_AMOUNT, "Amount Received"
        )
        if not is_valid:
            st.error(error_msg)
            return None
        
        is_valid, error_msg = validate_notes(notes)
        if not is_valid:
            st.error(error_msg)
            return None
        
        # Sanitize inputs
        seller_name = sanitize_string(seller_name)
        item_name = sanitize_string(item_name)
        notes = sanitize_string(notes)
        
        # Calculate base amount
        base_amount = price_per_unit * quantity_quintal
        transaction_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if amount_paid > total_amount:
            st.error("Amount Received cannot exceed total amount")
            return None

        # Validate linked purchase
        if buy_transaction_id:
            linked = get_transaction_by_id(buy_transaction_id)
            if linked.empty:
                st.error("Linked purchase not found")
                return None
            linked_row = linked.iloc[0]
            if linked_row.get("transaction_type") != "BUY" or linked_row.get("status") != "PENDING":
                st.error("Linked purchase must be a pending BUY transaction")
                return None
            try:
                linked_qty = float(linked_row.get("quantity_kg", 0))
                if quantity_quintal > linked_qty:
                    st.error("Selling quantity cannot exceed linked purchase quantity")
                    return None
            except (TypeError, ValueError):
                st.error("Invalid quantity on linked purchase")
                return None
        
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO transactions 
                         (transaction_type, buyer_name, seller_name, item_name, quantity_kg, 
                          price_per_unit, base_amount, mandi_charge, tractor_rent, muddat, 
                          cash_discount, labour_charge, transport_charge, total_amount, 
                          amount_paid, transaction_date, notes, status)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      ('SELL', None, seller_name, item_name, quantity_quintal, price_per_unit, 
                       base_amount, 0, 0, 0, cash_discount, labour_charge, transport_charge,
                       total_amount, amount_paid, transaction_date, notes, 'COMPLETED'))
            
            conn.commit()
            transaction_id = c.lastrowid
            
            # If linked to a buying transaction, update its status
            if buy_transaction_id:
                c.execute('UPDATE transactions SET status = ?, updated_at = ? WHERE id = ?',
                         ('SOLD', datetime.now().strftime("%Y-%m-%d %H:%M:%S"), buy_transaction_id))
                conn.commit()
                logger.info(f"Linked selling transaction ID {transaction_id} to buying transaction ID {buy_transaction_id}")
            
            logger.info(f"Added selling transaction ID {transaction_id} for seller {seller_name}")
            return transaction_id
            
    except sqlite3.Error as e:
        logger.error(f"Error adding selling transaction: {e}")
        st.error(f"Database error: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error adding selling transaction: {e}")
        st.error(f"An unexpected error occurred: {e}")
        return None

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

def update_payment(transaction_id: int, amount_paid: float) -> bool:
    """
    Update the amount paid for a transaction.
    
    Args:
        transaction_id: The ID of the transaction
        amount_paid: The new amount paid
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Validate input
        is_valid, error_msg = validate_numeric_value(
            amount_paid, 0, CONFIG.MAX_AMOUNT, "Amount Paid"
        )
        if not is_valid:
            st.error(error_msg)
            return False

        # Fetch total amount to validate against
        transaction_df = get_transaction_by_id(transaction_id)
        if transaction_df.empty:
            st.error("Transaction not found")
            return False
        total_amount = pd.to_numeric(
            transaction_df.iloc[0].get("total_amount", 0),
            errors="coerce"
        )
        if pd.isna(total_amount):
            st.error("Invalid total amount for this transaction")
            return False
        if amount_paid > float(total_amount):
            st.error("Amount Paid cannot exceed total amount")
            return False

        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('''UPDATE transactions 
                         SET amount_paid = ?, updated_at = ? 
                         WHERE id = ?''',
                     (amount_paid, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), transaction_id))
            conn.commit()
            
            if c.rowcount > 0:
                logger.info(f"Updated payment for transaction ID {transaction_id} to ₹{amount_paid}")
                return True
            else:
                logger.warning(f"Transaction ID {transaction_id} not found")
                return False
                
    except sqlite3.Error as e:
        logger.error(f"Error updating payment for transaction {transaction_id}: {e}")
        st.error(f"Database error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error updating payment: {e}")
        st.error(f"An unexpected error occurred: {e}")
        return False

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

# =============================================================================
# CALCULATION FUNCTIONS
# =============================================================================

def calculate_buying_price(
    buying_price: float,
    weight_quintal: float
) -> Tuple[float, float, float, float]:
    """
    Calculate total buying cost including all charges.
    
    Args:
        buying_price: Base buying price
        weight_quintal: Weight in quintals
        
    Returns:
        Tuple of (total_buying_price, mandi_charge, tractor_rent, muddat)
        
    Raises:
        ValueError: If inputs are invalid
    """
    # Validate inputs
    if buying_price <= 0:
        raise ValueError("Buying price must be positive")
    if weight_quintal <= 0:
        raise ValueError("Weight must be positive")
    
    mandi_charge = CONFIG.MANDI_CHARGE_RATE * buying_price
    tractor_rent = CONFIG.TRACTOR_RENT_PER_QUINTAL * weight_quintal
    muddat = CONFIG.MUDDAT_RATE * buying_price
    total_buying_price = buying_price + mandi_charge + tractor_rent + muddat
    
    return total_buying_price, mandi_charge, tractor_rent, muddat

def calculate_selling_price(
    selling_price: float,
    weight_quintal: float
) -> Tuple[float, float, float, float]:
    """
    Calculate total selling revenue after deducting charges.
    
    Args:
        selling_price: Base selling price
        weight_quintal: Weight in quintals
        
    Returns:
        Tuple of (total_selling_price, cash_discount, labour_charge, transport_charge)
        
    Raises:
        ValueError: If inputs are invalid
    """
    # Validate inputs
    if selling_price <= 0:
        raise ValueError("Selling price must be positive")
    if weight_quintal <= 0:
        raise ValueError("Weight must be positive")
    
    cash_discount = CONFIG.CASH_DISCOUNT_RATE * selling_price
    labour_charge = CONFIG.LABOUR_CHARGE_PER_QUINTAL * weight_quintal
    transport_charge = CONFIG.TRANSPORT_CHARGE_PER_QUINTAL * weight_quintal
    total_selling_price = selling_price - cash_discount - labour_charge - transport_charge
    
    # Ensure total is not negative
    if total_selling_price < 0:
        logger.warning(f"Total selling price is negative: {total_selling_price}")
        total_selling_price = 0
    
    return total_selling_price, cash_discount, labour_charge, transport_charge

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def format_currency(amount: float) -> str:
    """
    Format a number as Indian currency.
    
    Args:
        amount: The amount to format
        
    Returns:
        Formatted currency string
    """
    if pd.isna(amount):
        return "₹0.00"
    return f"₹{amount:,.2f}"

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, returning default if denominator is zero.
    
    Args:
        numerator: The numerator
        denominator: The denominator
        default: Default value to return if division fails
        
    Returns:
        Result of division or default value
    """
    try:
        if denominator == 0 or pd.isna(denominator):
            return default
        return numerator / denominator
    except (TypeError, ZeroDivisionError):
        return default

def get_transaction_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Get a summary of transactions from a DataFrame.
    
    Args:
        df: DataFrame containing transactions
        
    Returns:
        Dictionary containing summary statistics
    """
    if df.empty:
        return {
            'total_buy': 0.0,
            'total_sell': 0.0,
            'profit_loss': 0.0,
            'pending_count': 0,
            'total_transactions': 0
        }
    
    df = df.copy()
    if 'total_amount' in df.columns:
        df['total_amount'] = pd.to_numeric(df['total_amount'], errors='coerce').fillna(0)
    buy_df = df[df['transaction_type'] == 'BUY']
    sell_df = df[df['transaction_type'] == 'SELL']
    
    total_buy = buy_df['total_amount'].sum() if not buy_df.empty else 0.0
    total_sell = sell_df['total_amount'].sum() if not sell_df.empty else 0.0
    profit_loss = total_sell - total_buy
    pending_count = len(df[df['status'] == 'PENDING'])
    
    return {
        'total_buy': total_buy,
        'total_sell': total_sell,
        'profit_loss': profit_loss,
        'pending_count': pending_count,
        'total_transactions': len(df)
    }

# =============================================================================
# STREAMLIT UI COMPONENTS
# =============================================================================

def display_metric(label: str, value: str, delta: Optional[str] = None) -> None:
    """
    Display a metric with consistent styling.
    
    Args:
        label: Metric label
        value: Metric value
        delta: Optional delta value
    """
    st.metric(label, value, delta)

def display_success_message(message: str) -> None:
    """Display a success message with logging."""
    st.success(message)
    logger.info(message)

def display_error_message(message: str) -> None:
    """Display an error message with logging."""
    st.error(message)
    logger.error(message)

def display_warning_message(message: str) -> None:
    """Display a warning message with logging."""
    st.warning(message)
    logger.warning(message)

def display_info_message(message: str) -> None:
    """Display an info message with logging."""
    st.info(message)
    logger.info(message)

# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main() -> None:
    """Main application entry point."""
    try:
        # Configure page
        st.set_page_config(
            page_title=CONFIG.APP_TITLE,
            layout=CONFIG.PAGE_LAYOUT,
            page_icon="📊",
            initial_sidebar_state="expanded"
        )
        
        # Inject custom CSS
        inject_custom_css()
        
        # Initialize database
        if not init_database():
            st.error("Failed to initialize database. Please check the logs.")
            return
        
        # Initialize session state
        session_defaults = {
            'show_delete_confirmation': False,
            'transaction_to_delete': None,
            'last_refresh': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        for key, default_value in session_defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
        
        # Main Streamlit app with clean header
        st.markdown("""
        <div style='text-align: center; padding: 2rem; border-radius: 16px;
                    background: linear-gradient(135deg, #e0f2fe 0%, #eef2ff 50%, #f8fafc 100%);
                    border: 1px solid #e5e7eb; box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);'>
            <div style='font-size: 0.9rem; color: #64748b; letter-spacing: 0.08em; text-transform: uppercase;'>
                Business Control Center
            </div>
            <h1 style='margin: 0.35rem 0 0; font-size: 2.6rem; color: #0f172a;'>
                Buying & Selling Dashboard
            </h1>
            <p style='color: #475569; font-size: 1.05rem; margin-top: 0.5rem;'>
                Track purchases, sales, and cashflow in one place
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Sidebar navigation
        st.sidebar.markdown("""
        <div style='padding: 1rem 0;'>
            <h2 style='color: #ecf0f1; font-size: 1.3rem; margin: 0;'>
                Navigation
            </h2>
        </div>
        """, unsafe_allow_html=True)
        
        page = st.sidebar.radio(
            "",
            [
                "Dashboard",
                "Record Buying",
                "Record Selling",
                "View Transactions",
                "Pending Inventory",
                "Buyer/Seller Ledger",
                "Settings"
            ],
            label_visibility="collapsed"
        )
        
        # Route to appropriate page
        if page == "Dashboard":
            render_dashboard()
        elif page == "Record Buying":
            render_record_buying()
        elif page == "Record Selling":
            render_record_selling()
        elif page == "View Transactions":
            render_view_transactions()
        elif page == "Pending Inventory":
            render_pending_inventory()
        elif page == "Buyer/Seller Ledger":
            render_ledger()
        elif page == "Settings":
            render_settings()
            
    except Exception as e:
        logger.error(f"Application error: {e}")
        st.error(f"An unexpected error occurred: {e}")
        st.error("Please refresh the page or contact support.")

def render_dashboard() -> None:
    """Render the dashboard page."""
    st.markdown("""
    <div style='background-color: white; padding: 1.5rem; border-radius: 8px; 
               box-shadow: 0 2px 4px rgba(0,0,0,0.08); margin-bottom: 2rem; border: 1px solid #e9ecef;'>
        <h2 style='color: #2c3e50; margin: 0; font-size: 1.6rem;'>
            Dashboard Overview
        </h2>
        <p style='color: #6c757d; margin: 0.5rem 0 0 0;'>
            Monitor your business performance at a glance
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        df = get_all_transactions()
        
        if not df.empty:
            summary = get_transaction_summary(df)
            
            # Summary metrics
            st.markdown("""
            <div style='margin-bottom: 1.5rem;'>
                <h3 style='color: #34495e; margin-bottom: 1rem;'>Key Metrics</h3>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div style='background: white; padding: 1.25rem; border-radius: 8px; 
                           box-shadow: 0 2px 4px rgba(0,0,0,0.08); text-align: center; border: 1px solid #e9ecef;'>
                    <div style='font-size: 2rem; font-weight: 600; color: #2c3e50; margin-bottom: 0.5rem;'>
                        {format_currency(summary['total_buy'])}
                    </div>
                    <div style='color: #6c757d; font-weight: 500; font-size: 0.9rem;'>
                        Total Buying Cost
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div style='background: white; padding: 1.25rem; border-radius: 8px; 
                           box-shadow: 0 2px 4px rgba(0,0,0,0.08); text-align: center; border: 1px solid #e9ecef;'>
                    <div style='font-size: 2rem; font-weight: 600; color: #2c3e50; margin-bottom: 0.5rem;'>
                        {format_currency(summary['total_sell'])}
                    </div>
                    <div style='color: #6c757d; font-weight: 500; font-size: 0.9rem;'>
                        Total Selling Revenue
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                profit_color = "#27ae60" if summary['profit_loss'] >= 0 else "#e74c3c"
                st.markdown(f"""
                <div style='background: white; padding: 1.25rem; border-radius: 8px; 
                           box-shadow: 0 2px 4px rgba(0,0,0,0.08); text-align: center; border: 1px solid #e9ecef;'>
                    <div style='font-size: 2rem; font-weight: 600; color: {profit_color}; margin-bottom: 0.5rem;'>
                        {format_currency(summary['profit_loss'])}
                    </div>
                    <div style='color: #6c757d; font-weight: 500; font-size: 0.9rem;'>
                        Net Profit/Loss
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div style='background: white; padding: 1.25rem; border-radius: 8px; 
                           box-shadow: 0 2px 4px rgba(0,0,0,0.08); text-align: center; border: 1px solid #e9ecef;'>
                    <div style='font-size: 2rem; font-weight: 600; color: #2c3e50; margin-bottom: 0.5rem;'>
                        {summary['pending_count']}
                    </div>
                    <div style='color: #6c757d; font-weight: 500; font-size: 0.9rem;'>
                        Pending Inventory
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Charts section
            st.markdown("<hr style='margin: 2rem 0;'>", unsafe_allow_html=True)
            st.markdown("""
            <div style='margin-bottom: 1.5rem;'>
                <h3 style='color: #34495e; margin-bottom: 1rem;'>Analytics</h3>
            </div>
            """, unsafe_allow_html=True)
            
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.markdown("""
                <div style='background: white; padding: 1.25rem; border-radius: 8px; 
                           box-shadow: 0 2px 4px rgba(0,0,0,0.08); margin-bottom: 1rem; border: 1px solid #e9ecef;'>
                    <h4 style='color: #34495e; margin-top: 0;'>Transaction Type Distribution</h4>
                </div>
                """, unsafe_allow_html=True)
                transaction_counts = df['transaction_type'].value_counts()
                if not transaction_counts.empty:
                    st.bar_chart(transaction_counts, color="#3498db")
                else:
                    st.info("No transaction data available")
            
            with col_chart2:
                st.markdown("""
                <div style='background: white; padding: 1.25rem; border-radius: 8px; 
                           box-shadow: 0 2px 4px rgba(0,0,0,0.08); margin-bottom: 1rem; border: 1px solid #e9ecef;'>
                    <h4 style='color: #34495e; margin-top: 0;'>Transaction Status Distribution</h4>
                </div>
                """, unsafe_allow_html=True)
                status_counts = df['status'].value_counts()
                if not status_counts.empty:
                    st.bar_chart(status_counts, color="#2ecc71")
                else:
                    st.info("No status data available")
            
            # Recent transactions section
            st.markdown("<hr style='margin: 2rem 0;'>", unsafe_allow_html=True)
            st.markdown("""
            <div style='margin-bottom: 1.5rem;'>
                <h3 style='color: #34495e; margin-bottom: 1rem;'>Recent Transactions</h3>
            </div>
            """, unsafe_allow_html=True)
            
            recent_df = df.head(10)
            display_columns = ['id', 'transaction_type', 'item_name', 'quantity_kg', 
                             'total_amount', 'transaction_date', 'status']
            available_columns = [col for col in display_columns if col in recent_df.columns]
            
            st.markdown("""
            <div style='background: white; padding: 1.25rem; border-radius: 8px; 
                       box-shadow: 0 2px 4px rgba(0,0,0,0.08); border: 1px solid #e9ecef;'>
            """, unsafe_allow_html=True)
            st.dataframe(
                recent_df[available_columns].rename(columns={'quantity_kg': 'Quantity (Quintal)'}),
                use_container_width=True,
                height=300
            )
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='background-color: #f8f9fa; padding: 3rem; border-radius: 8px; 
                       text-align: center; border: 1px solid #e9ecef;'>
                <div style='font-size: 3rem; margin-bottom: 1rem; color: #6c757d;'>📝</div>
                <h3 style='color: #2c3e50; margin: 0 0 0.5rem 0;'>No Transactions Yet</h3>
                <p style='color: #6c757d; margin: 0;'>
                    Start by recording your first transaction to see your dashboard come to life!
                </p>
            </div>
            """, unsafe_allow_html=True)
            
    except Exception as e:
        logger.error(f"Error rendering dashboard: {e}")
        display_error_message(f"Error loading dashboard: {e}")

def render_record_buying() -> None:
    """Render the record buying transaction page."""
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem;'>
        <h2 style='color: white; margin: 0; font-size: 1.8rem;'>
            📥 Record Buying Transaction
        </h2>
        <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;'>
            Add new purchase transactions to your inventory
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background: white; padding: 2rem; border-radius: 12px; 
               box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 2rem;'>
        <h3 style='color: #1a1a2e; margin-top: 0;'>Transaction Details</h3>
        <p style='color: #4a5568; margin-bottom: 1.5rem;'>
            Fill in the details below to record a new buying transaction
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("buying_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style='margin-bottom: 0.5rem;'>
                <label style='color: #1a1a2e; font-weight: 600;'>Buyer Name *</label>
            </div>
            """, unsafe_allow_html=True)
            buyer_name = st.text_input(
                "",
                placeholder="e.g., Farmer Name/Organization",
                max_chars=CONFIG.MAX_NAME_LENGTH,
                label_visibility="collapsed"
            )
            
            st.markdown("""
            <div style='margin-bottom: 0.5rem; margin-top: 1rem;'>
                <label style='color: #1a1a2e; font-weight: 600;'>Item Name *</label>
            </div>
            """, unsafe_allow_html=True)
            item_name = st.text_input(
                "",
                placeholder="e.g., Rice, Wheat",
                max_chars=CONFIG.MAX_ITEM_NAME_LENGTH,
                label_visibility="collapsed"
            )
        
        with col2:
            st.markdown("""
            <div style='margin-bottom: 0.5rem;'>
                <label style='color: #1a1a2e; font-weight: 600;'>Quantity (Quintal) *</label>
            </div>
            """, unsafe_allow_html=True)
            quantity_quintal = st.number_input(
                "",
                min_value=CONFIG.MIN_QUANTITY,
                max_value=CONFIG.MAX_QUANTITY,
                value=1.0,
                step=0.5,
                format="%.2f",
                label_visibility="collapsed"
            )
            
            st.markdown("""
            <div style='margin-bottom: 0.5rem; margin-top: 1rem;'>
                <label style='color: #1a1a2e; font-weight: 600;'>Price per Quintal (₹) *</label>
            </div>
            """, unsafe_allow_html=True)
            price_per_unit = st.number_input(
                "",
                min_value=CONFIG.MIN_PRICE,
                max_value=CONFIG.MAX_PRICE,
                value=1000.0,
                step=100.0,
                format="%.2f",
                label_visibility="collapsed"
            )
        
        with col3:
            st.markdown("""
            <div style='margin-bottom: 0.5rem;'>
                <label style='color: #1a1a2e; font-weight: 600;'>Amount Paid (₹)</label>
            </div>
            """, unsafe_allow_html=True)
            amount_paid = st.number_input(
                "",
                min_value=0.0,
                max_value=CONFIG.MAX_AMOUNT,
                value=0.0,
                step=100.0,
                format="%.2f",
                label_visibility="collapsed"
            )
            
            st.markdown("""
            <div style='margin-bottom: 0.5rem; margin-top: 1rem;'>
                <label style='color: #1a1a2e; font-weight: 600;'>Notes (Optional)</label>
            </div>
            """, unsafe_allow_html=True)
            notes = st.text_area(
                "",
                placeholder="Any additional notes",
                max_chars=CONFIG.MAX_NOTES_LENGTH,
                label_visibility="collapsed"
            )
        
        st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("📝 Record Buying Transaction", use_container_width=True)
        
        if submitted:
            if buyer_name and item_name and quantity_quintal > 0 and price_per_unit > 0:
                try:
                    base_amount = price_per_unit * quantity_quintal
                    total_amount, mandi_charge, tractor_rent, muddat = calculate_buying_price(
                        base_amount, quantity_quintal
                    )
                    
                    # Add to database
                    transaction_id = add_buying_transaction(
                        buyer_name, item_name, quantity_quintal, price_per_unit,
                        mandi_charge, tractor_rent, muddat,
                        total_amount, amount_paid, notes
                    )
                    
                    if transaction_id:
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #48bb7815 0%, #38a16915 100%); 
                                   padding: 1.5rem; border-radius: 12px; border-left: 4px solid #48bb78; margin-bottom: 1.5rem;'>
                            <div style='display: flex; align-items: center;'>
                                <div style='font-size: 2rem; margin-right: 1rem;'>✅</div>
                                <div>
                                    <h4 style='color: #065f46; margin: 0 0 0.25rem 0;'>
                                        Buying Transaction Recorded Successfully!
                                    </h4>
                                    <p style='color: #065f46; margin: 0;'>
                                        Transaction ID: {transaction_id}
                                    </p>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Show breakdown
                        with st.expander("💰 Cost Breakdown", expanded=True):
                            st.markdown("""
                            <div style='background: white; padding: 1.5rem; border-radius: 12px; 
                                       box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                            """, unsafe_allow_html=True)
                            col_b1, col_b2 = st.columns(2)
                            with col_b1:
                                st.markdown(f"""
                                <div style='margin-bottom: 0.75rem;'>
                                    <span style='color: #4a5568;'>Base Price:</span>
                                    <span style='color: #1a1a2e; font-weight: 700; float: right;'>{format_currency(base_amount)}</span>
                                </div>
                                <div style='margin-bottom: 0.75rem;'>
                                    <span style='color: #4a5568;'>Mandi Charge ({CONFIG.MANDI_CHARGE_RATE*100}%):</span>
                                    <span style='color: #1a1a2e; font-weight: 700; float: right;'>{format_currency(mandi_charge)}</span>
                                </div>
                                """, unsafe_allow_html=True)
                            with col_b2:
                                st.markdown(f"""
                                <div style='margin-bottom: 0.75rem;'>
                                    <span style='color: #4a5568;'>Tractor Rent (₹{CONFIG.TRACTOR_RENT_PER_QUINTAL}/Quintal):</span>
                                    <span style='color: #1a1a2e; font-weight: 700; float: right;'>{format_currency(tractor_rent)}</span>
                                </div>
                                <div style='margin-bottom: 0.75rem;'>
                                    <span style='color: #4a5568;'>Muddat ({CONFIG.MUDDAT_RATE*100}%):</span>
                                    <span style='color: #1a1a2e; font-weight: 700; float: right;'>{format_currency(muddat)}</span>
                                </div>
                                """, unsafe_allow_html=True)
                            st.markdown(f"""
                            <div style='border-top: 2px solid #667eea; padding-top: 1rem; margin-top: 1rem;'>
                                <span style='color: #1a1a2e; font-weight: 700; font-size: 1.2rem;'>Total:</span>
                                <span style='color: #667eea; font-weight: 700; font-size: 1.2rem; float: right;'>{format_currency(total_amount)}</span>
                            </div>
                            </div>
                            """, unsafe_allow_html=True)
                except ValueError as e:
                    display_error_message(f"Calculation error: {e}")
                except Exception as e:
                    display_error_message(f"An unexpected error occurred: {e}")
            else:
                st.markdown("""
                <div style='background: linear-gradient(135deg, #f5656515 0%, #e53e3e15 100%); 
                           padding: 1.5rem; border-radius: 12px; border-left: 4px solid #f56565;'>
                    <div style='display: flex; align-items: center;'>
                        <div style='font-size: 2rem; margin-right: 1rem;'>❌</div>
                        <div>
                            <h4 style='color: #c53030; margin: 0 0 0.25rem 0;'>
                                Validation Error
                            </h4>
                            <p style='color: #c53030; margin: 0;'>
                                Please fill all required fields with valid values
                            </p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

def render_record_selling() -> None:
    """Render the record selling transaction page."""
    st.markdown("""
    <div style='background: linear-gradient(135deg, #48bb78 0%, #38a169 100%); 
                padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem;'>
        <h2 style='color: white; margin: 0; font-size: 1.8rem;'>
            📤 Record Selling Transaction
        </h2>
        <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;'>
            Record sales and link them to your inventory
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Option to link with pending buying transaction
    st.markdown("""
    <div style='background: white; padding: 1.5rem; border-radius: 12px; 
               box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 1.5rem;'>
        <h3 style='color: #1a1a2e; margin-top: 0;'>🔗 Link with Previous Purchase (Optional)</h3>
    </div>
    """, unsafe_allow_html=True)
    
    pending_df = get_pending_transactions()
    
    link_purchase = None
    if not pending_df.empty:
        st.markdown("""
        <div style='background: #f7fafc; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;'>
            <p style='color: #4a5568; margin: 0;'>Select a pending purchase to link:</p>
        </div>
        """, unsafe_allow_html=True)
        purchase_options = {
            f"ID {row['id']} - {row['item_name']} ({row['quantity_kg']} Quintal)": row['id']
            for _, row in pending_df.iterrows()
        }
        
        selected_purchase = st.selectbox(
            "",
            options=[None] + list(purchase_options.keys()),
            format_func=lambda x: "No specific purchase" if x is None else x,
            label_visibility="collapsed"
        )
        
        if selected_purchase:
            link_purchase = purchase_options[selected_purchase]
    else:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); 
                   padding: 1.5rem; border-radius: 12px; border-left: 4px solid #667eea;'>
            <div style='display: flex; align-items: center;'>
                <div style='font-size: 2rem; margin-right: 1rem;'>ℹ️</div>
                <div>
                    <h4 style='color: #1a1a2e; margin: 0 0 0.25rem 0;'>
                        No Pending Purchases
                    </h4>
                    <p style='color: #4a5568; margin: 0;'>
                        You can still record a new selling transaction without linking.
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<hr style='margin: 2rem 0;'>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background: white; padding: 2rem; border-radius: 12px; 
               box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 2rem;'>
        <h3 style='color: #1a1a2e; margin-top: 0;'>Transaction Details</h3>
        <p style='color: #4a5568; margin-bottom: 1.5rem;'>
            Fill in the details below to record a new selling transaction
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("selling_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style='margin-bottom: 0.5rem;'>
                <label style='color: #1a1a2e; font-weight: 600;'>Seller Name *</label>
            </div>
            """, unsafe_allow_html=True)
            seller_name = st.text_input(
                "",
                placeholder="e.g., Market/Buyer Name",
                max_chars=CONFIG.MAX_NAME_LENGTH,
                label_visibility="collapsed"
            )
            
            st.markdown("""
            <div style='margin-bottom: 0.5rem; margin-top: 1rem;'>
                <label style='color: #1a1a2e; font-weight: 600;'>Item Name *</label>
            </div>
            """, unsafe_allow_html=True)
            item_name = st.text_input(
                "",
                placeholder="e.g., Rice, Wheat",
                max_chars=CONFIG.MAX_ITEM_NAME_LENGTH,
                label_visibility="collapsed"
            )
        
        with col2:
            st.markdown("""
            <div style='margin-bottom: 0.5rem;'>
                <label style='color: #1a1a2e; font-weight: 600;'>Quantity (Quintal) *</label>
            </div>
            """, unsafe_allow_html=True)
            quantity_quintal = st.number_input(
                "",
                min_value=CONFIG.MIN_QUANTITY,
                max_value=CONFIG.MAX_QUANTITY,
                value=1.0,
                step=0.5,
                format="%.2f",
                label_visibility="collapsed"
            )
            
            st.markdown("""
            <div style='margin-bottom: 0.5rem; margin-top: 1rem;'>
                <label style='color: #1a1a2e; font-weight: 600;'>Selling Price per Quintal (₹) *</label>
            </div>
            """, unsafe_allow_html=True)
            price_per_unit = st.number_input(
                "",
                min_value=CONFIG.MIN_PRICE,
                max_value=CONFIG.MAX_PRICE,
                value=1200.0,
                step=100.0,
                format="%.2f",
                label_visibility="collapsed"
            )
        
        with col3:
            st.markdown("""
            <div style='margin-bottom: 0.5rem;'>
                <label style='color: #1a1a2e; font-weight: 600;'>Amount Received (₹)</label>
            </div>
            """, unsafe_allow_html=True)
            amount_paid = st.number_input(
                "",
                min_value=0.0,
                max_value=CONFIG.MAX_AMOUNT,
                value=0.0,
                step=100.0,
                format="%.2f",
                label_visibility="collapsed"
            )
            
            st.markdown("""
            <div style='margin-bottom: 0.5rem; margin-top: 1rem;'>
                <label style='color: #1a1a2e; font-weight: 600;'>Notes (Optional)</label>
            </div>
            """, unsafe_allow_html=True)
            notes = st.text_area(
                "",
                placeholder="Any additional notes",
                max_chars=CONFIG.MAX_NOTES_LENGTH,
                label_visibility="collapsed"
            )
        
        st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("📝 Record Selling Transaction", use_container_width=True)
        
        if submitted:
            if seller_name and item_name and quantity_quintal > 0 and price_per_unit > 0:
                try:
                    base_amount = price_per_unit * quantity_quintal
                    total_amount, cash_discount, labour_charge, transport_charge = calculate_selling_price(
                        base_amount, quantity_quintal
                    )
                    
                    # Add to database
                    transaction_id = add_selling_transaction(
                        seller_name, item_name, quantity_quintal, price_per_unit,
                        cash_discount, labour_charge, transport_charge,
                        total_amount, amount_paid, link_purchase, notes
                    )
                    
                    if transaction_id:
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #48bb7815 0%, #38a16915 100%); 
                                   padding: 1.5rem; border-radius: 12px; border-left: 4px solid #48bb78; margin-bottom: 1.5rem;'>
                            <div style='display: flex; align-items: center;'>
                                <div style='font-size: 2rem; margin-right: 1rem;'>✅</div>
                                <div>
                                    <h4 style='color: #065f46; margin: 0 0 0.25rem 0;'>
                                        Selling Transaction Recorded Successfully!
                                    </h4>
                                    <p style='color: #065f46; margin: 0;'>
                                        Transaction ID: {transaction_id}
                                    </p>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Show breakdown
                        with st.expander("💰 Revenue Breakdown", expanded=True):
                            st.markdown("""
                            <div style='background: white; padding: 1.5rem; border-radius: 12px; 
                                       box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                            """, unsafe_allow_html=True)
                            col_s1, col_s2 = st.columns(2)
                            with col_s1:
                                st.markdown(f"""
                                <div style='margin-bottom: 0.75rem;'>
                                    <span style='color: #4a5568;'>Base Price:</span>
                                    <span style='color: #1a1a2e; font-weight: 700; float: right;'>{format_currency(base_amount)}</span>
                                </div>
                                <div style='margin-bottom: 0.75rem;'>
                                    <span style='color: #4a5568;'>Cash Discount ({CONFIG.CASH_DISCOUNT_RATE*100}%):</span>
                                    <span style='color: #e53e3e; font-weight: 700; float: right;'>-{format_currency(cash_discount)}</span>
                                </div>
                                """, unsafe_allow_html=True)
                            with col_s2:
                                st.markdown(f"""
                                <div style='margin-bottom: 0.75rem;'>
                                    <span style='color: #4a5568;'>Labour Charge (₹{CONFIG.LABOUR_CHARGE_PER_QUINTAL}/Quintal):</span>
                                    <span style='color: #e53e3e; font-weight: 700; float: right;'>-{format_currency(labour_charge)}</span>
                                </div>
                                <div style='margin-bottom: 0.75rem;'>
                                    <span style='color: #4a5568;'>Transport Charge (₹{CONFIG.TRANSPORT_CHARGE_PER_QUINTAL}/Quintal):</span>
                                    <span style='color: #e53e3e; font-weight: 700; float: right;'>-{format_currency(transport_charge)}</span>
                                </div>
                                """, unsafe_allow_html=True)
                            st.markdown(f"""
                            <div style='border-top: 2px solid #48bb78; padding-top: 1rem; margin-top: 1rem;'>
                                <span style='color: #1a1a2e; font-weight: 700; font-size: 1.2rem;'>Total Revenue:</span>
                                <span style='color: #48bb78; font-weight: 700; font-size: 1.2rem; float: right;'>{format_currency(total_amount)}</span>
                            </div>
                            </div>
                            """, unsafe_allow_html=True)
                except ValueError as e:
                    display_error_message(f"Calculation error: {e}")
                except Exception as e:
                    display_error_message(f"An unexpected error occurred: {e}")
            else:
                st.markdown("""
                <div style='background: linear-gradient(135deg, #f5656515 0%, #e53e3e15 100%); 
                           padding: 1.5rem; border-radius: 12px; border-left: 4px solid #f56565;'>
                    <div style='display: flex; align-items: center;'>
                        <div style='font-size: 2rem; margin-right: 1rem;'>❌</div>
                        <div>
                            <h4 style='color: #c53030; margin: 0 0 0.25rem 0;'>
                                Validation Error
                            </h4>
                            <p style='color: #c53030; margin: 0;'>
                                Please fill all required fields with valid values
                            </p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

def render_view_transactions() -> None:
    """Render the view transactions page."""
    st.markdown("""
    <div style='background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%); 
                padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem;'>
        <h2 style='color: white; margin: 0; font-size: 1.8rem;'>
            📋 All Transactions
        </h2>
        <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;'>
            View, filter, and manage all your transactions
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        df = get_all_transactions()
        
        if not df.empty:
            # Filter options
            st.markdown("""
            <div style='background: white; padding: 1.5rem; border-radius: 12px; 
                       box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 1.5rem;'>
                <h3 style='color: #1a1a2e; margin-top: 0;'>🔍 Filter Transactions</h3>
            </div>
            """, unsafe_allow_html=True)
            
            col_filter1, col_filter2, col_filter3 = st.columns(3)
            
            with col_filter1:
                st.markdown("""
                <div style='margin-bottom: 0.5rem;'>
                    <label style='color: #1a1a2e; font-weight: 600;'>Filter by Type</label>
                </div>
                """, unsafe_allow_html=True)
                transaction_type_filter = st.selectbox(
                    "",
                    ["All", "BUY", "SELL"],
                    index=0,
                    label_visibility="collapsed"
                )
            
            with col_filter2:
                st.markdown("""
                <div style='margin-bottom: 0.5rem;'>
                    <label style='color: #1a1a2e; font-weight: 600;'>Filter by Status</label>
                </div>
                """, unsafe_allow_html=True)
                status_filter = st.selectbox(
                    "",
                    ["All", "PENDING", "SOLD", "COMPLETED"],
                    index=0,
                    label_visibility="collapsed"
                )
            
            with col_filter3:
                st.markdown("""
                <div style='margin-bottom: 0.5rem;'>
                    <label style='color: #1a1a2e; font-weight: 600;'>Search Item Name</label>
                </div>
                """, unsafe_allow_html=True)
                search_item = st.text_input(
                    "",
                    placeholder="Type to search...",
                    label_visibility="collapsed"
                )
            
            # Apply filters
            filtered_df = df.copy()
            
            if transaction_type_filter != "All":
                filtered_df = filtered_df[filtered_df['transaction_type'] == transaction_type_filter]
            
            if status_filter != "All":
                filtered_df = filtered_df[filtered_df['status'] == status_filter]
            
            if search_item:
                filtered_df = filtered_df[
                    filtered_df['item_name'].str.contains(search_item, case=False, na=False)
                ]
            
            # Display table
            display_columns = ['id', 'transaction_type', 'item_name', 'quantity_kg', 
                             'price_per_unit', 'total_amount', 'transaction_date', 'status']
            available_columns = [col for col in display_columns if col in filtered_df.columns]
            
            if not filtered_df.empty:
                st.markdown(f"""
                <div style='background: white; padding: 1.5rem; border-radius: 12px; 
                           box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 1.5rem;'>
                    <h3 style='color: #1a1a2e; margin-top: 0;'>📊 Transaction Results ({len(filtered_df)} records)</h3>
                </div>
                """, unsafe_allow_html=True)
                
                st.dataframe(
                    filtered_df[available_columns].rename(columns={'quantity_kg': 'Quantity (Quintal)'}),
                    use_container_width=True,
                    height=400
                )
                
                # Delete transaction section
                st.markdown("<hr style='margin: 2rem 0;'>", unsafe_allow_html=True)
                st.markdown("""
                <div style='background: linear-gradient(135deg, #f5656515 0%, #e53e3e15 100%); 
                           padding: 1.5rem; border-radius: 12px; border-left: 4px solid #f56565; margin-bottom: 1.5rem;'>
                    <h3 style='color: #1a1a2e; margin-top: 0;'>🗑️ Delete Transaction</h3>
                    <p style='color: #4a5568; margin: 0;'>
                        Select a transaction to permanently delete it from the database
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                col_del1, col_del2 = st.columns([3, 1])
                
                with col_del1:
                    trans_list = filtered_df.reset_index(drop=True)
                    selected_idx = st.selectbox(
                        "Select transaction to delete",
                        options=range(len(trans_list)),
                        format_func=lambda x: f"ID {int(trans_list.iloc[x]['id'])} - {trans_list.iloc[x]['item_name']} ({trans_list.iloc[x]['transaction_type']})"
                    )
                    trans_id_to_delete = int(trans_list.iloc[selected_idx]['id'])
                
                with col_del2:
                    st.write("")
                    st.write("")
                    if st.button("🗑️ Delete", use_container_width=True, key="open_delete_btn"):
                        st.session_state.show_delete_confirmation = True
                        st.session_state.transaction_to_delete = trans_id_to_delete
                
                # Show confirmation if needed
                if (st.session_state.show_delete_confirmation and 
                    st.session_state.transaction_to_delete == trans_id_to_delete):
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #ed893615 0%, #dd6b2015 100%); 
                               padding: 1.5rem; border-radius: 12px; border-left: 4px solid #ed8936; margin-bottom: 1.5rem;'>
                        <div style='display: flex; align-items: center;'>
                            <div style='font-size: 2rem; margin-right: 1rem;'>⚠️</div>
                            <div>
                                <h4 style='color: #c05621; margin: 0 0 0.25rem 0;'>
                                    Confirm Deletion
                                </h4>
                                <p style='color: #c05621; margin: 0;'>
                                    Are you sure you want to delete Transaction ID {trans_id_to_delete}? This action cannot be undone!
                                </p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col_confirm1, col_confirm2, col_confirm3 = st.columns(3)
                    
                    with col_confirm1:
                        if st.button("✅ Yes, Delete", use_container_width=True, key="confirm_delete_yes"):
                            if delete_transaction(trans_id_to_delete):
                                st.session_state.show_delete_confirmation = False
                                st.session_state.transaction_to_delete = None
                                st.markdown(f"""
                                <div style='background: linear-gradient(135deg, #48bb7815 0%, #38a16915 100%); 
                                           padding: 1.5rem; border-radius: 12px; border-left: 4px solid #48bb78;'>
                                    <div style='display: flex; align-items: center;'>
                                        <div style='font-size: 2rem; margin-right: 1rem;'>✅</div>
                                        <div>
                                            <h4 style='color: #065f46; margin: 0 0 0.25rem 0;'>
                                                Transaction Deleted Successfully!
                                            </h4>
                                            <p style='color: #065f46; margin: 0;'>
                                                Transaction ID {trans_id_to_delete} has been permanently removed
                                            </p>
                                        </div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                                st.balloons()
                                import time
                                time.sleep(1)
                                st.rerun()
                    
                    with col_confirm2:
                        if st.button("❌ Cancel", use_container_width=True, key="confirm_delete_no"):
                            st.session_state.show_delete_confirmation = False
                            st.session_state.transaction_to_delete = None
                            st.rerun()
                    
                    with col_confirm3:
                        st.write("")
            else:
                st.markdown("""
                <div style='background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); 
                           padding: 3rem; border-radius: 12px; text-align: center; border-left: 4px solid #667eea;'>
                    <div style='font-size: 4rem; margin-bottom: 1rem;'>🔍</div>
                    <h3 style='color: #1a1a2e; margin: 0 0 0.5rem 0;'>No Transactions Found</h3>
                    <p style='color: #4a5568; margin: 0;'>
                        Try adjusting your filters or search terms
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            # Summary of filtered transactions
            if not filtered_df.empty:
                st.markdown("<hr style='margin: 2rem 0;'>", unsafe_allow_html=True)
                st.markdown("""
                <div style='background: white; padding: 1.5rem; border-radius: 12px; 
                           box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 1.5rem;'>
                    <h3 style='color: #1a1a2e; margin-top: 0;'>📈 Summary</h3>
                </div>
                """, unsafe_allow_html=True)
                
                col_sum1, col_sum2, col_sum3 = st.columns(3)
                
                with col_sum1:
                    buy_total = filtered_df[filtered_df['transaction_type'] == 'BUY']['total_amount'].sum()
                    st.markdown(f"""
                    <div style='background: white; padding: 1.5rem; border-radius: 12px; 
                               box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center;'>
                        <div style='font-size: 2rem; font-weight: 700; color: #667eea; margin-bottom: 0.5rem;'>
                            {format_currency(buy_total)}
                        </div>
                        <div style='color: #4a5568; font-weight: 600; font-size: 0.9rem;'>
                            💰 Buy Total
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_sum2:
                    sell_total = filtered_df[filtered_df['transaction_type'] == 'SELL']['total_amount'].sum()
                    st.markdown(f"""
                    <div style='background: white; padding: 1.5rem; border-radius: 12px; 
                               box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center;'>
                        <div style='font-size: 2rem; font-weight: 700; color: #48bb78; margin-bottom: 0.5rem;'>
                            {format_currency(sell_total)}
                        </div>
                        <div style='color: #4a5568; font-weight: 600; font-size: 0.9rem;'>
                            💵 Sell Total
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_sum3:
                    net = sell_total - buy_total
                    net_color = "#48bb78" if net >= 0 else "#f56565"
                    st.markdown(f"""
                    <div style='background: white; padding: 1.5rem; border-radius: 12px; 
                               box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center;'>
                        <div style='font-size: 2rem; font-weight: 700; color: {net_color}; margin-bottom: 0.5rem;'>
                            {format_currency(net)}
                        </div>
                        <div style='color: #4a5568; font-weight: 600; font-size: 0.9rem;'>
                            📊 Net P/L
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Export option
                st.markdown("<hr style='margin: 2rem 0;'>", unsafe_allow_html=True)
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Transactions as CSV",
                    data=csv,
                    file_name=f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        else:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); 
                       padding: 3rem; border-radius: 12px; text-align: center; border-left: 4px solid #667eea;'>
                <div style='font-size: 4rem; margin-bottom: 1rem;'>📝</div>
                <h3 style='color: #1a1a2e; margin: 0 0 0.5rem 0;'>No Transactions Yet</h3>
                <p style='color: #4a5568; margin: 0;'>
                    Start by recording your first transaction to see them here
                </p>
            </div>
            """, unsafe_allow_html=True)
            
    except Exception as e:
        logger.error(f"Error rendering view transactions: {e}")
        display_error_message(f"Error loading transactions: {e}")

def render_pending_inventory() -> None:
    """Render the pending inventory page."""
    st.markdown("""
    <div style='background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%); 
                padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem;'>
        <h2 style='color: white; margin: 0; font-size: 1.8rem;'>
            📦 Pending Inventory
        </h2>
        <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;'>
            Items bought but not yet sold
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        pending_df = get_pending_transactions()
        
        if not pending_df.empty:
            st.markdown(f"""
            <div style='background: white; padding: 1.5rem; border-radius: 12px; 
                       box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 1.5rem;'>
                <h3 style='color: #1a1a2e; margin-top: 0;'>📊 Pending Items ({len(pending_df)})</h3>
            </div>
            """, unsafe_allow_html=True)
            
            display_columns = ['id', 'item_name', 'quantity_kg', 'price_per_unit', 
                             'total_amount', 'transaction_date']
            available_columns = [col for col in display_columns if col in pending_df.columns]
            
            st.dataframe(
                pending_df[available_columns].rename(columns={'quantity_kg': 'Quantity (Quintal)'}),
                use_container_width=True
            )
            
            st.markdown("<hr style='margin: 2rem 0;'>", unsafe_allow_html=True)
            st.markdown("""
            <div style='background: white; padding: 1.5rem; border-radius: 12px; 
                       box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 1.5rem;'>
                <h3 style='color: #1a1a2e; margin-top: 0;'>💰 Investment Summary</h3>
            </div>
            """, unsafe_allow_html=True)
            
            col_p1, col_p2 = st.columns(2)
            
            with col_p1:
                total_invested = pending_df['total_amount'].sum()
                st.markdown(f"""
                <div style='background: white; padding: 1.5rem; border-radius: 12px; 
                           box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center;'>
                    <div style='font-size: 2.5rem; font-weight: 700; color: #ed8936; margin-bottom: 0.5rem;'>
                        {format_currency(total_invested)}
                    </div>
                    <div style='color: #4a5568; font-weight: 600; font-size: 0.9rem;'>
                        💰 Total Invested
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_p2:
                st.markdown(f"""
                <div style='background: white; padding: 1.5rem; border-radius: 12px; 
                           box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center;'>
                    <div style='font-size: 2.5rem; font-weight: 700; color: #ed8936; margin-bottom: 0.5rem;'>
                        {len(pending_df)}
                    </div>
                    <div style='color: #4a5568; font-weight: 600; font-size: 0.9rem;'>
                        📦 Pending Items
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("""
            <div style='background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); 
                       padding: 1.5rem; border-radius: 12px; border-left: 4px solid #667eea; margin-top: 1.5rem;'>
                <div style='display: flex; align-items: center;'>
                    <div style='font-size: 2rem; margin-right: 1rem;'>💡</div>
                    <div>
                        <h4 style='color: #1a1a2e; margin: 0 0 0.25rem 0;'>
                            Pro Tip
                        </h4>
                        <p style='color: #4a5568; margin: 0;'>
                            Go to 'Record Selling' page and link these items when you sell them!
                        </p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #48bb7815 0%, #38a16915 100%); 
                       padding: 3rem; border-radius: 12px; text-align: center; border-left: 4px solid #48bb78;'>
                <div style='font-size: 4rem; margin-bottom: 1rem;'>✅</div>
                <h3 style='color: #065f46; margin: 0 0 0.5rem 0;'>No Pending Inventory!</h3>
                <p style='color: #065f46; margin: 0;'>
                    All purchases have been sold. Great job!
                </p>
            </div>
            """, unsafe_allow_html=True)
            
    except Exception as e:
        logger.error(f"Error rendering pending inventory: {e}")
        display_error_message(f"Error loading pending inventory: {e}")

def render_ledger() -> None:
    """Render the buyer/seller ledger page."""
    st.header("💼 Buyer/Seller Ledger")
    
    try:
        df = get_all_transactions()
        
        if not df.empty:
            # Tabs for Buyers and Sellers
            tab1, tab2 = st.tabs(["Buyers", "Sellers"])
            
            with tab1:
                render_buyer_ledger(df)
            
            with tab2:
                render_seller_ledger(df)
        else:
            display_info_message("No transactions recorded yet.")
            
    except Exception as e:
        logger.error(f"Error rendering ledger: {e}")
        display_error_message(f"Error loading ledger: {e}")

def render_buyer_ledger(df: pd.DataFrame) -> None:
    """Render the buyer ledger tab."""
    st.subheader("Buyer Payment Details")
    
    # Get all buyers (from BUY transactions)
    buyer_df = df[df['transaction_type'] == 'BUY'].copy()
    
    if not buyer_df.empty:
        # Group by buyer name
        buyers = buyer_df['buyer_name'].dropna().unique()
        buyers = [b for b in buyers if b and b != '']
        
        if buyers:
            buyer_ledger = []
            for buyer in buyers:
                buyer_trans = buyer_df[buyer_df['buyer_name'] == buyer]
                total_due = buyer_trans['total_amount'].sum()
                total_paid = buyer_trans['amount_paid'].sum()
                balance = total_due - total_paid
                num_transactions = len(buyer_trans)
                
                buyer_ledger.append({
                    'Buyer Name': buyer,
                    'Total Amount Due (₹)': format_currency(total_due),
                    'Amount Paid (₹)': format_currency(total_paid),
                    'Remaining Balance (₹)': format_currency(balance),
                    'Transactions': num_transactions,
                    'Status': '✅ Paid' if abs(balance) < 0.01 else '⏳ Pending'
                })
            
            buyer_ledger_df = pd.DataFrame(buyer_ledger)
            st.dataframe(buyer_ledger_df, use_container_width=True)
            
            # Summary
            st.divider()
            col_b1, col_b2, col_b3 = st.columns(3)
            
            with col_b1:
                total_due_all = buyer_df['total_amount'].sum()
                display_metric("Total Due from Buyers", format_currency(total_due_all))
            
            with col_b2:
                total_paid_all = buyer_df['amount_paid'].sum()
                display_metric("Total Paid by Buyers", format_currency(total_paid_all))
            
            with col_b3:
                balance_all = total_due_all - total_paid_all
                display_metric("Total Balance Due", format_currency(balance_all))
            
            # Update payment section
            st.divider()
            st.subheader("Update Buyer Payment")
            
            col_u1, col_u2, col_u3 = st.columns(3)
            
            with col_u1:
                selected_buyer = st.selectbox("Select Buyer", options=sorted(buyers))
            
            with col_u2:
                buyer_transactions = buyer_df[buyer_df['buyer_name'] == selected_buyer]
                trans_options = [
                    f"ID {row['id']} - {row['item_name']} ({row['quantity_kg']} Q)" 
                    for _, row in buyer_transactions.iterrows()
                ]
                selected_trans = st.selectbox("Select Transaction", options=trans_options)
            
            with col_u3:
                trans_id = int(selected_trans.split(" - ")[0].replace("ID ", ""))
                trans_total = buyer_transactions[buyer_transactions['id'] == trans_id]['total_amount'].values
                trans_total = float(trans_total[0]) if len(trans_total) > 0 else CONFIG.MAX_AMOUNT
                new_payment = st.number_input(
                    "Update Amount Paid (₹)",
                    min_value=0.0,
                    max_value=min(CONFIG.MAX_AMOUNT, trans_total),
                    step=100.0,
                    format="%.2f"
                )
            
            if st.button("Update Payment", key="buyer_payment"):
                if update_payment(trans_id, new_payment):
                    display_success_message("✅ Payment updated successfully!")
                    st.rerun()
        else:
            display_info_message("No buyer transactions found.")
    else:
        display_info_message("No buyer transactions found.")

def render_seller_ledger(df: pd.DataFrame) -> None:
    """Render the seller ledger tab."""
    st.subheader("Seller Payment Details")
    
    # Get all sellers (from SELL transactions)
    seller_df = df[df['transaction_type'] == 'SELL'].copy()
    
    # Filter out rows where seller_name is None or NaN
    seller_df = seller_df[seller_df['seller_name'].notna()]
    seller_df = seller_df[seller_df['seller_name'] != '']
    seller_df = seller_df[seller_df['seller_name'] != 'None']
    
    if not seller_df.empty:
        # Group by seller name
        sellers = seller_df['seller_name'].dropna().unique()
        sellers = [s for s in sellers if s and s != '' and s != 'None']
        
        if sellers:
            seller_ledger = []
            for seller in sellers:
                seller_trans = seller_df[seller_df['seller_name'] == seller]
                total_revenue = seller_trans['total_amount'].sum()
                total_received = seller_trans['amount_paid'].sum()
                balance = total_revenue - total_received
                num_transactions = len(seller_trans)
                
                seller_ledger.append({
                    'Seller Name': seller,
                    'Total Revenue (₹)': format_currency(total_revenue),
                    'Amount Received (₹)': format_currency(total_received),
                    'Remaining Balance (₹)': format_currency(balance),
                    'Transactions': num_transactions,
                    'Status': '✅ Paid' if abs(balance) < 0.01 else '⏳ Pending'
                })
            
            seller_ledger_df = pd.DataFrame(seller_ledger)
            
            if not seller_ledger_df.empty:
                st.dataframe(seller_ledger_df, use_container_width=True)
                
                # Summary
                st.divider()
                col_s1, col_s2, col_s3 = st.columns(3)
                
                with col_s1:
                    total_revenue_all = seller_df['total_amount'].sum()
                    display_metric("Total Revenue from Sales", format_currency(total_revenue_all))
                
                with col_s2:
                    total_received_all = seller_df['amount_paid'].sum()
                    display_metric("Total Amount Received", format_currency(total_received_all))
                
                with col_s3:
                    balance_all = total_revenue_all - total_received_all
                    display_metric("Total Balance Due", format_currency(balance_all))
                
                # Update payment section
                st.divider()
                st.subheader("Update Seller Payment")
                
                col_u1, col_u2, col_u3 = st.columns(3)
                
                with col_u1:
                    selected_seller = st.selectbox(
                        "Select Seller",
                        options=sorted(sellers),
                        key="select_seller_dropdown"
                    )
                
                with col_u2:
                    seller_transactions = seller_df[seller_df['seller_name'] == selected_seller]
                    trans_options = [
                        f"ID {int(row['id'])} - {row['item_name']} ({row['quantity_kg']} Q)" 
                        for _, row in seller_transactions.iterrows()
                    ]
                    if trans_options:
                        selected_trans = st.selectbox(
                            "Select Transaction",
                            options=trans_options,
                            key="seller_trans_select"
                        )
                    else:
                        display_info_message("No transactions for this seller")
                        selected_trans = None
                
                with col_u3:
                    if selected_trans:
                        trans_id = int(selected_trans.split(" - ")[0].replace("ID ", ""))
                        trans_total = seller_transactions[seller_transactions['id'] == trans_id]['total_amount'].values
                        trans_total = float(trans_total[0]) if len(trans_total) > 0 else CONFIG.MAX_AMOUNT
                        new_payment = st.number_input(
                            "Update Amount Received (₹)",
                            min_value=0.0,
                            max_value=min(CONFIG.MAX_AMOUNT, trans_total),
                            step=100.0,
                            format="%.2f",
                            key="seller_payment_input"
                        )
                        
                        if st.button("Update Payment", key="seller_payment"):
                            if update_payment(trans_id, new_payment):
                                display_success_message("✅ Payment updated successfully!")
                                st.rerun()
            else:
                display_info_message("No seller data available.")
        else:
            display_info_message("No seller transactions found.")
    else:
        display_info_message("No seller transactions found.")

def render_settings() -> None:
    """Render the settings page."""
    st.markdown("""
    <div style='background: linear-gradient(135deg, #718096 0%, #4a5568 100%); 
                padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem;'>
        <h2 style='color: white; margin: 0; font-size: 1.8rem;'>
            ⚙️ Settings
        </h2>
        <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;'>
            Configure and monitor your application
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background: white; padding: 1.5rem; border-radius: 12px; 
               box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 1.5rem;'>
        <h3 style='color: #1a1a2e; margin-top: 0;'>📋 Current Configuration</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Display current configuration
    config_data = {
        "Setting": [
            "Database Path",
            "Mandi Charge Rate",
            "Muddat Rate",
            "Cash Discount Rate",
            "Tractor Rent (per Quintal)",
            "Labour Charge (per Quintal)",
            "Transport Charge (per Quintal)",
            "Max Quantity (Quintal)",
            "Max Price per Unit (₹)",
            "Max Total Amount (₹)"
        ],
        "Value": [
            CONFIG.DB_PATH,
            f"{CONFIG.MANDI_CHARGE_RATE * 100}%",
            f"{CONFIG.MUDDAT_RATE * 100}%",
            f"{CONFIG.CASH_DISCOUNT_RATE * 100}%",
            f"₹{CONFIG.TRACTOR_RENT_PER_QUINTAL}",
            f"₹{CONFIG.LABOUR_CHARGE_PER_QUINTAL}",
            f"₹{CONFIG.TRANSPORT_CHARGE_PER_QUINTAL}",
            f"{CONFIG.MAX_QUANTITY}",
            f"₹{CONFIG.MAX_PRICE}",
            f"₹{CONFIG.MAX_AMOUNT}"
        ]
    }
    
    config_df = pd.DataFrame(config_data)
    st.dataframe(config_df, use_container_width=True)
    
    st.markdown("<hr style='margin: 2rem 0;'>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background: white; padding: 1.5rem; border-radius: 12px; 
               box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 1.5rem;'>
        <h3 style='color: #1a1a2e; margin-top: 0;'>💾 Database Information</h3>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        df = get_all_transactions()
        if not df.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""
                <div style='background: white; padding: 1.5rem; border-radius: 12px; 
                           box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center;'>
                    <div style='font-size: 2.5rem; font-weight: 700; color: #667eea; margin-bottom: 0.5rem;'>
                        {len(df)}
                    </div>
                    <div style='color: #4a5568; font-weight: 600; font-size: 0.9rem;'>
                        📊 Total Transactions
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                db_size = os.path.getsize(CONFIG.DB_PATH) / 1024
                st.markdown(f"""
                <div style='background: white; padding: 1.5rem; border-radius: 12px; 
                           box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center;'>
                    <div style='font-size: 2.5rem; font-weight: 700; color: #48bb78; margin-bottom: 0.5rem;'>
                        {db_size:.2f}
                    </div>
                    <div style='color: #4a5568; font-weight: 600; font-size: 0.9rem;'>
                        💾 Database Size (KB)
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                last_updated = st.session_state.get('last_refresh', 'N/A')
                st.markdown(f"""
                <div style='background: white; padding: 1.5rem; border-radius: 12px; 
                           box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center;'>
                    <div style='font-size: 1.5rem; font-weight: 700; color: #ed8936; margin-bottom: 0.5rem;'>
                        {last_updated}
                    </div>
                    <div style='color: #4a5568; font-weight: 600; font-size: 0.9rem;'>
                        🕐 Last Updated
                    </div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); 
                       padding: 1.5rem; border-radius: 12px; border-left: 4px solid #667eea;'>
                <div style='display: flex; align-items: center;'>
                    <div style='font-size: 2rem; margin-right: 1rem;'>ℹ️</div>
                    <div>
                        <h4 style='color: #1a1a2e; margin: 0 0 0.25rem 0;'>
                            No Transactions
                        </h4>
                        <p style='color: #4a5568; margin: 0;'>
                            Database is empty. Start by recording your first transaction.
                        </p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #f5656515 0%, #e53e3e15 100%); 
                   padding: 1.5rem; border-radius: 12px; border-left: 4px solid #f56565;'>
            <div style='display: flex; align-items: center;'>
                <div style='font-size: 2rem; margin-right: 1rem;'>❌</div>
                <div>
                    <h4 style='color: #c53030; margin: 0 0 0.25rem 0;'>
                        Error Reading Database
                    </h4>
                    <p style='color: #c53030; margin: 0;'>
                        {e}
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<hr style='margin: 2rem 0;'>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background: white; padding: 1.5rem; border-radius: 12px; 
               box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 1.5rem;'>
        <h3 style='color: #1a1a2e; margin-top: 0;'>📝 Application Logs</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Show recent log entries
    log_file = os.path.join("logs", f"app_{datetime.now().strftime('%Y%m%d')}.log")
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                log_lines = f.readlines()
                recent_logs = log_lines[-20:]  # Last 20 lines
                st.markdown("""
                <div style='background: #1a1a2e; padding: 1rem; border-radius: 8px; 
                           color: #a0aec0; font-family: monospace; font-size: 0.85rem;'>
                """, unsafe_allow_html=True)
                st.text_area("", value=''.join(recent_logs), height=200, label_visibility="collapsed")
                st.markdown("</div>", unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #f5656515 0%, #e53e3e15 100%); 
                       padding: 1.5rem; border-radius: 12px; border-left: 4px solid #f56565;'>
                <div style='display: flex; align-items: center;'>
                    <div style='font-size: 2rem; margin-right: 1rem;'>❌</div>
                    <div>
                        <h4 style='color: #c53030; margin: 0 0 0.25rem 0;'>
                            Error Reading Log File
                        </h4>
                        <p style='color: #c53030; margin: 0;'>
                            {e}
                        </p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); 
                   padding: 1.5rem; border-radius: 12px; border-left: 4px solid #667eea;'>
            <div style='display: flex; align-items: center;'>
                <div style='font-size: 2rem; margin-right: 1rem;'>ℹ️</div>
                <div>
                    <h4 style='color: #1a1a2e; margin: 0 0 0.25rem 0;'>
                        No Log File Found
                    </h4>
                    <p style='color: #4a5568; margin: 0;'>
                        No log file found for today. Logs will be created as you use the application.
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    main()
