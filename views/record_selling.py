"""
Record Selling page for the Buying & Selling Dashboard Application.
"""

import streamlit as st

from config import CONFIG
from database import get_pending_transactions, get_all_parties, add_party
from calculations import calculate_selling_price
from transactions import add_selling_transaction
from utils import format_currency, display_error_message


def render_record_selling() -> None:
    """Render the record selling transaction page."""
    st.markdown("""
    <div style='background: linear-gradient(135deg, #48bb78 0%, #38a169 100%); 
                padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem;'>
        <h2 style='color: white; margin: 0; font-size: 1.8rem;'>
            📤 Record Selling Transaction
        </h2>
        <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;'>
            Record sales and link them to your inventory
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Option to link with pending buying transaction
    pending_df = get_pending_transactions()
    link_purchase = None
    
    if not pending_df.empty:
        st.subheader("🔗 Link with Previous Purchase (Optional)")
        purchase_options = {
            f"ID {row['id']} - {row['item_name']} ({row['quantity_kg']} Quintal)": row['id']
            for _, row in pending_df.iterrows()
        }
        selected_purchase = st.selectbox(
            "Select pending purchase",
            options=[None] + list(purchase_options.keys()),
            format_func=lambda x: "No specific purchase" if x is None else x
        )
        if selected_purchase:
            link_purchase = purchase_options[selected_purchase]
    else:
        st.info("ℹ️ No pending purchases to link. You can still record a selling transaction.")
    
    st.markdown("---")
    
    # Get existing parties for dropdown
    parties_df = get_all_parties("SELLER")
    party_options = ["➕ Add New Seller..."]
    if not parties_df.empty:
        party_options += [f"{row['id']} - {row['name']} ({row.get('phone', '') or 'No phone'})" 
                         for _, row in parties_df.iterrows()]
    
    # Party selection outside form for dynamic updates
    selected_party = st.selectbox("Select Seller *", party_options, key="sell_party_select")
    
    # If adding new seller, show inline form
    seller_name = ""
    party_id = None
    new_seller_phone = ""
    
    if selected_party == "➕ Add New Seller...":
        col_new1, col_new2 = st.columns(2)
        with col_new1:
            seller_name = st.text_input("New Seller Name *", placeholder="e.g., Market Name", key="new_seller_name")
        with col_new2:
            new_seller_phone = st.text_input("Phone (optional)", placeholder="e.g., 9876543210", key="new_seller_phone")
    else:
        party_id = int(selected_party.split(" - ")[0])
        seller_name = selected_party.split(" - ")[1].split(" (")[0]
    
    with st.form("selling_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            item_name = st.text_input(
                "Item Name *",
                placeholder="e.g., Rice, Wheat",
                max_chars=CONFIG.MAX_ITEM_NAME_LENGTH
            )
        
        with col2:
            quantity_quintal = st.number_input(
                "Quantity (Quintal) *",
                min_value=CONFIG.MIN_QUANTITY,
                max_value=CONFIG.MAX_QUANTITY,
                value=1.0,
                step=0.5,
                format="%.2f"
            )
            
            price_per_unit = st.number_input(
                "Selling Price per Quintal (₹) *",
                min_value=CONFIG.MIN_PRICE,
                max_value=CONFIG.MAX_PRICE,
                value=1200.0,
                step=100.0,
                format="%.2f"
            )
        
        with col3:
            amount_paid = st.number_input(
                "Amount Received (₹)",
                min_value=0.0,
                max_value=CONFIG.MAX_AMOUNT,
                value=0.0,
                step=100.0,
                format="%.2f"
            )
            
            notes = st.text_area(
                "Notes (Optional)",
                placeholder="Any additional notes",
                max_chars=CONFIG.MAX_NOTES_LENGTH
            )
        
        submitted = st.form_submit_button("📝 Record Selling Transaction", use_container_width=True)
        
        if submitted:
            if seller_name and item_name and quantity_quintal > 0 and price_per_unit > 0:
                try:
                    # If new seller, create party first
                    if selected_party == "➕ Add New Seller...":
                        party_id = add_party(
                            name=seller_name.strip(),
                            phone=new_seller_phone.strip() if new_seller_phone else "",
                            party_type="SELLER"
                        )
                        if not party_id:
                            st.error("Failed to add new seller")
                            return
                    
                    base_amount = price_per_unit * quantity_quintal
                    total_amount, cash_discount, labour_charge, transport_charge = calculate_selling_price(
                        base_amount, quantity_quintal
                    )
                    
                    # Add to database
                    transaction_id = add_selling_transaction(
                        seller_name, item_name, quantity_quintal, price_per_unit,
                        cash_discount, labour_charge, transport_charge,
                        total_amount, amount_paid, link_purchase, notes
                    )
                    
                    if transaction_id:
                        st.success(f"✅ Selling Transaction Recorded! ID: {transaction_id}")
                        
                        # Show breakdown
                        with st.expander("💰 Revenue Breakdown", expanded=True):
                            col_s1, col_s2 = st.columns(2)
                            with col_s1:
                                st.write(f"**Base Price:** {format_currency(base_amount)}")
                                st.write(f"**Cash Discount ({CONFIG.CASH_DISCOUNT_RATE*100}%):** -{format_currency(cash_discount)}")
                            with col_s2:
                                st.write(f"**Labour (₹{CONFIG.LABOUR_CHARGE_PER_QUINTAL}/Q):** -{format_currency(labour_charge)}")
                                st.write(f"**Transport (₹{CONFIG.TRANSPORT_CHARGE_PER_QUINTAL}/Q):** -{format_currency(transport_charge)}")
                            st.markdown(f"### Total Revenue: {format_currency(total_amount)}")
                except ValueError as e:
                    display_error_message(f"Calculation error: {e}")
                except Exception as e:
                    display_error_message(f"An unexpected error occurred: {e}")
            else:
                st.error("❌ Please fill all required fields with valid values")
