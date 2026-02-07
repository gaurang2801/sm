"""
Transaction operations for the Buying & Selling Dashboard Application.
"""

import sqlite3
import pandas as pd
from datetime import datetime
from typing import Optional
import streamlit as st

from config import CONFIG
from database import get_db_connection, get_transaction_by_id
from validators import (
    validate_name, validate_item_name, validate_numeric_value, 
    validate_notes, sanitize_string
)
from logger_setup import logger


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

        # Fetch transaction to validate
        transaction_df = get_transaction_by_id(transaction_id)
        if transaction_df.empty:
            st.error("Transaction not found")
            return False
        
        row = transaction_df.iloc[0]
        
        # Calculate base_amount for validation (price × quantity)
        # We use base_amount because ledger tracks base amounts, not total with expenses
        price = pd.to_numeric(row.get("price_per_unit", 0), errors="coerce")
        qty = pd.to_numeric(row.get("quantity_kg", 0), errors="coerce")
        
        if pd.isna(price) or pd.isna(qty):
            # Fallback to total_amount if base values are missing
            max_amount = pd.to_numeric(row.get("total_amount", 0), errors="coerce")
        else:
            max_amount = price * qty
        
        if pd.isna(max_amount):
            st.error("Invalid amount for this transaction")
            return False
        
        # Validate that amount_paid does not exceed max_amount
        if amount_paid > max_amount:
            st.error(f"Amount paid (₹{amount_paid:.2f}) cannot exceed base amount (₹{max_amount:.2f})")
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
                st.error("Transaction not found")
                return False
                
    except sqlite3.Error as e:
        logger.error(f"Error updating payment for transaction {transaction_id}: {e}")
        st.error(f"Database error: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error updating payment: {e}")
        st.error(f"An unexpected error occurred: {e}")
        return False
