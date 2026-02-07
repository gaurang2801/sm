"""
Ledger page for the Buying & Selling Dashboard Application.
Shows buyer/seller payment status using BASE AMOUNT (price × quantity).
Extra charges are YOUR expenses, not buyer's/seller's.
"""

import pandas as pd
import streamlit as st

from config import CONFIG
from database import get_all_transactions
from transactions import update_payment
from utils import format_currency, display_info_message, display_error_message
from logger_setup import logger


def render_ledger() -> None:
    """Render the buyer/seller ledger page."""
    st.title("💰 Buyer/Seller Ledger")
    st.caption("Track payments & balances • Base amounts only (your expenses excluded)")
    
    try:
        df = get_all_transactions()
        
        if not df.empty:
            # Ensure base_amount column exists
            if 'base_amount' not in df.columns:
                df['base_amount'] = df['price_per_unit'] * df['quantity_kg']
            
            tab1, tab2, tab3 = st.tabs(["👤 Buyers (You Pay)", "🏪 Sellers (They Pay You)", "📊 Summary"])
            
            with tab1:
                render_buyer_ledger(df)
            
            with tab2:
                render_seller_ledger(df)
            
            with tab3:
                render_ledger_summary(df)
        else:
            st.info("📝 No transactions recorded yet. Add some transactions to see the ledger.")
            
    except Exception as e:
        logger.error(f"Error rendering ledger: {e}")
        display_error_message(f"Error loading ledger: {e}")


def render_buyer_ledger(df: pd.DataFrame) -> None:
    """Render the buyer ledger tab."""
    st.info("💡 **Note:** This shows BASE amount (Price × Quantity). Your expenses (Mandi, Tractor, Muddat) are NOT included.")
    
    buyer_df = df[df['transaction_type'] == 'BUY'].copy()
    
    if buyer_df.empty:
        st.warning("No buyer transactions found.")
        return
    
    # Calculate base_amount if needed
    if 'base_amount' not in buyer_df.columns:
        buyer_df['base_amount'] = buyer_df['price_per_unit'] * buyer_df['quantity_kg']
    
    buyers = buyer_df['buyer_name'].dropna().unique()
    buyers = [b for b in buyers if b and b != '']
    
    if not buyers:
        st.warning("No buyers found in transactions.")
        return
    
    # Create ledger summary
    buyer_ledger = []
    for buyer in buyers:
        buyer_trans = buyer_df[buyer_df['buyer_name'] == buyer]
        total_base = buyer_trans['base_amount'].sum()
        total_paid = buyer_trans['amount_paid'].sum()
        balance = total_base - total_paid
        
        buyer_ledger.append({
            'Buyer': buyer,
            'Base Amount': total_base,
            'Paid': total_paid,
            'Balance': balance,
            'Transactions': len(buyer_trans),
            'Status': '✅ Cleared' if balance <= 0.01 else '⏳ Pending'
        })
    
    ledger_df = pd.DataFrame(buyer_ledger)
    st.dataframe(
        ledger_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Base Amount": st.column_config.NumberColumn("Base Amount (₹)", format="₹%.2f"),
            "Paid": st.column_config.NumberColumn("Paid (₹)", format="₹%.2f"),
            "Balance": st.column_config.NumberColumn("Balance (₹)", format="₹%.2f"),
        }
    )
    
    # Summary metrics
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Base Amount", format_currency(buyer_df['base_amount'].sum()))
    with col2:
        st.metric("Total Paid", format_currency(buyer_df['amount_paid'].sum()))
    with col3:
        balance = buyer_df['base_amount'].sum() - buyer_df['amount_paid'].sum()
        st.metric("Balance Due", format_currency(balance))
    
    # Update payment section
    st.divider()
    st.subheader("💳 Update Payment")
    
    # Selectboxes outside form for dynamic behavior
    col1, col2 = st.columns(2)
    
    with col1:
        selected_buyer = st.selectbox("Select Buyer", options=sorted(buyers), key="buyer_select")
    
    with col2:
        buyer_transactions = buyer_df[buyer_df['buyer_name'] == selected_buyer]
        trans_options = {
            f"ID {int(row['id'])} - {row['item_name']} ({row['quantity_kg']:.1f} Q)": int(row['id'])
            for _, row in buyer_transactions.iterrows()
        }
        
        if not trans_options:
            st.warning("No transactions for this buyer")
            return
            
        selected_label = st.selectbox("Select Transaction", options=list(trans_options.keys()), key="buyer_trans_select")
        trans_id = trans_options[selected_label]
    
    # Get current values
    trans_row = buyer_transactions[buyer_transactions['id'] == trans_id].iloc[0]
    trans_base = float(trans_row['base_amount'])
    current_paid = float(trans_row['amount_paid'])
    
    st.info(f"**Base Amount:** {format_currency(trans_base)} | **Currently Paid:** {format_currency(current_paid)}")
    
    # Store trans_id in session state for form submission
    st.session_state['buyer_trans_id'] = trans_id
    st.session_state['buyer_trans_base'] = trans_base
    
    # Payment form with just the amount input and submit button
    with st.form("buyer_payment_form"):
        new_payment = st.number_input(
            "New Payment Amount (₹)", 
            min_value=0.0, 
            max_value=float(trans_base), 
            value=float(current_paid),
            step=100.0
        )
        
        submitted = st.form_submit_button("💾 Update Payment", use_container_width=True)
        
        if submitted:
            # Get trans_id from session state
            tid = st.session_state.get('buyer_trans_id')
            if tid and update_payment(tid, new_payment):
                st.success("✅ Payment updated successfully!")
                st.rerun()
            else:
                st.error("Failed to update payment.")


