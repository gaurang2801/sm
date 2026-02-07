"""
Settings page for the Buying & Selling Dashboard Application.
"""

import os
from datetime import datetime
import streamlit as st
import pandas as pd

from config import CONFIG
from database import get_all_transactions
from utils import display_error_message
from logger_setup import logger


def render_settings() -> None:
    """Render the settings page."""
    st.markdown("""
    <div style='background: linear-gradient(135deg, #718096 0%, #4a5568 100%); 
                padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem;'>
        <h2 style='color: white; margin: 0; font-size: 1.8rem;'>⚙️ Settings</h2>
        <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;'>Configure and monitor your application</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 📋 Current Configuration")
    
    config_data = {
        "Setting": [
            "Database Path", "Mandi Charge Rate", "Muddat Rate", "Cash Discount Rate",
            "Tractor Rent (per Quintal)", "Labour Charge (per Quintal)", "Transport Charge (per Quintal)",
            "Max Quantity (Quintal)", "Max Price per Unit (₹)", "Max Total Amount (₹)"
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
    
    st.dataframe(pd.DataFrame(config_data), use_container_width=True)
    
    st.divider()
    st.markdown("### 💾 Database Information")
    
    try:
        df = get_all_transactions()
        if not df.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Total Transactions", len(df))
            with col2:
                db_size = os.path.getsize(CONFIG.DB_PATH) / 1024
                st.metric("💾 Database Size (KB)", f"{db_size:.2f}")
            with col3:
                last_updated = st.session_state.get('last_refresh', 'N/A')
                st.metric("🕐 Last Updated", last_updated)
        else:
            st.info("Database is empty. Start by recording your first transaction.")
    except Exception as e:
        display_error_message(f"Error reading database: {e}")
    
    st.divider()
    st.markdown("### 📝 Application Logs")
    
    log_file = os.path.join("logs", f"app_{datetime.now().strftime('%Y%m%d')}.log")
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                log_lines = f.readlines()
                recent_logs = log_lines[-20:]
                st.text_area("Recent Logs", value=''.join(recent_logs), height=200, disabled=True)
        except Exception as e:
            display_error_message(f"Error reading log file: {e}")
    else:
        st.info("No log file found for today. Logs will be created as you use the application.")
