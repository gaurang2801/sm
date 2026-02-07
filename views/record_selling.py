"""
Record Selling page for the Buying & Selling Dashboard Application.
"""

import streamlit as st

from config import CONFIG
from database import get_pending_transactions
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
    st.markdown("""
    <div style='background: white; padding: 1.5rem; border-radius: 12px; 
               box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 1.5rem;'>
        <h3 style='color: #1a1a2e; margin-top: 0;'>🔗 Link with Previous Purchase (Optional)</h3>
    </div>
    """, unsafe_allow_html=True)
    
    pending_df = get_pending_transactions()
    
    link_purchase = None
    if not pending_df.empty:
        st.markdown("""
        <div style='background: #f7fafc; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;'>
            <p style='color: #4a5568; margin: 0;'>Select a pending purchase to link:</p>
        </div>
        """, unsafe_allow_html=True)
        purchase_options = {
            f"ID {row['id']} - {row['item_name']} ({row['quantity_kg']} Quintal)": row['id']
            for _, row in pending_df.iterrows()
        }
        
        selected_purchase = st.selectbox(
            "",
            options=[None] + list(purchase_options.keys()),
            format_func=lambda x: "No specific purchase" if x is None else x,
            label_visibility="collapsed"
        )
        
        if selected_purchase:
            link_purchase = purchase_options[selected_purchase]
    else:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); 
                   padding: 1.5rem; border-radius: 12px; border-left: 4px solid #667eea;'>
            <div style='display: flex; align-items: center;'>
                <div style='font-size: 2rem; margin-right: 1rem;'>ℹ️</div>
                <div>
                    <h4 style='color: #1a1a2e; margin: 0 0 0.25rem 0;'>
                        No Pending Purchases
                    </h4>
                    <p style='color: #4a5568; margin: 0;'>
                        You can still record a new selling transaction without linking.
                    </p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<hr style='margin: 2rem 0;'>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style='background: white; padding: 2rem; border-radius: 12px; 
               box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 2rem;'>
        <h3 style='color: #1a1a2e; margin-top: 0;'>Transaction Details</h3>
        <p style='color: #4a5568; margin-bottom: 1.5rem;'>
            Fill in the details below to record a new selling transaction
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("selling_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div style='margin-bottom: 0.5rem;'>
                <label style='color: #1a1a2e; font-weight: 600;'>Seller Name *</label>
            </div>
            """, unsafe_allow_html=True)
            seller_name = st.text_input(
                "",
                placeholder="e.g., Market/Buyer Name",
                max_chars=CONFIG.MAX_NAME_LENGTH,
                label_visibility="collapsed"
            )
            
            st.markdown("""
            <div style='margin-bottom: 0.5rem; margin-top: 1rem;'>
                <label style='color: #1a1a2e; font-weight: 600;'>Item Name *</label>
            </div>
            """, unsafe_allow_html=True)
            item_name = st.text_input(
                "",
                placeholder="e.g., Rice, Wheat",
                max_chars=CONFIG.MAX_ITEM_NAME_LENGTH,
                label_visibility="collapsed"
            )
        
        with col2:
            st.markdown("""
            <div style='margin-bottom: 0.5rem;'>
                <label style='color: #1a1a2e; font-weight: 600;'>Quantity (Quintal) *</label>
            </div>
            """, unsafe_allow_html=True)
            quantity_quintal = st.number_input(
                "",
                min_value=CONFIG.MIN_QUANTITY,
                max_value=CONFIG.MAX_QUANTITY,
                value=1.0,
                step=0.5,
                format="%.2f",
                label_visibility="collapsed"
            )
            
            st.markdown("""
            <div style='margin-bottom: 0.5rem; margin-top: 1rem;'>
                <label style='color: #1a1a2e; font-weight: 600;'>Selling Price per Quintal (₹) *</label>
            </div>
            """, unsafe_allow_html=True)
            price_per_unit = st.number_input(
                "",
                min_value=CONFIG.MIN_PRICE,
                max_value=CONFIG.MAX_PRICE,
                value=1200.0,
                step=100.0,
                format="%.2f",
                label_visibility="collapsed"
            )
        
        with col3:
            st.markdown("""
            <div style='margin-bottom: 0.5rem;'>
                <label style='color: #1a1a2e; font-weight: 600;'>Amount Received (₹)</label>
            </div>
            """, unsafe_allow_html=True)
            amount_paid = st.number_input(
                "",
                min_value=0.0,
                max_value=CONFIG.MAX_AMOUNT,
                value=0.0,
                step=100.0,
                format="%.2f",
                label_visibility="collapsed"
            )
            
            st.markdown("""
            <div style='margin-bottom: 0.5rem; margin-top: 1rem;'>
                <label style='color: #1a1a2e; font-weight: 600;'>Notes (Optional)</label>
            </div>
            """, unsafe_allow_html=True)
            notes = st.text_area(
                "",
                placeholder="Any additional notes",
                max_chars=CONFIG.MAX_NOTES_LENGTH,
                label_visibility="collapsed"
            )
        
        st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("📝 Record Selling Transaction", use_container_width=True)
        
        if submitted:
            if seller_name and item_name and quantity_quintal > 0 and price_per_unit > 0:
                try:
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
                        st.markdown(f"""
                        <div style='background: linear-gradient(135deg, #48bb7815 0%, #38a16915 100%); 
                                   padding: 1.5rem; border-radius: 12px; border-left: 4px solid #48bb78; margin-bottom: 1.5rem;'>
                            <div style='display: flex; align-items: center;'>
                                <div style='font-size: 2rem; margin-right: 1rem;'>✅</div>
                                <div>
                                    <h4 style='color: #065f46; margin: 0 0 0.25rem 0;'>
                                        Selling Transaction Recorded Successfully!
                                    </h4>
                                    <p style='color: #065f46; margin: 0;'>
                                        Transaction ID: {transaction_id}
                                    </p>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Show breakdown
                        with st.expander("💰 Revenue Breakdown", expanded=True):
                            st.markdown("""
                            <div style='background: white; padding: 1.5rem; border-radius: 12px; 
                                       box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
                            """, unsafe_allow_html=True)
                            col_s1, col_s2 = st.columns(2)
                            with col_s1:
                                st.markdown(f"""
                                <div style='margin-bottom: 0.75rem;'>
                                    <span style='color: #4a5568;'>Base Price:</span>
                                    <span style='color: #1a1a2e; font-weight: 700; float: right;'>{format_currency(base_amount)}</span>
                                </div>
                                <div style='margin-bottom: 0.75rem;'>
                                    <span style='color: #4a5568;'>Cash Discount ({CONFIG.CASH_DISCOUNT_RATE*100}%):</span>
                                    <span style='color: #e53e3e; font-weight: 700; float: right;'>-{format_currency(cash_discount)}</span>
                                </div>
                                """, unsafe_allow_html=True)
                            with col_s2:
                                st.markdown(f"""
                                <div style='margin-bottom: 0.75rem;'>
                                    <span style='color: #4a5568;'>Labour Charge (₹{CONFIG.LABOUR_CHARGE_PER_QUINTAL}/Quintal):</span>
                                    <span style='color: #e53e3e; font-weight: 700; float: right;'>-{format_currency(labour_charge)}</span>
                                </div>
                                <div style='margin-bottom: 0.75rem;'>
                                    <span style='color: #4a5568;'>Transport Charge (₹{CONFIG.TRANSPORT_CHARGE_PER_QUINTAL}/Quintal):</span>
                                    <span style='color: #e53e3e; font-weight: 700; float: right;'>-{format_currency(transport_charge)}</span>
                                </div>
                                """, unsafe_allow_html=True)
                            st.markdown(f"""
                            <div style='border-top: 2px solid #48bb78; padding-top: 1rem; margin-top: 1rem;'>
                                <span style='color: #1a1a2e; font-weight: 700; font-size: 1.2rem;'>Total Revenue:</span>
                                <span style='color: #48bb78; font-weight: 700; font-size: 1.2rem; float: right;'>{format_currency(total_amount)}</span>
                            </div>
                            </div>
                            """, unsafe_allow_html=True)
                except ValueError as e:
                    display_error_message(f"Calculation error: {e}")
                except Exception as e:
                    display_error_message(f"An unexpected error occurred: {e}")
            else:
                st.markdown("""
                <div style='background: linear-gradient(135deg, #f5656515 0%, #e53e3e15 100%); 
                           padding: 1.5rem; border-radius: 12px; border-left: 4px solid #f56565;'>
                    <div style='display: flex; align-items: center;'>
                        <div style='font-size: 2rem; margin-right: 1rem;'>❌</div>
                        <div>
                            <h4 style='color: #c53030; margin: 0 0 0.25rem 0;'>
                                Validation Error
                            </h4>
                            <p style='color: #c53030; margin: 0;'>
                                Please fill all required fields with valid values
                            </p>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