def render_seller_ledger(df: pd.DataFrame) -> None:
    """Render the seller ledger tab."""
    st.info("💡 **Note:** This shows BASE amount (Price × Quantity). Your deductions (Discount, Labour, Transport) are NOT included.")
    
    seller_df = df[df['transaction_type'] == 'SELL'].copy()
    seller_df = seller_df[seller_df['seller_name'].notna()]
    seller_df = seller_df[seller_df['seller_name'] != '']
    seller_df = seller_df[seller_df['seller_name'] != 'None']
    
    if seller_df.empty:
        st.warning("No seller transactions found.")
        return
    
    # Calculate base_amount if needed
    if 'base_amount' not in seller_df.columns:
        seller_df['base_amount'] = seller_df['price_per_unit'] * seller_df['quantity_kg']
    
    sellers = seller_df['seller_name'].dropna().unique()
    sellers = [s for s in sellers if s and s != '' and s != 'None']
    
    if not sellers:
        st.warning("No sellers found in transactions.")
        return
    
    # Create ledger summary
    seller_ledger = []
    for seller in sellers:
        seller_trans = seller_df[seller_df['seller_name'] == seller]
        total_base = seller_trans['base_amount'].sum()
        total_received = seller_trans['amount_paid'].sum()
        balance = total_base - total_received
        
        seller_ledger.append({
            'Seller': seller,
            'Base Amount': total_base,
            'Received': total_received,
            'Balance': balance,
            'Transactions': len(seller_trans),
            'Status': '✅ Cleared' if balance <= 0.01 else '⏳ Pending'
        })
    
    ledger_df = pd.DataFrame(seller_ledger)
    st.dataframe(
        ledger_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Base Amount": st.column_config.NumberColumn("Base Amount (₹)", format="₹%.2f"),
            "Received": st.column_config.NumberColumn("Received (₹)", format="₹%.2f"),
            "Balance": st.column_config.NumberColumn("Balance (₹)", format="₹%.2f"),
        }
    )
    
    # Summary metrics
    st.divider()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Base Amount", format_currency(seller_df['base_amount'].sum()))
    with col2:
        st.metric("Total Received", format_currency(seller_df['amount_paid'].sum()))
    with col3:
        balance = seller_df['base_amount'].sum() - seller_df['amount_paid'].sum()
        st.metric("Balance Receivable", format_currency(balance))
    
    # Update payment section
    st.divider()
    st.subheader("💳 Update Payment Received")
    
    # Selectboxes outside form for dynamic behavior
    col1, col2 = st.columns(2)
    
    with col1:
        selected_seller = st.selectbox("Select Seller", options=sorted(sellers), key="seller_select")
    
    with col2:
        seller_transactions = seller_df[seller_df['seller_name'] == selected_seller]
        trans_options = {
            f"ID {int(row['id'])} - {row['item_name']} ({row['quantity_kg']:.1f} Q)": int(row['id'])
            for _, row in seller_transactions.iterrows()
        }
        
        if not trans_options:
            st.warning("No transactions for this seller")
            return
            
        selected_label = st.selectbox("Select Transaction", options=list(trans_options.keys()), key="seller_trans_select")
        trans_id = trans_options[selected_label]
    
    # Get current values
    trans_row = seller_transactions[seller_transactions['id'] == trans_id].iloc[0]
    trans_base = float(trans_row['base_amount'])
    current_received = float(trans_row['amount_paid'])
    
    st.info(f"**Base Amount:** {format_currency(trans_base)} | **Currently Received:** {format_currency(current_received)}")
    
    # Store trans_id in session state for form submission
    st.session_state['seller_trans_id'] = trans_id
    st.session_state['seller_trans_base'] = trans_base
    
    # Payment form with just the amount input and submit button
    with st.form("seller_payment_form"):
        new_payment = st.number_input(
            "New Received Amount (₹)", 
            min_value=0.0, 
            max_value=float(trans_base), 
            value=float(current_received),
            step=100.0
        )
        
        submitted = st.form_submit_button("💾 Update Payment", use_container_width=True)
        
        if submitted:
            # Get trans_id from session state
            tid = st.session_state.get('seller_trans_id')
            if tid and update_payment(tid, new_payment):
                st.success("✅ Payment updated successfully!")
                st.rerun()
            else:
                st.error("Failed to update payment.")


