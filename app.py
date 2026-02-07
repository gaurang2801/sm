"""
Buying & Selling Dashboard Application
A professional Streamlit application for managing buying and selling transactions.
"""

import streamlit as st
from datetime import datetime

from config import CONFIG
from database import init_database
from styles import inject_custom_css
from logger_setup import logger
from views import (
    render_dashboard,
    render_record_buying,
    render_record_selling,
    render_view_transactions,
    render_pending_inventory,
    render_ledger,
    render_settings,
    render_parties
)


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
        if 'show_delete_confirmation' not in st.session_state:
            st.session_state.show_delete_confirmation = False
        if 'transaction_to_delete' not in st.session_state:
            st.session_state.transaction_to_delete = None
        if 'last_refresh' not in st.session_state:
            st.session_state.last_refresh = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Sidebar navigation
        with st.sidebar:
            st.markdown("## 📊 Dashboard")
            st.markdown("---")
            
            page = st.radio(
                "Navigate",
                [
                    "🏠 Dashboard",
                    "👥 Contacts",
                    "📥 Record Buying",
                    "📤 Record Selling",
                    "📋 All Transactions",
                    "📦 Pending Inventory",
                    "💰 Ledger",
                    "⚙️ Settings"
                ],
                label_visibility="collapsed"
            )
            
            st.markdown("---")
            st.caption(f"Last updated: {st.session_state.last_refresh}")
        
        # Clean page name
        page_name = page.split(" ", 1)[1] if " " in page else page
        
        # Route to appropriate page
        if page_name == "Dashboard":
            render_dashboard()
        elif page_name == "Contacts":
            render_parties()
        elif page_name == "Record Buying":
            render_record_buying()
        elif page_name == "Record Selling":
            render_record_selling()
        elif page_name == "All Transactions":
            render_view_transactions()
        elif page_name == "Pending Inventory":
            render_pending_inventory()
        elif page_name == "Ledger":
            render_ledger()
        elif page_name == "Settings":
            render_settings()
            
    except Exception as e:
        logger.error(f"Application error: {e}")
        st.error(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
