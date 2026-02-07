"""
View Transactions page for the Buying & Selling Dashboard Application.
"""

import time
from datetime import datetime
import streamlit as st

from database import get_all_transactions, delete_transaction
from utils import format_currency, display_error_message
from logger_setup import logger


def render_view_transactions() -> None:
    """Render the view transactions page."""
    st.markdown("""
    <div style='background: linear-gradient(135deg, #4299e1 0%, #3182ce 100%); 
                padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem;'>
        <h2 style='color: white; margin: 0; font-size: 1.8rem;'>
            📋 All Transactions
        </h2>
        <p style='color: rgba(255,255,255,0.9); margin: 0.5rem 0 0 0;'>
            View, filter, and manage all your transactions
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    try:
        df = get_all_transactions()
        
        if not df.empty:
            # Filter options
            st.markdown("""
            <div style='background: white; padding: 1.5rem; border-radius: 12px; 
                       box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 1.5rem;'>
                <h3 style='color: #1a1a2e; margin-top: 0;'>🔍 Filter Transactions</h3>
            </div>
            """, unsafe_allow_html=True)
            
            col_filter1, col_filter2, col_filter3 = st.columns(3)
            
            with col_filter1:
                st.markdown("""
                <div style='margin-bottom: 0.5rem;'>
                    <label style='color: #1a1a2e; font-weight: 600;'>Filter by Type</label>
                </div>
                """, unsafe_allow_html=True)
                transaction_type_filter = st.selectbox(
                    "",
                    ["All", "BUY", "SELL"],
                    index=0,
                    label_visibility="collapsed"
                )
            
            with col_filter2:
                st.markdown("""
                <div style='margin-bottom: 0.5rem;'>
                    <label style='color: #1a1a2e; font-weight: 600;'>Filter by Status</label>
                </div>
                """, unsafe_allow_html=True)
                status_filter = st.selectbox(
                    "",
                    ["All", "PENDING", "SOLD", "COMPLETED"],
                    index=0,
                    label_visibility="collapsed"
                )
            
            with col_filter3:
                st.markdown("""
                <div style='margin-bottom: 0.5rem;'>
                    <label style='color: #1a1a2e; font-weight: 600;'>Search Item Name</label>
                </div>
                """, unsafe_allow_html=True)
                search_item = st.text_input(
                    "",
                    placeholder="Type to search...",
                    label_visibility="collapsed"
                )
            
            # Apply filters
            filtered_df = df.copy()
            
            if transaction_type_filter != "All":
                filtered_df = filtered_df[filtered_df['transaction_type'] == transaction_type_filter]
            
            if status_filter != "All":
                filtered_df = filtered_df[filtered_df['status'] == status_filter]
            
            if search_item:
                filtered_df = filtered_df[
                    filtered_df['item_name'].str.contains(search_item, case=False, na=False)
                ]
            
            # Display table
            display_columns = ['id', 'transaction_type', 'item_name', 'quantity_kg', 
                             'price_per_unit', 'total_amount', 'transaction_date', 'status']
            available_columns = [col for col in display_columns if col in filtered_df.columns]
            
            if not filtered_df.empty:
                st.markdown(f"""
                <div style='background: white; padding: 1.5rem; border-radius: 12px; 
                           box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 1.5rem;'>
                    <h3 style='color: #1a1a2e; margin-top: 0;'>📊 Transaction Results ({len(filtered_df)} records)</h3>
                </div>
                """, unsafe_allow_html=True)
                
                st.dataframe(
                    filtered_df[available_columns].rename(columns={'quantity_kg': 'Quantity (Quintal)'}),
                    use_container_width=True,
                    height=400
                )
                
                # Delete transaction section
                st.markdown("<hr style='margin: 2rem 0;'>", unsafe_allow_html=True)
                st.markdown("""
                <div style='background: linear-gradient(135deg, #f5656515 0%, #e53e3e15 100%); 
                           padding: 1.5rem; border-radius: 12px; border-left: 4px solid #f56565; margin-bottom: 1.5rem;'>
                    <h3 style='color: #1a1a2e; margin-top: 0;'>🗑️ Delete Transaction</h3>
                    <p style='color: #4a5568; margin: 0;'>
                        Select a transaction to permanently delete it from the database
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                col_del1, col_del2 = st.columns([3, 1])
                
                with col_del1:
                    trans_list = filtered_df.reset_index(drop=True)
                    selected_idx = st.selectbox(
                        "Select transaction to delete",
                        options=range(len(trans_list)),
                        format_func=lambda x: f"ID {int(trans_list.iloc[x]['id'])} - {trans_list.iloc[x]['item_name']} ({trans_list.iloc[x]['transaction_type']})"
                    )
                    trans_id_to_delete = int(trans_list.iloc[selected_idx]['id'])
                
                with col_del2:
                    st.write("")
                    st.write("")
                    if st.button("🗑️ Delete", use_container_width=True, key="open_delete_btn"):
                        st.session_state.show_delete_confirmation = True
                        st.session_state.transaction_to_delete = trans_id_to_delete
                
                # Show confirmation if needed
                if (st.session_state.get('show_delete_confirmation', False) and 
                    st.session_state.get('transaction_to_delete') == trans_id_to_delete):
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #ed893615 0%, #dd6b2015 100%); 
                               padding: 1.5rem; border-radius: 12px; border-left: 4px solid #ed8936; margin-bottom: 1.5rem;'>
                        <div style='display: flex; align-items: center;'>
                            <div style='font-size: 2rem; margin-right: 1rem;'>⚠️</div>
                            <div>
                                <h4 style='color: #c05621; margin: 0 0 0.25rem 0;'>
                                    Confirm Deletion
                                </h4>
                                <p style='color: #c05621; margin: 0;'>
                                    Are you sure you want to delete Transaction ID {trans_id_to_delete}? This action cannot be undone!
                                </p>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    col_confirm1, col_confirm2, col_confirm3 = st.columns(3)
                    
                    with col_confirm1:
                        if st.button("✅ Yes, Delete", use_container_width=True, key="confirm_delete_yes"):
                            if delete_transaction(trans_id_to_delete):
                                st.session_state.show_delete_confirmation = False
                                st.session_state.transaction_to_delete = None
                                st.markdown(f"""
                                <div style='background: linear-gradient(135deg, #48bb7815 0%, #38a16915 100%); 
                                           padding: 1.5rem; border-radius: 12px; border-left: 4px solid #48bb78;'>
                                    <div style='display: flex; align-items: center;'>
                                        <div style='font-size: 2rem; margin-right: 1rem;'>✅</div>
                                        <div>
                                            <h4 style='color: #065f46; margin: 0 0 0.25rem 0;'>
                                                Transaction Deleted Successfully!
                                            </h4>
                                            <p style='color: #065f46; margin: 0;'>
                                                Transaction ID {trans_id_to_delete} has been permanently removed
                                            </p>
                                        </div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                                st.balloons()
                                time.sleep(1)
                                st.rerun()
                    
                    with col_confirm2:
                        if st.button("❌ Cancel", use_container_width=True, key="confirm_delete_no"):
                            st.session_state.show_delete_confirmation = False
                            st.session_state.transaction_to_delete = None
                            st.rerun()
                    
                    with col_confirm3:
                        st.write("")
            else:
                st.markdown("""
                <div style='background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); 
                           padding: 3rem; border-radius: 12px; text-align: center; border-left: 4px solid #667eea;'>
                    <div style='font-size: 4rem; margin-bottom: 1rem;'>🔍</div>
                    <h3 style='color: #1a1a2e; margin: 0 0 0.5rem 0;'>No Transactions Found</h3>
                    <p style='color: #4a5568; margin: 0;'>
                        Try adjusting your filters or search terms
                    </p>
                </div>
                """, unsafe_allow_html=True)
            
            # Summary of filtered transactions
            if not filtered_df.empty:
                st.markdown("<hr style='margin: 2rem 0;'>", unsafe_allow_html=True)
                st.markdown("""
                <div style='background: white; padding: 1.5rem; border-radius: 12px; 
                           box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 1.5rem;'>
                    <h3 style='color: #1a1a2e; margin-top: 0;'>📈 Summary</h3>
                </div>
                """, unsafe_allow_html=True)
                
                col_sum1, col_sum2, col_sum3 = st.columns(3)
                
                with col_sum1:
                    buy_total = filtered_df[filtered_df['transaction_type'] == 'BUY']['total_amount'].sum()
                    st.markdown(f"""
                    <div style='background: white; padding: 1.5rem; border-radius: 12px; 
                               box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center;'>
                        <div style='font-size: 2rem; font-weight: 700; color: #667eea; margin-bottom: 0.5rem;'>
                            {format_currency(buy_total)}
                        </div>
                        <div style='color: #4a5568; font-weight: 600; font-size: 0.9rem;'>
                            💰 Buy Total
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_sum2:
                    sell_total = filtered_df[filtered_df['transaction_type'] == 'SELL']['total_amount'].sum()
                    st.markdown(f"""
                    <div style='background: white; padding: 1.5rem; border-radius: 12px; 
                               box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center;'>
                        <div style='font-size: 2rem; font-weight: 700; color: #48bb78; margin-bottom: 0.5rem;'>
                            {format_currency(sell_total)}
                        </div>
                        <div style='color: #4a5568; font-weight: 600; font-size: 0.9rem;'>
                            💵 Sell Total
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_sum3:
                    net = sell_total - buy_total
                    net_color = "#48bb78" if net >= 0 else "#f56565"
                    st.markdown(f"""
                    <div style='background: white; padding: 1.5rem; border-radius: 12px; 
                               box-shadow: 0 4px 6px rgba(0,0,0,0.1); text-align: center;'>
                        <div style='font-size: 2rem; font-weight: 700; color: {net_color}; margin-bottom: 0.5rem;'>
                            {format_currency(net)}
                        </div>
                        <div style='color: #4a5568; font-weight: 600; font-size: 0.9rem;'>
                            📊 Net P/L
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Export option
                st.markdown("<hr style='margin: 2rem 0;'>", unsafe_allow_html=True)
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download Transactions as CSV",
                    data=csv,
                    file_name=f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        else:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%); 
                       padding: 3rem; border-radius: 12px; text-align: center; border-left: 4px solid #667eea;'>
                <div style='font-size: 4rem; margin-bottom: 1rem;'>📝</div>
                <h3 style='color: #1a1a2e; margin: 0 0 0.5rem 0;'>No Transactions Yet</h3>
                <p style='color: #4a5568; margin: 0;'>
                    Start by recording your first transaction to see them here
                </p>
            </div>
            """, unsafe_allow_html=True)
            
    except Exception as e:
        logger.error(f"Error rendering view transactions: {e}")
        display_error_message(f"Error loading transactions: {e}")
