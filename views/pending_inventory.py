"""
Pending Inventory page for the Buying & Selling Dashboard Application.
"""

import streamlit as st

from database import get_pending_transactions
from utils import format_currency, display_error_message
from logger_setup import logger


def render_pending_inventory() -> None:
    """Render the pending inventory page."""
    st.markdown("""
    <div style='background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%); 
                padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem;'>
        <h2 style='color: white; margin: 0; font-size: 1.8rem;'>📦 Pending Inventory</h2>
        <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;'>Items bought but not yet sold</p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        pending_df = get_pending_transactions()
        
        if not pending_df.empty:
            st.markdown(f"### 📊 Pending Items ({len(pending_df)})")
            
            display_columns = ['id', 'item_name', 'quantity_kg', 'price_per_unit', 
                             'total_amount', 'transaction_date']
            available_columns = [col for col in display_columns if col in pending_df.columns]
            
            st.dataframe(
                pending_df[available_columns].rename(columns={'quantity_kg': 'Quantity (Quintal)'}),
                use_container_width=True
            )
            
            st.divider()
            st.markdown("### 💰 Investment Summary")
            
            col_p1, col_p2 = st.columns(2)
            
            with col_p1:
                total_invested = pending_df['total_amount'].sum()
                st.metric("Total Invested", format_currency(total_invested))
            
            with col_p2:
                st.metric("Pending Items", len(pending_df))
            
            st.info("💡 **Pro Tip**: Go to 'Record Selling' page and link these items when you sell them!")
        else:
            st.success("✅ **No Pending Inventory!** All purchases have been sold. Great job!")
            
    except Exception as e:
        logger.error(f"Error rendering pending inventory: {e}")
        display_error_message(f"Error loading pending inventory: {e}")
