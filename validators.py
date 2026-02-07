"""
Input validation functions for the Buying & Selling Dashboard Application.
"""

import re
from typing import Optional, Tuple
import pandas as pd

from config import CONFIG


# Validation patterns
NAME_ALLOWED_PATTERN = re.compile(r"^[\w .,'\&/()-]+$", re.UNICODE)
ITEM_ALLOWED_PATTERN = re.compile(r"^[\w .,'\&/()-+%]+$", re.UNICODE)


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
    
    Args:
        value: The text value to validate
        field_name: Name of the field for error messages
        max_length: Maximum allowed length
        pattern: Optional regex pattern to match
        
    Returns:
        Tuple of (is_valid, error_message)
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
