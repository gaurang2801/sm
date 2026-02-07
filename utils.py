"""
Utility functions for the Buying & Selling Dashboard Application.
"""

from typing import Dict, Any
import pandas as pd
import streamlit as st

from logger_setup import logger


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

def display_metric(label: str, value: str, delta: str = None) -> None:
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
