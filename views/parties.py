"""
Parties Management view for managing buyers and sellers.
"""

import streamlit as st
import pandas as pd
from database import add_party, get_all_parties, delete_party
from utils import format_currency


def render_parties():
    """Render the parties management page."""
    st.header("👥 Manage Contacts")
    st.markdown("Add and manage buyers/sellers. People with the same name will be tracked separately.")
    
    # Tabs for Add and View
    tab1, tab2 = st.tabs(["➕ Add Contact", "📋 View All"])
    
    # ----- Add Contact Tab -----
    with tab1:
        with st.form("add_party_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Name *", placeholder="e.g., Amit Kumar")
                phone = st.text_input("Phone", placeholder="e.g., 9876543210")
            
            with col2:
                party_type = st.selectbox("Type", ["BOTH", "BUYER", "SELLER"])
                address = st.text_input("Address/Village", placeholder="e.g., Rampur")
            
            notes = st.text_area("Notes", placeholder="Any additional info...")
            
            submitted = st.form_submit_button("➕ Add Contact", use_container_width=True)
            
            if submitted:
                if not name.strip():
                    st.error("❌ Name is required!")
                else:
                    party_id = add_party(
                        name=name.strip(),
                        phone=phone.strip(),
                        address=address.strip(),
                        party_type=party_type,
                        notes=notes.strip()
                    )
                    if party_id:
                        st.success(f"✅ Contact '{name}' added successfully! (ID: {party_id})")
                        st.rerun()
                    else:
                        st.error("❌ Failed to add contact")
    
    # ----- View All Tab -----
    with tab2:
        # Filter by type
        filter_type = st.selectbox("Filter by Type", ["ALL", "BUYER", "SELLER", "BOTH"])
        
        parties_df = get_all_parties(filter_type if filter_type != "ALL" else None)
        
        if parties_df.empty:
            st.info("No contacts found. Add some contacts first!")
        else:
            st.markdown(f"**Total Contacts:** {len(parties_df)}")
            
            # Display parties in a nice table
            display_df = parties_df[['id', 'name', 'phone', 'address', 'party_type', 'notes']].copy()
            display_df.columns = ['ID', 'Name', 'Phone', 'Address', 'Type', 'Notes']
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            # Delete option
            st.markdown("---")
            st.subheader("🗑️ Delete Contact")
            
            party_options = [f"{row['id']} - {row['name']} ({row.get('phone', 'No phone')})" 
                           for _, row in parties_df.iterrows()]
            
            if party_options:
                selected = st.selectbox("Select contact to delete", party_options)
                party_id_to_delete = int(selected.split(" - ")[0])
                
                if st.button("🗑️ Delete Selected Contact", type="secondary"):
                    if delete_party(party_id_to_delete):
                        st.success("✅ Contact deleted!")
                        st.rerun()
                    else:
                        st.error("❌ Failed to delete. Contact may have linked transactions.")
