"""
Calculation functions for the Buying & Selling Dashboard Application.
"""

from typing import Tuple

from config import CONFIG
from logger_setup import logger


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
