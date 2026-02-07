"""
Dashboard page for the Buying & Selling Dashboard Application.
"""

import streamlit as st
import pandas as pd

from database import get_all_transactions
from utils import format_currency, get_transaction_summary, display_error_message
from logger_setup import logger


def render_dashboard() -> None:
    """Render the dashboard page."""
    st.title("📊 Dashboard")
    st.caption("Monitor your business performance at a glance")
    
    try:
        df = get_all_transactions()
        
        if not df.empty:
            summary = get_transaction_summary(df)
            
            # Key Metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="💰 Total Buying",
                    value=format_currency(summary['total_buy'])
                )
            
            with col2:
                st.metric(
                    label="💵 Total Selling",
                    value=format_currency(summary['total_sell'])
                )
            
            with col3:
                delta_color = "normal" if summary['profit_loss'] >= 0 else "inverse"
                st.metric(
                    label="📈 Profit/Loss",
                    value=format_currency(summary['profit_loss']),
                    delta=f"{'Profit' if summary['profit_loss'] >= 0 else 'Loss'}",
                    delta_color=delta_color
                )
            
            with col4:
                st.metric(
                    label="📦 Pending Items",
                    value=summary['pending_count']
                )
            
            st.divider()
            
            # Charts
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                st.subheader("Transaction Types")
                transaction_counts = df['transaction_type'].value_counts()
                if not transaction_counts.empty:
                    st.bar_chart(transaction_counts, color="#3b82f6")
            
            with col_chart2:
                st.subheader("Status Distribution")
                status_counts = df['status'].value_counts()
                if not status_counts.empty:
                    st.bar_chart(status_counts, color="#10b981")
            
            st.divider()
            
            # Recent Transactions
            st.subheader("🕐 Recent Transactions")
            
            recent_df = df.head(10).copy()
            display_columns = ['id', 'transaction_type', 'item_name', 'quantity_kg', 
                             'total_amount', 'transaction_date', 'status']
            available_columns = [col for col in display_columns if col in recent_df.columns]
            
            st.dataframe(
                recent_df[available_columns],
                use_container_width=True,
                hide_index=True,
                column_config={
                    "id": "ID",
                    "transaction_type": "Type",
                    "item_name": "Item",
                    "quantity_kg": st.column_config.NumberColumn("Qty (Q)", format="%.2f"),
                    "total_amount": st.column_config.NumberColumn("Amount (₹)", format="₹%.2f"),
                    "transaction_date": "Date",
                    "status": "Status"
                }
            )
            
        else:
            st.info("📝 **No transactions yet!** Start by recording your first transaction.")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("""
                ### Getting Started
                1. Go to **Record Buying** to add purchase transactions
                2. Go to **Record Selling** to add sales
                3. View your analytics here on the Dashboard
                """)
            
    except Exception as e:
        logger.error(f"Error rendering dashboard: {e}")
        display_error_message(f"Error loading dashboard: {e}")
