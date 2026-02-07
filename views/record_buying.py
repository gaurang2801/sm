"""
Record Buying page for the Buying & Selling Dashboard Application.
"""

import streamlit as st

from config import CONFIG
from calculations import calculate_buying_price
from transactions import add_buying_transaction
from database import get_all_parties, add_party
from utils import format_currency, display_error_message


def render_record_buying() -> None:
    """Render the record buying transaction page."""
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem;'>
        <h2 style='color: white; margin: 0; font-size: 1.8rem;'>
            📥 Record Buying Transaction
        </h2>
        <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;'>
            Add new purchase transactions to your inventory
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get existing parties for dropdown
    parties_df = get_all_parties("BUYER")
    party_options = ["➕ Add New Buyer..."]
    if not parties_df.empty:
        party_options += [f"{row['id']} - {row['name']} ({row.get('phone', '') or 'No phone'})" 
                         for _, row in parties_df.iterrows()]
    
    # Party selection outside form for dynamic updates
    selected_party = st.selectbox("Select Buyer *", party_options, key="buy_party_select")
    
    # If adding new buyer, show inline form
    buyer_name = ""
    party_id = None
    new_buyer_phone = ""
    
    if selected_party == "➕ Add New Buyer...":
        col_new1, col_new2 = st.columns(2)
        with col_new1:
            buyer_name = st.text_input("New Buyer Name *", placeholder="e.g., Amit Kumar", key="new_buyer_name")
        with col_new2:
            new_buyer_phone = st.text_input("Phone (optional)", placeholder="e.g., 9876543210", key="new_buyer_phone")
    else:
        party_id = int(selected_party.split(" - ")[0])
        buyer_name = selected_party.split(" - ")[1].split(" (")[0]
    
    with st.form("buying_form"):
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
                "Price per Quintal (₹) *",
                min_value=CONFIG.MIN_PRICE,
                max_value=CONFIG.MAX_PRICE,
                value=1000.0,
                step=100.0,
                format="%.2f"
            )
        
        with col3:
            amount_paid = st.number_input(
                "Amount Paid (₹)",
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
        
        submitted = st.form_submit_button("📝 Record Buying Transaction", use_container_width=True)
        
        if submitted:
            if buyer_name and item_name and quantity_quintal > 0 and price_per_unit > 0:
                try:
                    # If new buyer, create party first
                    if selected_party == "➕ Add New Buyer...":
                        party_id = add_party(
                            name=buyer_name.strip(),
                            phone=new_buyer_phone.strip() if new_buyer_phone else "",
                            party_type="BUYER"
                        )
                        if not party_id:
                            st.error("Failed to add new buyer")
                            return
                    
                    base_amount = price_per_unit * quantity_quintal
                    total_amount, mandi_charge, tractor_rent, muddat = calculate_buying_price(
                        base_amount, quantity_quintal
                    )
                    
                    # Add to database
                    transaction_id = add_buying_transaction(
                        buyer_name, item_name, quantity_quintal, price_per_unit,
                        mandi_charge, tractor_rent, muddat,
                        total_amount, amount_paid, notes
                    )
                    
                    if transaction_id:
                        st.success(f"✅ Buying Transaction Recorded! ID: {transaction_id}")
                        
                        # Show breakdown
                        with st.expander("💰 Cost Breakdown", expanded=True):
                            col_b1, col_b2 = st.columns(2)
                            with col_b1:
                                st.write(f"**Base Price:** {format_currency(base_amount)}")
                                st.write(f"**Mandi Charge ({CONFIG.MANDI_CHARGE_RATE*100}%):** {format_currency(mandi_charge)}")
                            with col_b2:
                                st.write(f"**Tractor Rent (₹{CONFIG.TRACTOR_RENT_PER_QUINTAL}/Q):** {format_currency(tractor_rent)}")
                                st.write(f"**Muddat ({CONFIG.MUDDAT_RATE*100}%):** {format_currency(muddat)}")
                            st.markdown(f"### Total: {format_currency(total_amount)}")
                except ValueError as e:
                    display_error_message(f"Calculation error: {e}")
                except Exception as e:
                    display_error_message(f"An unexpected error occurred: {e}")
            else:
                st.error("❌ Please fill all required fields with valid values")
