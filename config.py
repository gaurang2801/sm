"""
Configuration settings for the Buying & Selling Dashboard Application.
"""

from dataclasses import dataclass


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


# Initialize global configuration
CONFIG = AppConfig()