def render_ledger_summary(df: pd.DataFrame) -> None:
    """Render overall ledger summary with expenses breakdown."""
    st.subheader("📊 Overall Summary")
    
    # Calculate base amounts
    if 'base_amount' not in df.columns:
        df['base_amount'] = df['price_per_unit'] * df['quantity_kg']
    
    buy_df = df[df['transaction_type'] == 'BUY']
    sell_df = df[df['transaction_type'] == 'SELL']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📥 Buying Summary")
        if not buy_df.empty:
            total_base = buy_df['base_amount'].sum()
            total_expenses = buy_df['mandi_charge'].sum() + buy_df['tractor_rent'].sum() + buy_df['muddat'].sum()
            
            st.metric("Base Amount (to buyers)", format_currency(total_base))
            st.metric("Your Expenses", format_currency(total_expenses), help="Mandi + Tractor + Muddat")
            st.metric("Total Cost", format_currency(total_base + total_expenses))
        else:
            st.info("No buying transactions")
    
    with col2:
        st.markdown("### 📤 Selling Summary")
        if not sell_df.empty:
            total_base = sell_df['base_amount'].sum()
            total_deductions = sell_df['cash_discount'].sum() + sell_df['labour_charge'].sum() + sell_df['transport_charge'].sum()
            
            st.metric("Base Amount (from sellers)", format_currency(total_base))
            st.metric("Your Deductions", format_currency(total_deductions), help="Discount + Labour + Transport")
            st.metric("Net Receivable", format_currency(total_base - total_deductions))
        else:
            st.info("No selling transactions")
    
    # Total expenses
    st.divider()
    st.subheader("💸 Your Total Expenses")
    st.caption("These are YOUR costs, not charged to buyers/sellers")
    
    col1, col2, col3 = st.columns(3)
    
    if not buy_df.empty:
        buy_expenses = buy_df['mandi_charge'].sum() + buy_df['tractor_rent'].sum() + buy_df['muddat'].sum()
    else:
        buy_expenses = 0
    
    if not sell_df.empty:
        sell_deductions = sell_df['cash_discount'].sum() + sell_df['labour_charge'].sum() + sell_df['transport_charge'].sum()
    else:
        sell_deductions = 0
    
    with col1:
        st.metric("Buying Expenses", format_currency(buy_expenses))
    with col2:
        st.metric("Selling Deductions", format_currency(sell_deductions))
    with col3:
        st.metric("Total Your Expenses", format_currency(buy_expenses + sell_deductions))
